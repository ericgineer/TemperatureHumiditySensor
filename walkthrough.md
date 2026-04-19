# Real-Time Sensor Dashboard Walkthrough

I have successfully built the real-time sensor dashboard. It features a modern, fast backend running your custom 1-Wire hardware readings and broadcasts the sensor data to a premium graphical user interface using WebSockets.

## Changes Made

### 1. High-Performance Dashboard Backend
**File:** [TemperatureHumiditySensor.py](file:///c:/Users/radio/git/TemperatureHumiditySensor/TemperatureHumiditySensor.py)
- Rewrote the main script to leverage the **FastAPI** web framework.
- **Hardware Integration:** The hardware reading logic you provided now runs continuously in a `threading.Thread` so it doesn't interrupt the HTTP web server. I've configured it to use the exact `addr` and `open()` logic you shared for your 1-Wire device (`fe-0021b1004824`). 
- **Graceful Fallbacks:** To ensure you can test the UI on your Windows machine even if the 1-Wire hardware isn't attached, the backend will safely fallback to sending simulated mocked temperature/humidity data.
- **WebSockets:** Created a robust asynchronous WebSocket manager that broadcasts out the `{"temp": ..., "humidity": ..., "timestamp": ...}` payload to all attached devices on your network every 1 second.
- **Dependency Tracking:** Automatically installed `fastapi`, `uvicorn`, and `websockets` locally.

### 2. Premium Real-Time Interface
All graphical files have been generated nicely inside a new `static/` directory.

- **[index.html](file:///c:/Users/radio/git/TemperatureHumiditySensor/static/index.html)**: Constructs the skeleton with large digital displays and a responsive canvas context for graphing.
- **[style.css](file:///c:/Users/radio/git/TemperatureHumiditySensor/static/style.css)**: Brings the experience to life using:
  - Custom Google Fonts (`Outfit`)
  - A gorgeous animated dark mode background.
  - "Glassmorphism" — an effect where UI cards look like slightly frosted glass overlaid on glowing orbs.
  - Interactive hover transitions.
- **[app.js](file:///c:/Users/radio/git/TemperatureHumiditySensor/static/app.js)**: Handles the connection pooling to the local backend's WebSocket endpoint. Uses `Chart.js` with smooth tensioned curved lines and transparent gradient fills to continuously slide incoming real-time data onto a stunning glowing graph.

## Validation and Next Steps

All Python dependencies are installed. You can now launch this on your network!

> [!TIP]
> **To start the dashboard:**
> Open your terminal, navigate to your project folder, and run:
> ```bash
> python TemperatureHumiditySensor.py
> ```
> 
> You will see Uvicorn start on `0.0.0.0:8000`.

### Viewing it Across Devices
Because we configured the host to `0.0.0.0`, you can view the dashboard from any device connected to your local WiFi:
- **On this computer**: Navigate your browser to `http://127.0.0.0:8000` or `http://localhost:8000`
- **On your phone/tablet**: Find out your computer's local IP address (e.g., `192.168.1.XX`), open Safari/Chrome on your phone, and visit `http://192.168.1.XX:8000`.

Watch the indicator dot—it should light up green ("Live"), and you'll immediately see the real-time data rolling across the graph!
