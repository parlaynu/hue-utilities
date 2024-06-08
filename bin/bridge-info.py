#!/usr/bin/env python3
import argparse
import hlib


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--bridge', help='ip address of the bridge', type=str, default=None)
    args = parser.parse_args()

    cfg = hlib.load_config()
    if args.bridge is not None:
        cfg['bridge'] = args.bridge

    bridge = hlib.find_bridge(cfg['bridge'])
    if bridge is None:
        print("Error: failed to locate a bridge")
        return

    print("Bridge:")
    print(f" Hostname: {bridge.hostname}")
    print(f"       ID: {bridge.id}")
    print(f"    Model: {bridge.model_id}")
    print(f"Addresses:", end= "")
    for address in bridge.addresses:
        print(f" {address}", end="")
    print("")
    print(f"     Port: {bridge.port}")


if __name__ == "__main__":
    main()