import urllib.request
import json
import time
import sys

# Tests persistence of data
print("Checking /api/latest for persisted data...")
try:
    with urllib.request.urlopen("http://localhost:3000/api/latest") as r:
        latest = json.loads(r.read().decode('utf-8'))
        print(f"Latest data: {latest}")
        
    if latest.get('name'):
        print("\nSUCCESS: Data persistence verified. Server returned data immediately.")
    else:
        print("\nFAILURE: No data returned. Persistence failed.")

except Exception as e:
    print(f"\nERROR: {e}")
