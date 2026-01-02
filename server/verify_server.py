import urllib.request
import json
import time

url = "http://localhost:3000/api/data"
data = {
    "name": "iSpindel_Test",
    "ID": "12345",
    "angle": 45.5,
    "temperature": 22.5,
    "temp_units": "C",
    "battery": 4.1,
    "gravity": 1.050,
    "interval": 900,
    "RSSI": -60
}

req = urllib.request.Request(url)
req.add_header('Content-Type', 'application/json')
jsondata = json.dumps(data).encode('utf-8')
req.add_header('Content-Length', len(jsondata))

try:
    print("Sending POST request...")
    response = urllib.request.urlopen(req, jsondata)
    print(f"Response code: {response.getcode()}")
    print(f"Response body: {response.read().decode('utf-8')}")

    time.sleep(1)

    print("\nFetching latest data...")
    with urllib.request.urlopen("http://localhost:3000/api/latest") as r:
        latest = json.loads(r.read().decode('utf-8'))
        print(f"Latest data: {latest}")
        
    if latest.get('name') == "iSpindel_Test":
        print("\nSUCCESS: Data verified.")
    else:
        print("\nFAILURE: Data mismatch.")

except Exception as e:
    print(f"\nERROR: {e}")
