#!/usr/bin/env python3
import argparse
from pprint import pprint
import json

import hlib


def check_temp(cl, device_id):
    
    device_name = None
    
    # first, try and find the device as a device
    url = f"/clip/v2/resource/device/{device_id}"
    
    resp = cl.get(url)
    if resp.status_code == 200:
        data = resp.json()
        device = data['data'][0]

        # see if the device has a temperature device
        temp_id = None
        services = device.get('services', [])
        for service in services:
            if service['rtype'] == 'temperature':
                temp_id = service['rid']
                break

        if temp_id is None:
            print("Device has no temperature sensor")
            for service in services:
                print(f"- {service['rtype']}")
            return None, None

        device_name = device['metadata']['name']
        device_id = temp_id

    # now get the temperature
    url = f"/clip/v2/resource/temperature/{device_id}"

    resp = cl.get(url)
    if resp.status_code != 200:
        print(f"Request failed with {resp.status_code} {resp.reason}")
        return None

    data = resp.json()
    device = data['data'][0]

    temp = device['temperature']['temperature']
    return float(temp), device_name


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--bridge', help='ip address of the bridge', type=str, default=None)
    parser.add_argument('device_id', help='id of the device to query', type=str, nargs='+')
    args = parser.parse_args()
    
    cfg = hlib.load_config()
    if args.bridge is not None:
        cfg['bridge'] = args.bridge

    bridge = hlib.find_bridge(cfg['bridge'])
    if bridge is None:
        print("Error: failed to locate a bridge")
        return
    
    cl = hlib.new_client(bridge, cfg['user_name'])
    
    print("Temperatures:")
    for idx, device_id in enumerate(args.device_id):
        temp, device_name = check_temp(cl, device_id)
        if temp is None:
            continue
        
        if device_name is None:
            print(f"{idx:02d} {temp}")
        else:
            print(f"{idx:02d} {temp} at {device_name}")


if __name__ == "__main__":
    main()

