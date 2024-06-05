#!/usr/bin/env python3
import argparse
import hlib


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--addr', help='ip address of the bridge', type=str, default=None)
    args = parser.parse_args()

    bridge = hlib.find_bridge(args.addr)
    if bridge is None:
        print("Error: failed to locate a bridge")
        return
    
    cfg = hlib.load_config()
    cl = hlib.new_client(bridge, cfg['user_name'])
    
    resp = cl.get("/clip/v2/resource/device")
    if resp.status_code != 200:
        print(f"Request failed with {resp.status_code} {resp.reason}")
        return
    
    data = resp.json()
    devices = data['data']
    
    for idx, device in enumerate(devices):
        if idx > 0:
            print("")
        print(f"Product: {device['product_data']['product_name']}")
        print(f"  Model: {device['product_data']['model_id']}")
        print(f"   Name: {device['metadata']['name']}")
        print(f"     ID: {device['id']}")
        
        print("Services:")
        for service in device['services']:
            print(f"  - {service['rtype']}")
            print(f"    {service['rid']}")

if __name__ == "__main__":
    main()

