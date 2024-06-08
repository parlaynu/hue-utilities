#!/usr/bin/env python3
import argparse
import sys, syslog
import json
import time
from datetime import datetime
from pprint import pprint

import requests

import hlib


def get_devices(cl):
    resp = cl.get("/clip/v2/resource/device")
    if resp.status_code != 200:
        print(f"Request failed with {resp.status_code} {resp.reason}")
        return
    
    data = resp.json()
    raw_devices = data['data']
        
    devices = {}
    
    for d in raw_devices:
        top_id = d['id']
        
        device = {
            'id': top_id,
            'type': d['type'],
            'product': d['product_data']['product_name'],
            'archtype': d['metadata']['archetype'],
            'name': d['metadata']['name'],
        }
        devices[top_id] = device
        
    return devices


def listener(client, types):
    
    types = set(types)

    # get the devices
    devices = get_devices(client)
    
    # start listening for events
    headers = {
        "Accept": "text/event-stream"
    }
    
    prefix = "data: "
    resp = client.get("/eventstream/clip/v2", extra_headers=headers, stream=True, timeout=300)
    for line in resp.iter_lines():
        line = line.decode('utf-8')
        if len(line) == 0:
            continue
            
        if not line.startswith(prefix):
            continue
            
        line = line[len(prefix):]
        events = json.loads(line)
        
        for event in events:
            datas = event['data']
            for data in datas:
                owner = data.get("owner", None)
                if owner is None:
                    continue
                
                # only report events related to devices
                if owner['rtype'] != 'device':
                    continue

                # filter types
                dtype = data['type']
                if len(types) > 0 and dtype not in types:
                    continue
                
                data['event_stamp'] = event['creationtime']
                data['event_id'] = event['id']
                data['event_type'] = event['type']
                
                owner_id = owner['rid']
                if owner := devices.get(owner_id, None):
                    data['owner'] = owner
                
                yield data
                

def syslogger(pipe):
    syslog.openlog(ident="hue-events", facility=syslog.LOG_LOCAL0)
    for item in pipe:
        jdata = json.dumps(item)
        syslog.syslog(syslog.LOG_INFO, jdata)
        yield item


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--bridge', help='ip address of the bridge', type=str, default=None)
    parser.add_argument("types", help="event types to filter for", type=str, nargs='*', default=None)
    args = parser.parse_args()
    
    cfg = hlib.load_config()
    if args.bridge is not None:
        cfg['bridge'] = args.bridge

    bridge = hlib.find_bridge(cfg['bridge'])
    if bridge is None:
        print("Error: failed to locate a bridge")
        return

    running = True
    while running:
        try:
            stamp = datetime.now().strftime("%Y-%m-%d,%H:%M:%S")
            print(f"{stamp},connecting", file=sys.stderr)
            
            # build the pipeline
            client = hlib.new_client(bridge, cfg['user_name'])
            pipe = listener(client, args.types)
            pipe = syslogger(pipe)
            
            # run the pipeline
            for item in pipe:
                pass
            
        except (requests.ConnectionError, requests.exceptions.ChunkedEncodingError):
            stamp = datetime.now().strftime("%Y-%m-%d,%H:%M:%S")
            print(f"{stamp},closing", file=sys.stderr)
            client.close()
            print(f"{stamp},resting", file=sys.stderr)
            time.sleep(60)
        except KeyboardInterrupt:
            running = False
        except Exception as e:
            running = False
            print(type(e), file=sys.stderr)
            print(e, file=sys.stderr)


if __name__ == "__main__":
    main()

