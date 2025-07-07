#!/usr/bin/env python
"""Debug script to test alarm attributes."""

import os
from yamcs.client import YamcsClient

# Get configuration from environment
url = os.getenv("YAMCS_URL", "http://localhost:8090")
instance = os.getenv("YAMCS_INSTANCE", "simulator")

print(f"Connecting to Yamcs at {url}")
print(f"Instance: {instance}")

# Create client
client = YamcsClient(url)

# Get processor
processor = client.get_processor(instance, "realtime")

print("\nListing alarms...")
alarms = list(processor.list_alarms())
print(f"Found {len(alarms)} active alarms")

if alarms:
    # Examine first alarm
    alarm = alarms[0]
    print(f"\nExamining alarm: {alarm.name}")
    print(f"Type: {type(alarm)}")
    
    # List all attributes
    print("\nAvailable attributes:")
    for attr in sorted(dir(alarm)):
        if not attr.startswith('_'):
            try:
                value = getattr(alarm, attr)
                if not callable(value):
                    print(f"  {attr}: {value}")
            except Exception as e:
                print(f"  {attr}: <error: {e}>")
else:
    print("No active alarms to examine")