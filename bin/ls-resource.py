#!/usr/bin/env python3
import argparse
from pprint import pprint

import hlib


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--bridge', help='ip address of the bridge', type=str, default=None)
    parser.add_argument('resource_type', help='type of the resource', type=str)
    parser.add_argument('resource_id', help='id of the resource', type=str)
    args = parser.parse_args()
    
    cfg = hlib.load_config()
    if args.bridge is not None:
        cfg['bridge'] = args.bridge

    bridge = hlib.find_bridge(cfg['bridge'])
    if bridge is None:
        print("Error: failed to locate a bridge")
        return
    
    cl = hlib.new_client(bridge, cfg['user_name'])
    
    url = f"/clip/v2/resource/{args.resource_type}/{args.resource_id}"
    
    resp = cl.get(url)
    if resp.status_code != 200:
        print(f"Request failed with {resp.status_code} {resp.reason}")
        return
    
    data = resp.json()
    resources = data['data']
    
    for resource in resources:
        pprint(resource)
    
if __name__ == "__main__":
    main()

