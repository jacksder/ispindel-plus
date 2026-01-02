# iSpindel Configuration Guide

Follow these steps to configure your iSpindel device to send data to your new server.

## 1. Enter Configuration Mode
1. **Turn on** your iSpindel.
2. Press the **Reset** button (usually on the Wemos D1 Mini board) rapidly 3-4 times, or short the reset pins if you have a switch installed, until the blue LED starts flashing continuously.
   - *Note: On some versions, you just need to turn it on and it will enter config mode if it can't find a known network, or simply hold the reset button. Refer to your specific build instructions if unsure.*

## 2. Connect to iSpindel WiFi
1. On your phone or computer, look for a WiFi network named **iSpindel** (or standard-ap).
2. Connect to it.
   - If asked for a password, it is often empty or try `ispindel`.

## 3. Open Configuration Page
1. Open a web browser.
2. Navigate to: `http://192.168.4.1`
3. You should see the "Configuration" menu. Click **Configuration**.

## 4. Enter Settings
Fill in the following details:

### WiFi Settings
*   **SSID**: `<Your Home WiFi Name>`
*   **Password**: `<Your Home WiFi Password>`

### Server Settings for This Project
*   **Service Type**: `HTTP`
*   **Server Address**: `10.0.0.231`
*   **Server Port**: `3000`
*   **Server URL**: `/api/data`
*   **Update Interval**: `900` (Recommended: 15 minutes. Lower values drain battery faster.)
*   **Token**: (Leave empty)

### Advanced Settings
*   **Battery Conversion Factor**: This calibrates the battery voltage reading.
    *   **Default**: `191.8`
    *   **Calibration Formula**: `(displayed_voltage / measured_voltage) * current_factor = new_factor`
    *   *Tip: Unless your battery reading is wildly off, the default is usually fine.*

## 5. Save and Restart
1. Click **Save**.
2. The device will restart and attempt to connect to your WiFi.
3. Once connected, it will send the first data point to your server.

## 6. How to Update Settings (Polynomial, etc.)
Once the iSpindel is running, it does **not** host the configuration page. To change settings (like your gravity polynomial after calibration):
1. **Reset the Device**: Press the reset button 3-4 times rapidly (or short the reset pins) until the blue LED flashes constantly.
2. **Connect to AP**: Connect your phone/computer to the `iSpindel` WiFi network again.
3. **Go to 192.168.4.1**: The config page will be available there.
4. **Update & Save**: Enter your new polynomial and click Save.

## 6. Verify
Check your dashboard at [http://localhost:3000](http://localhost:3000) (or `http://10.0.0.231:3000` from another device on your network). You should see the new data appear.
