import http.server
import socketserver
import json
import csv
import os
import datetime
from datetime import datetime

PORT = 3000
DATA_DIR = '../data'
CSV_FILE = os.path.join(DATA_DIR, 'measurements.csv')

# Global variable to store the latest reading
latest_reading = {}

class ISpindelHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/latest':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(latest_reading).encode('utf-8'))
        else:
            # Default behavior serves static files
            super().do_GET()

    def do_POST(self):
        if self.path == '/api/data':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                print(f"Received data: {data}")
                
                global latest_reading
                timestamp = datetime.now().isoformat()
                
                # Update latest reading with timestamp
                latest_reading = data.copy()
                latest_reading['timestamp'] = timestamp
                
                # Extract fields with defaults
                name = data.get('name', 'Unknown')
                id_val = data.get('ID', '')
                angle = data.get('angle', 0)
                temperature = data.get('temperature', 0)
                temp_units = data.get('temp_units', 'C')
                battery = data.get('battery', 0)
                gravity = data.get('gravity', 0)
                interval = data.get('interval', 0)
                rssi = data.get('RSSI', 0)
                
                # Write to CSV
                # Ensure directory exists (relative to where we are running, which will be 'public')
                # But we are referencing via '../data' so it should be fine if we are in public
                
                row = [timestamp, name, id_val, angle, temperature, temp_units, battery, gravity, interval, rssi]
                
                with open(CSV_FILE, 'a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(row)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"message": "Data received"}')
                
            except Exception as e:
                print(f"Error processing POST: {e}")
                self.send_response(500)
                self.end_headers()
        else:
            self.send_error(404)

def ensure_setup():
    # We will run from the root directory but change to public for serving
    # So we need to set up data dir relative to public or absolute
    # Let's rely on the structure being:
    # /root
    #   /data
    #   /public
    #   server.py
    
    # Actually, the logic below assumes we start in root, create data, then chdir to public.
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', newline='') as f:
            f.write('Timestamp,Name,ID,Angle,Temperature,Temp_Units,Battery,Gravity,Interval,RSSI\n')

if __name__ == "__main__":
    # Ensure data directory exists before changing CWD
    # DATA_DIR is '../data' assuming we are inside 'public'.
    # But currently we are at root.
    
    # Let's correct the paths.
    # We start at /playground/final-sun/
    
    abs_root = os.getcwd()
    abs_data_dir = os.path.join(abs_root, 'data')
    abs_csv_file = os.path.join(abs_data_dir, 'measurements.csv')
    
    if not os.path.exists(abs_data_dir):
        os.makedirs(abs_data_dir)
        
    if not os.path.exists(abs_csv_file):
        with open(abs_csv_file, 'w', newline='') as f:
            f.write('Timestamp,Name,ID,Angle,Temperature,Temp_Units,Battery,Gravity,Interval,RSSI\n')

    # Update global constants to be absolute since we are changing CWD
    CSV_FILE = abs_csv_file
    
    # Change to public directory to serve files easily
    public_dir = os.path.join(abs_root, 'public')
    if not os.path.exists(public_dir):
        os.makedirs(public_dir)
    os.chdir(public_dir)
    
    # Allow address reuse to prevent "Address already in use" errors during quick restarts
    socketserver.TCPServer.allow_reuse_address = True
    
    with socketserver.TCPServer(("", PORT), ISpindelHandler) as httpd:
        print(f"Serving at port {PORT}")
        print(f"Serving files from {public_dir}")
        print(f"Writing data to {CSV_FILE}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
