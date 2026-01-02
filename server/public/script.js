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
// Initial chart load
updateChart();
updateSessionInfo();
// Refresh chart every 5 minutes
setInterval(updateChart, 300000);

function updateChart() {
    fetch('/api/history')
        .then(response => response.json())
        .then(data => {
            if (!data || data.length === 0) return;

            const timestamps = data.map(d => d.Timestamp);
            const gravities = data.map(d => parseFloat(d.Gravity));
            const temps = data.map(d => parseFloat(d.Temperature));

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
                document.getElementById('session-date').textContent = data.start_date || '--';
            }
        })
        .catch(err => console.error('Error loading session info:', err));
}
