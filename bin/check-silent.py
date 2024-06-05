#!/usr/bin/env python3
import argparse
from pprint import pprint
import json

import hlib


def check_light(cl, light_id):
    url = f"/clip/v2/resource/light/{light_id}"
        
    resp = cl.get(url)
    if resp.status_code != 200:
        print(f"Request failed with {resp.status_code} {resp.reason}")
        return
    
    data = resp.json()
    light = data['data'][0]
    
    light_name = light['metadata']['name']

    poweron = light['powerup']['on']
    configured = poweron['mode'] == 'on' and poweron['on']['on'] == False
    
    return light_name, configured


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--addr', help='ip address of the bridge', type=str, default=None)
    parser.add_argument('light_id', help='id of light to check', type=str, nargs='+')
    args = parser.parse_args()
    
    bridge = hlib.find_bridge(args.addr)
    if bridge is None:
        print("Error: failed to locate a bridge")
        return
    
    cfg = hlib.load_config()
    cl = hlib.new_client(bridge, cfg['user_name'])
    
    green = {}
    red = {}
    for light_id in args.light_id:
        light_name, silent = check_light(cl, light_id)
        print(f'{light_id}: name: {light_name}, silent: {silent}')
        
        if silent:
            green[light_id] = light_name
        else:
            red[light_id] = light_name
    
    # check for pushover configuratin
    token = cfg.get('pushover_token', None)
    clients = cfg.get('pushover_clients', None)
    if token and clients:
        messages = []
        if len(red):
            messages.append("RED: incorrectly configured lights")
            for light_id, light_name in red.items():
                messages.append(f"  - {light_id} {light_name}")
        
        if len(green):
            messages.append("GREEN: correctly configured lights")
            for light_id, light_name in green.items():
                messages.append(f"  - {light_id} {light_name}")
        
        if len(red):
            title = "RED: incorrectly configured lights"
        else:
            title = "GREEN: correctly configured lights"
        
        message = "\n".join(messages)
        hlib.send_message(token, clients, message, title)


if __name__ == "__main__":
    main()

