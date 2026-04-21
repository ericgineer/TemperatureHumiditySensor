document.addEventListener('DOMContentLoaded', () => {
    const tempVal = document.getElementById('temp-val');
    const humVal = document.getElementById('hum-val');
    const indicator = document.getElementById('connection-status');
    const statusText = document.getElementById('status-text');

    // Chart Setup
    const ctx = document.getElementById('envChart').getContext('2d');
    
    // Gradient for Temperature
    const gradientTemp = ctx.createLinearGradient(0, 0, 0, 400);
    gradientTemp.addColorStop(0, 'rgba(239, 68, 68, 0.5)');
    gradientTemp.addColorStop(1, 'rgba(239, 68, 68, 0.0)');

    // Gradient for Humidity
    const gradientHum = ctx.createLinearGradient(0, 0, 0, 400);
    gradientHum.addColorStop(0, 'rgba(59, 130, 246, 0.5)');
    gradientHum.addColorStop(1, 'rgba(59, 130, 246, 0.0)');

    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [], // Timestamps
            datasets: [
                {
                    label: 'Temperature (°F)',
                    borderColor: '#ef4444',
                    backgroundColor: gradientTemp,
                    borderWidth: 2,
                    pointRadius: 0,
                    pointHoverRadius: 6,
                    fill: true,
                    tension: 0.4,
                    data: [],
                    yAxisID: 'y'
                },
                {
                    label: 'Humidity (%)',
                    borderColor: '#3b82f6',
                    backgroundColor: gradientHum,
                    borderWidth: 2,
                    pointRadius: 0,
                    pointHoverRadius: 6,
                    fill: true,
                    tension: 0.4,
                    data: [],
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                legend: {
                    labels: { color: '#94a3b8', font: { family: 'Outfit', size: 14 } }
                },
                tooltip: {
                    backgroundColor: 'rgba(15, 23, 42, 0.9)',
                    titleColor: '#f8fafc',
                    bodyColor: '#f8fafc',
                    bodyFont: { family: 'Outfit' },
                    titleFont: { family: 'Outfit' },
                    borderColor: 'rgba(255,255,255,0.1)',
                    borderWidth: 1
                }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)', drawBorder: false },
                    ticks: { color: '#94a3b8', maxTicksLimit: 10, font: {family: 'Outfit'} }
                },
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    min: 0,
                    max: 100,
                    grid: { color: 'rgba(255, 255, 255, 0.05)', drawBorder: false },
                    ticks: { color: '#ef4444', font: {family: 'Outfit'} },
                    title: { display: true, text: 'Temperature (°F)', color: '#ef4444' }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    min: 0,
                    max: 100,
                    grid: { drawOnChartArea: false }, // Only draw grid lines for one axis
                    ticks: { color: '#3b82f6', font: {family: 'Outfit'} },
                    title: { display: true, text: 'Humidity (%)', color: '#3b82f6' }
                }
            }
        }
    });

    // Fetch History and start WebSocket Connection
    async function init() {
        try {
            const res = await fetch('/history');
            const data = await res.json();
            data.history.forEach(item => {
                const temp = parseFloat(item.temp);
                const hum = parseFloat(item.humidity);
                const timeStr = new Date(item.timestamp).toLocaleTimeString([], { hour12: false });
                
                chart.data.labels.push(timeStr);
                chart.data.datasets[0].data.push(temp);
                chart.data.datasets[1].data.push(hum);
                
                if (!isNaN(temp)) tempVal.textContent = temp.toFixed(1);
                if (!isNaN(hum)) humVal.textContent = hum.toFixed(1);
            });
            chart.update('none');
        } catch(e) {
            console.error("Failed to load history", e);
        }

        connectWebSocket();
    }

    function connectWebSocket() {
        // Determine WS protocol based on HTTP protocol
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        // Use window.location.host to allow network access globally
        const wsUrl = `${protocol}//${window.location.host}/ws`;
        const ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            indicator.className = 'indicator connected';
            statusText.textContent = 'Live';
        };

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                
                // Update text values
                const temp = parseFloat(data.temp);
                const hum = parseFloat(data.humidity);
                
                if (!isNaN(temp)) tempVal.textContent = temp.toFixed(1);
                if (!isNaN(hum)) humVal.textContent = hum.toFixed(1);

                // Update chart
                const timeStr = new Date(data.timestamp).toLocaleTimeString([], { hour12: false });
                
                chart.data.labels.push(timeStr);
                chart.data.datasets[0].data.push(temp);
                chart.data.datasets[1].data.push(hum);

                // Keep all historical limit removed

                chart.update('none'); // Update without full animation for a continuous flow

            } catch(e) {
                console.error("Error parsing message", e);
            }
        };

        ws.onclose = () => {
            indicator.className = 'indicator disconnected';
            statusText.textContent = 'Disconnected. Reconnecting...';
            // Auto reconnect
            setTimeout(connectWebSocket, 3000);
        };
        
        ws.onerror = (err) => {
            console.error("WebSocket error", err);
            ws.close();
        };
    }

    init();
});
