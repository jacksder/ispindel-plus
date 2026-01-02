import urllib.request
import json

try:
    print("Fetching history...")
    with urllib.request.urlopen("http://localhost:3000/api/history") as r:
        data = json.loads(r.read().decode('utf-8'))
        
    print(f"Data points returned: {len(data)}")
    if len(data) > 0:
        print("Sample point:", data[0])
        print("\nSUCCESS: History endpoint works.")
    else:
        print("\nWARNING: History endpoint works but returned no data (CSV might be empty).")

except Exception as e:
    print(f"\nERROR: {e}")
