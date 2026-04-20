import asyncio
import time
import json
import threading
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
import uvicorn
import os

app = FastAPI()

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def root():
    return FileResponse(os.path.join(static_dir, "index.html"))

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in list(self.active_connections):
            try:
                await connection.send_text(message)
            except Exception:
                self.disconnect(connection)

manager = ConnectionManager()
latest_data = {"temp": None, "humidity": None, "timestamp": None}
history_data = []

def sensor_reader_loop():
    global latest_data
    addr = 'fe-0021b1004824' # Must be changed for your device.
    W1PATH ='/sys/bus/w1/devices/' + addr
    
    # Attempt to open file path
    f = None
    try:
        f = open(W1PATH+'/rw', 'rb+')
        print(f"Successfully opened sensor at {W1PATH}")
    except Exception as e:
        print(f"Notice: Could not open actual sensor ({e}). Falling back to simulated data for testing.")

    while True:
        try:
            timestamp = str(datetime.now())
            if f is not None:
                f.write(b'\xA5\x00\x01') # Turn on LED
                f.seek(0)
                f.write(b'\xB4') # Start sensor conversion cycle
                f.seek(0)
                time.sleep(1) # Wait for conversion

                f.write(b'\xA5\x00\x00') # Turn off LED
                f.seek(0)
                f.write(b'\xF0\x00') # Read memory
                binData = f.read(33)
                byteList = list(binData)
                temp = ''.join(map(chr, byteList[15:22])).strip()
                humidity = ''.join(map(chr, byteList[22:29])).strip()
            else:
                # Mock data if running on a machine without the 1-Wire device
                import random
                time.sleep(1)
                base_temp_f = 77.0 # 25 C
                base_hum = 50.0
                temp = str(round(base_temp_f + random.uniform(-1, 1), 2))
                humidity = str(round(base_hum + random.uniform(-2, 2), 2))
                
            latest_data = {
                "temp": temp,
                "humidity": humidity,
                "timestamp": timestamp
            }
            history_data.append(latest_data)
            # For logging
            # print(f"{timestamp}, {temp}, {humidity}")
        except Exception as e:
            print(f"Error reading sensor: {e}")
            time.sleep(1) # prevent rapid looping on fail
        finally:
            pass

@app.on_event("startup")
async def startup_event():
    # Start the sensor reading thread
    thread = threading.Thread(target=sensor_reader_loop, daemon=True)
    thread.start()
    
    # Start the asyncio background task to broadcast data to websockets
    asyncio.create_task(broadcast_data())

async def broadcast_data():
    while True:
        await asyncio.sleep(1)
        if latest_data["temp"] is not None:
            await manager.broadcast(json.dumps(latest_data))

@app.get("/history")
async def get_history():
    return {"history": history_data}

@app.get("/download")
async def download_csv():
    # first column of CSV file is the date, the second colunm is the time, the third colunm is the temperature, and the fourth colunm is the humidity
    lines = ["Date,Time,Temperature (F),Humidity (%)"]
    for data in history_data:
        try:
            # timestamp format: '2026-04-19 17:05:02.123456'
            dt = datetime.fromisoformat(data["timestamp"])
            date_str = dt.strftime("%Y-%m-%d")
            time_str = dt.strftime("%H:%M:%S")
            lines.append(f"{date_str},{time_str},{data['temp']},{data['humidity']}")
        except Exception:
            pass
    csv_content = "\n".join(lines)
    return Response(content=csv_content, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=sensor_data.csv"})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    uvicorn.run("TemperatureHumiditySensor:app", host="0.0.0.0", port=8000, reload=False)
