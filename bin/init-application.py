#!/usr/bin/env python3
import argparse
import os
from pprint import pprint
import random, string
from importlib.resources import files

import hlib


def create_app(bridge, app_name, app_instance):
    cl = hlib.new_client(bridge)
    data = {
        "devicetype": f"{app_name}#{app_instance}",
        "generateclientkey": True
    }
    
    inp = input("Press hue link button. Type 'yes' to continue: ")
    if inp != "yes":
        return None, None, "operation cancelled by user"
    
    resp = cl.post("/api", json=data)
    if resp.status_code != 200:
        return None, None, f"{resp.status_code} {resp.reason}"
    
    data = resp.json()[0]
    
    if result := data.get("error", None):
        return None, None, result['description']

    if result := data.get("success", None):
        return result['username'], result['clientkey'], "success"
    
    return None, None, "an unknown error occurred"


def save_config(bridge, app_name, app_instance, user_name, client_key):
    config_file = files("hlib.resources").joinpath("config.yaml")

    with open(config_file, "w") as f:
        print(f"app_name: {app_name}", file=f)
        print(f"app_instance: {app_instance}", file=f)
        print(f"user_name: {user_name}", file=f)
        print(f"client_key: {client_key}", file=f)
    
    print(f"Configuration saved to {config_file}")

    
def main():
    # parse command line
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--name', help='name of your application', type=str, default=None)
    parser.add_argument('-i', '--instance', help='name the instance', type=str, default=None)
    args = parser.parse_args()
    
    if args.name is None:
        args.name = 'huetilities'
    if args.instance is None:
        args.instance = ''.join(random.choice(string.ascii_lowercase) for i in range(10))
    
    # get the bridge address
    bridge = hlib.find_bridge()
    if bridge is None:
        print("Error: failed to locate a bridge")
        return
    
    print(f"Found bridge {bridge.id} at address {bridge.addresses[0]}")
    
    # create the application
    user_name, client_key, msg = create_app(bridge, args.name, args.instance)
    if user_name is None:
        print(f"Failed to create app: {msg}")
        return
    
    # write out the config file
    save_config(bridge, args.name, args.instance, user_name, client_key)
    

if __name__ == "__main__":
    main()

