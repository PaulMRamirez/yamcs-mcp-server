#!/usr/bin/env python
"""Simple script to test what attributes are available on a Yamcs link."""

import os
from yamcs.client import YamcsClient

# Get configuration from environment
url = os.getenv("YAMCS_URL", "http://localhost:8090")
instance = os.getenv("YAMCS_INSTANCE", "simulator")

print(f"Connecting to Yamcs at {url}")
print(f"Instance: {instance}")

# Create client
client = YamcsClient(url)

# List links
print("\nListing links...")
links = list(client.list_links(instance))
if not links:
    print("No links found!")
    exit(1)

# Test with first link
link = links[0]
print(f"\nTesting link: {link.name}")
print(f"Type of link object: {type(link)}")

# Print all non-private attributes
print("\nAvailable attributes:")
for attr in sorted(dir(link)):
    if not attr.startswith('_'):
        try:
            value = getattr(link, attr)
            if not callable(value):
                print(f"  {attr}: {value}")
        except Exception as e:
            print(f"  {attr}: <error: {e}>")

# Get link via get_link method
print(f"\nGetting link via get_link...")
link_client = client.get_link(instance, link.name)
link_info = link_client.get_info()

print(f"\nType of link_info object: {type(link_info)}")
print("\nAvailable attributes on link_info:")
for attr in sorted(dir(link_info)):
    if not attr.startswith('_'):
        try:
            value = getattr(link_info, attr)
            if not callable(value):
                print(f"  {attr}: {value}")
        except Exception as e:
            print(f"  {attr}: <error: {e}>")