#!/usr/bin/env python3
import argparse
from pprint import pprint
import json

import hlib


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--negate', help='negate the silencing - always turn on', action='store_true')
    parser.add_argument('light_id', help='id of light to silence', type=str)
    args = parser.parse_args()
    
    bridge = hlib.find_bridge()
    if bridge is None:
        print("Error: failed to locate a bridge")
        return
    
    cfg = hlib.load_config()
    cl = hlib.new_client(bridge, cfg['user_name'])
    
    url = f"/clip/v2/resource/light/{args.light_id}"
    
    turn_on = True if args.negate else False
    payload = {
        'powerup': {
            'preset': 'custom',
            'on': { 'mode': 'on', 'on': {'on': turn_on }},
            'dimming': { 'mode': 'previous' },
            'color': { 'mode': 'previous' }
        }
    }
    # payload = json.dumps(payload)
        
    resp = cl.put(url, payload)
    if resp.status_code != 200:
        print(f"Request failed with {resp.status_code} {resp.reason}")
        print(resp.json())
        return
    
    data = resp.json()
    pprint(data)


if __name__ == "__main__":
    main()

