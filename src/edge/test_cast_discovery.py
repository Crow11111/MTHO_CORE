import asyncio
import pychromecast
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

def discover_casts():
    print("Scanning for Google Cast devices...")
    services, browser = pychromecast.discovery.discover_chromecasts()
    pychromecast.discovery.stop_discovery(browser)
    
    if not services:
        print("No Cast devices found.")
        return
    
    print(f"Found {len(services)} devices:")
    for service in services:
        print(f" - {service.friendly_name} ({service.model_name}) at {service.host}:{service.port}")

if __name__ == "__main__":
    discover_casts()
