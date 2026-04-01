# test_services.py
from detection.network import scan_all_devices

print("Scanning network...")
devices = scan_all_devices()

if devices:
    print(f"✅ Found {len(devices)} device(s):")
    for d in devices:
        print(f"   IP: {d['ip']} — MAC: {d['mac']}")
else:
    print("⚠️  No devices found.")