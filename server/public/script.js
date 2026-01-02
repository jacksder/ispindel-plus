function updateDisplay() {
    fetch('/api/latest')
        .then(response => response.json())
        .then(data => {
            if (Object.keys(data).length === 0) return;

            document.getElementById('gravity').textContent = data.gravity ? data.gravity.toFixed(3) : '--';
            document.getElementById('temperature').textContent = data.temperature ? data.temperature.toFixed(1) : '--';
            document.getElementById('temp-unit').textContent = data.temp_units || '°C';
            document.getElementById('battery').textContent = data.battery ? data.battery.toFixed(2) : '--';
            document.getElementById('angle').textContent = data.angle ? data.angle.toFixed(1) : '--';

            document.getElementById('device-name').textContent = data.name || '--';
            document.getElementById('rssi').textContent = data.RSSI || '--';

            if (data.timestamp) {
                const date = new Date(data.timestamp);
                document.getElementById('last-updated').textContent = 'Last Updated: ' + date.toLocaleTimeString();
            }
        })
        .catch(err => console.error('Error fetching data:', err));
}

// Update every 5 seconds
setInterval(updateDisplay, 5000);
updateDisplay();
