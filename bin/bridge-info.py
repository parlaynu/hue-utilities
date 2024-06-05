#!/usr/bin/env python3
import argparse
from hlib import find_bridge


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--addr', help='ip address of the bridge', type=str, default=None)
    args = parser.parse_args()

    bridge = find_bridge(args.addr)
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