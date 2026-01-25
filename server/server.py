import http.server
import socketserver
import json
import csv
import os
import datetime
from datetime import datetime
import math

PORT = 3000
DATA_DIR = '../data'
CSV_FILE = os.path.join(DATA_DIR, 'measurements.csv')
CALIBRATION_FILE = os.path.join(DATA_DIR, 'measurements_tilt_gravity.csv')
SESSION_FILE = os.path.join(DATA_DIR, 'session.json')

# Global variable to store the latest reading
latest_reading = {}

# Polynomial coefficients for gravity calculation (default to 0)
gravity_coeffs = []

def poly_fit(x, y, degree):
    """
    Fits a polynomial of given degree to data points (x, y) using Least Squares.
    Returns coefficients [beta_0, beta_1, ..., beta_degree] for y = b0 + b1*x + ...
    """
    n = len(x)
    if n <= degree:
        return [] # Not enough points

    # Create Vandermonde matrix X
    X = [[0.0] * (degree + 1) for _ in range(n)]
    for i in range(n):
        for j in range(degree + 1):
            X[i][j] = x[i] ** j

    # Transpose of X
    XT = [[X[i][j] for i in range(n)] for j in range(degree + 1)]

    # Compute XT * X (Normal matrix)
    XTX = [[0.0] * (degree + 1) for _ in range(degree + 1)]
    for i in range(degree + 1):
        for j in range(degree + 1):
            val = 0.0
            for k in range(n):
                val += XT[i][k] * X[k][j]
            XTX[i][j] = val

    # Compute XT * y
    XTy = [0.0] * (degree + 1)
    for i in range(degree + 1):
        val = 0.0
        for k in range(n):
            val += XT[i][k] * y[k]
        XTy[i] = val

    # Solve XTX * beta = XTy using Gaussian elimination
    # Augmented matrix [XTX | XTy]
    aug = [row[:] + [XTy[i]] for i, row in enumerate(XTX)]
    
    # Forward elimination
    for i in range(degree + 1):
        # Pivot
        pivot = aug[i][i]
        if abs(pivot) < 1e-10:
            return [] # Singular matrix
            
        for j in range(i + 1, degree + 2):
            aug[i][j] /= pivot
        aug[i][i] = 1.0

        for k in range(i + 1, degree + 1):
            factor = aug[k][i]
            for j in range(i, degree + 2):
                aug[k][j] -= factor * aug[i][j]

    # Back substitution
    coeffs = [0.0] * (degree + 1)
    for i in range(degree, -1, -1):
        val = aug[i][degree + 1]
        for j in range(i + 1, degree + 1):
            val -= aug[i][j] * coeffs[j]
        coeffs[i] = val
        
    return coeffs

def calculate_gravity(tilt):
    global gravity_coeffs
    if not gravity_coeffs:
        return 0.0
    
    gravity = 0.0
    for i, coeff in enumerate(gravity_coeffs):
        gravity += coeff * (tilt ** i)
    return gravity

def load_calibration():
    global gravity_coeffs
    try:
        points_x = []
        points_y = []
        
        if os.path.exists(CALIBRATION_FILE):
            with open(CALIBRATION_FILE, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        t = float(row['tilt'])
                        g = float(row['gravity'])
                        points_x.append(t)
                        points_y.append(g)
                    except ValueError:
                        continue
        
        if len(points_x) > 2:
            # Fit a quadratic (degree 2) or cubic (degree 3) if enough points
            degree = 2 if len(points_x) < 5 else 3
            gravity_coeffs = poly_fit(points_x, points_y, degree)
            print(f"Calibration loaded. Coeffs: {gravity_coeffs}")
        else:
            print("Not enough calibration points to fit function.")
            gravity_coeffs = []
            
    except Exception as e:
        print(f"Error loading calibration: {e}")

def load_latest_from_csv():
    global latest_reading
    try:
        if not os.path.exists(CSV_FILE):
            return

        with open(CSV_FILE, 'r') as f:
            reader = csv.reader(f)
            header = next(reader, None)  # Skip header
            if not header:
                return
            
            # Read all remaining lines
            rows = list(reader)
            if rows:
                last_row = rows[-1]
                try:
                    latest_reading = {
                        'timestamp': last_row[0],
                        'name': last_row[1],
                        'ID': last_row[2],
                        'angle': float(last_row[3]),
                        'temperature': float(last_row[4]),
                        'temp_units': last_row[5],
                        'battery': float(last_row[6]),
                        'gravity': float(last_row[7]),
                        'interval': int(last_row[8]),
                        'RSSI': int(last_row[9])
                    }
                    print(f"Loaded latest data from CSV: {latest_reading.get('name')} at {latest_reading.get('timestamp')}")
                except (IndexError, ValueError) as e:
                    print(f"Error parsing last CSV row: {e}")
            
    except Exception as e:
        print(f"Error loading CSV history: {e}")

class ISpindelHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/latest':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(latest_reading).encode('utf-8'))
        elif self.path == '/api/session':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            if os.path.exists(SESSION_FILE):
                with open(SESSION_FILE, 'r') as f:
                    self.wfile.write(f.read().encode('utf-8'))
            else:
                self.wfile.write(b'{}')
        elif self.path == '/api/history':
            try:
                history = []
                if os.path.exists(CSV_FILE):
                    with open(CSV_FILE, 'r') as f:
                        reader = csv.DictReader(f)
                        history = list(reader)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(history).encode('utf-8'))
            except Exception as e:
                print(f"Error serving history: {e}")
                self.send_error(500)
        elif self.path == '/api/calibration':
            try:
                data = {
                    'coeffs': gravity_coeffs,
                    'points': []
                }
                if os.path.exists(CALIBRATION_FILE):
                    with open(CALIBRATION_FILE, 'r') as f:
                        reader = csv.DictReader(f)
                        data['points'] = list(reader)
                        
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(data).encode('utf-8'))
            except Exception as e:
                print(f"Error serving calibration: {e}")
                self.send_error(500)
        else:
            # Default behavior serves static files
            super().do_GET()

    def do_POST(self):
        global latest_reading
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
                interval = data.get('interval', 0)
                rssi = data.get('RSSI', 0)
                
                # Calculate gravity from tilt if calibration exists
                calculated_gravity = data.get('gravity', 0)
                if gravity_coeffs:
                    calculated_gravity = calculate_gravity(angle)
                    latest_reading['gravity'] = calculated_gravity
                    print(f"Calculated gravity {calculated_gravity:.4f} from angle {angle}")
                
                gravity = calculated_gravity
                
                # Write to CSV
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
        elif self.path == '/api/new_session':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                session_name = data.get('sessionName', 'Unnamed')
                safe_name = "".join([c for c in session_name if c.isalpha() or c.isdigit() or c==' ' or c=='_']).rstrip()
                
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                archive_name = f"archive_{timestamp}_{safe_name}.csv"
                archive_path = os.path.join(DATA_DIR, archive_name)
                
                if os.path.exists(CSV_FILE):
                    os.rename(CSV_FILE, archive_path)
                    print(f"Archived current session to {archive_name}")
                
                session_info = {
                    "name": session_name,
                    "start_date": timestamp
                }
                with open(SESSION_FILE, 'w') as f:
                    json.dump(session_info, f)

                with open(CSV_FILE, 'w', newline='') as f:
                    f.write('Timestamp,Name,ID,Angle,Temperature,Temp_Units,Battery,Gravity,Interval,RSSI\n')
                
                latest_reading = {}
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"message": "New session started"}')
            except Exception as e:
                print(f"Error starting new session: {e}")
                self.send_error(500)
        else:
            self.send_error(404)

def ensure_setup():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', newline='') as f:
            f.write('Timestamp,Name,ID,Angle,Temperature,Temp_Units,Battery,Gravity,Interval,RSSI\n')

if __name__ == "__main__":
    abs_root = os.getcwd()
    abs_data_dir = os.path.join(abs_root, 'data')
    abs_csv_file = os.path.join(abs_data_dir, 'measurements.csv')
    
    if not os.path.exists(abs_data_dir):
        os.makedirs(abs_data_dir)
        
    if not os.path.exists(abs_csv_file):
        with open(abs_csv_file, 'w', newline='') as f:
            f.write('Timestamp,Name,ID,Angle,Temperature,Temp_Units,Battery,Gravity,Interval,RSSI\n')

    CSV_FILE = abs_csv_file
    CALIBRATION_FILE = os.path.join(abs_data_dir, 'measurements_tilt_gravity.csv')
    SESSION_FILE = os.path.join(abs_data_dir, 'session.json')
    
    # Load calibration data
    load_calibration()
    
    public_dir = os.path.join(abs_root, 'public')
    if not os.path.exists(public_dir):
        os.makedirs(public_dir)
    os.chdir(public_dir)
    
    socketserver.TCPServer.allow_reuse_address = True
    
    with socketserver.TCPServer(("", PORT), ISpindelHandler) as httpd:
        print(f"Serving at port {PORT}")
        print(f"Serving files from {public_dir}")
        print(f"Writing data to {CSV_FILE}")
        
        load_latest_from_csv()
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
