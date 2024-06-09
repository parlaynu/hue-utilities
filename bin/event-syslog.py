#!/usr/bin/env python3
import argparse
import sys
import time
from datetime import datetime

import requests

import hlib
from hops import listener, event_filter, syslogger


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
            pipe = listener(client)
            if len(args.types) > 0:
                pipe = event_filter(pipe, types=args.types)
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


if __name__ == "__main__":
    main()

