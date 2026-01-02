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
                document.getElementById('last-updated').textContent = 'Last Updated: ' + formatDateTime(data.timestamp);
            }
            updateTimeElapsed();
        })
        .catch(err => console.error('Error fetching data:', err));
}

// Initial data load
updateDisplay();
updateChart();
updateSessionInfo();

// Global start date
let sessionStartDate = null;

// Update elapsed time every second
// setInterval(updateTimeElapsed, 1000);

function formatDateTime(dateStr) {
    if (!dateStr) return '--';
    const date = new Date(dateStr);
    if (isNaN(date.getTime())) return '--';

    return date.toLocaleString(); // Uses local browser format (e.g. "1/2/2026, 12:30:00 PM")
}

function updateTimeElapsed() {
    if (!sessionStartDate) {
        document.getElementById('session-elapsed').textContent = '--';
        return;
    }

    const now = new Date();
    const diff = now - sessionStartDate;

    if (diff < 0) {
        document.getElementById('session-elapsed').textContent = '0d 0h 0m 0s';
        return;
    }

    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((diff % (1000 * 60)) / 1000);

    document.getElementById('session-elapsed').textContent = `${days}d ${hours}h ${minutes}m ${seconds}s`;
}

function updateChart() {
    fetch('/api/history')
        .then(response => response.json())
        .then(data => {
            if (!data || data.length === 0) return;

            const timestamps = data.map(d => d.Timestamp);
            const gravities = data.map(d => parseFloat(d.Gravity));
            const temps = data.map(d => parseFloat(d.Temperature));
            const batteries = data.map(d => parseFloat(d.Battery));
            const angles = data.map(d => parseFloat(d.Angle));

            // Chart 1: Gravity & Temperature
            const trace1 = {
                x: timestamps,
                y: gravities,
                name: 'Gravity',
                type: 'scatter',
                mode: 'lines+markers',
                marker: { symbol: 'diamond', size: 6 },
                line: { shape: 'spline', color: '#e67e22' }
            };

            const trace2 = {
                x: timestamps,
                y: temps,
                name: 'Temperature',
                yaxis: 'y2',
                type: 'scatter',
                mode: 'lines+markers',
                marker: { symbol: 'diamond', size: 6 },
                line: { shape: 'spline', color: '#e74c3c' }
            };

            const layout = {
                title: 'Fermentation History',
                paper_bgcolor: '#2d2d2d',
                plot_bgcolor: '#2d2d2d',
                font: { color: '#e0e0e0' },
                hovermode: 'x unified',
                xaxis: { title: 'Time', gridcolor: '#444' },
                yaxis: {
                    title: 'Specific Gravity',
                    gridcolor: '#444'
                },
                yaxis2: {
                    title: 'Temperature',
                    overlaying: 'y',
                    side: 'right',
                    gridcolor: '#444'
                },
                showlegend: true,
                legend: {
                    x: 0.5,
                    y: 1.1,
                    orientation: 'h',
                    xanchor: 'center'
                }
            };

            Plotly.newPlot('chart', [trace1, trace2], layout);

            // Chart 2: Battery & Angle
            const trace3 = {
                x: timestamps,
                y: batteries,
                name: 'Battery',
                type: 'scatter',
                mode: 'lines+markers',
                marker: { symbol: 'circle', size: 6 },
                line: { shape: 'spline', color: '#3498db' }
            };

            const trace4 = {
                x: timestamps,
                y: angles,
                name: 'Angle',
                yaxis: 'y2',
                type: 'scatter',
                mode: 'lines+markers',
                marker: { symbol: 'circle', size: 6 },
                line: { shape: 'spline', color: '#9b59b6' }
            };

            const layout2 = {
                title: 'Device Health',
                paper_bgcolor: '#2d2d2d',
                plot_bgcolor: '#2d2d2d',
                font: { color: '#e0e0e0' },
                hovermode: 'x unified',
                xaxis: { title: 'Time', gridcolor: '#444' },
                yaxis: {
                    title: 'Battery (V)',
                    gridcolor: '#444'
                },
                yaxis2: {
                    title: 'Tilt (Angle)',
                    overlaying: 'y',
                    side: 'right',
                    gridcolor: '#444'
                },
                showlegend: true,
                legend: {
                    x: 0.5,
                    y: 1.1,
                    orientation: 'h',
                    xanchor: 'center'
                }
            };

            Plotly.newPlot('battery-chart', [trace3, trace4], layout2);
        })
        .catch(err => console.error('Error loading chart:', err));
}

document.getElementById('new-session-btn').addEventListener('click', startNewSession);

function startNewSession() {
    const sessionName = prompt("Enter a name for this new brewing session:\n(This will archive the current data)");

    if (sessionName) {
        if (confirm(`Are you sure you want to start session "${sessionName}"?\nCurrent data will be archived.`)) {
            fetch('/api/new_session', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ sessionName: sessionName })
            })
                .then(response => {
                    if (response.ok) {
                        alert("New session started!");
                        location.reload();
                    } else {
                        alert("Error starting session.");
                    }
                })
                .catch(err => console.error('Error:', err));
        }
    }
}

function updateSessionInfo() {
    fetch('/api/session')
        .then(response => response.json())
        .then(data => {
            if (data.name) {
                document.getElementById('session-name').textContent = data.name;

                // Parse date - the server sends "YYYY-MM-DD_HH-MM-SS" or similar, 
                // but checking server.py it sends timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                // which is not standard ISO. We might need to handle that or standardise it.
                // Actually server.py line 147: timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                // Javascript Date constructor might struggle with underscores.

                let visibleDate = '--';
                if (data.start_date) {
                    // Replace underscores with specific format or just try parsing
                    // "2026-01-02_12-30-00" -> "2026-01-02T12:30:00"
                    const isoLike = data.start_date.replace('_', 'T').replace(/-/g, (match, offset) => {
                        // Only replace last two hyphens with colons for time
                        // Input: 2026-01-02T12-30-00
                        // We want: 2026-01-02T12:30:00
                        // Actually simple regex replacement is safer
                        return match;
                    });

                    // Simple manual parse for safer handling of custom format
                    const parts = data.start_date.match(/(\d{4})-(\d{2})-(\d{2})_(\d{2})-(\d{2})-(\d{2})/);
                    if (parts) {
                        sessionStartDate = new Date(parts[1], parts[2] - 1, parts[3], parts[4], parts[5], parts[6]);
                        visibleDate = formatDateTime(sessionStartDate);
                    } else {
                        // Fallback
                        sessionStartDate = new Date(data.start_date);
                        visibleDate = formatDateTime(data.start_date);
                    }
                }

                document.getElementById('session-date').textContent = visibleDate;
                updateTimeElapsed();
            }
        })
        .catch(err => console.error('Error loading session info:', err));
}
