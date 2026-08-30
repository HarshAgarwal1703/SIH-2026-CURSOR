from flask import Flask, jsonify
from flask_cors import CORS
import serial
import threading
import time
import joblib
import pandas as pd

# =========================
# CONFIGURATION
# =========================
PORT = "COM3"
BAUD = 115200

DECISION_THRESHOLD = 36.0  # AI relay threshold

# =========================
# LOAD ML MODEL
# =========================
model = joblib.load("model.pkl")

# =========================
# FLASK APP
# =========================
app = Flask(__name__)
CORS(app)

ser = None

# Live data for React
latest = {
    "temperature": 0.0,
    "humidity": 0.0,
    "load": 0,
    "current": 0.0,
    "loadCurrent": 0.0,
    "voltage": 220,
    "powerFactor": 0.0,
    "pump": "OFF"
}

# =========================
# SERIAL READER THREAD
# Expected Arduino Format:
# dhtTemp,dhtHum,dsTemp,load,pf,loadCurrent,mode
# =========================
def read_serial():
    global ser

    while True:
        try:
            line = ser.readline().decode(errors="ignore").strip()

            if not line:
                continue

            print("RAW:", line)

            parts = line.split(",")

            if len(parts) < 7:
                continue

            dhtTemp = float(parts[0])
            humidity = float(parts[1])
            dsTemp = float(parts[2])
            load = float(parts[3])
            pf = float(parts[4])
            loadCurrent = float(parts[5])
            mode = parts[6]

            # ML Prediction
            X = pd.DataFrame(
                [[dhtTemp, dsTemp, load, pf]],
                columns=[
                    "ambient_temp",
                    "hotspot_temp",
                    "load_percent",
                    "load_efficiency_index",
                ],
            )

            predicted_temp = float(model.predict(X)[0])

            # Relay Command
            if predicted_temp > DECISION_THRESHOLD:
                ser.write(b"RELAY_ON\n")
                pump = "ON"
            else:
                ser.write(b"RELAY_OFF\n")
                pump = "OFF"

            # Update React data
            latest["temperature"] = round(predicted_temp, 1)
            latest["humidity"] = round(humidity, 1)
            latest["load"] = int(load)
            latest["current"] = round(dsTemp, 1)
            latest["loadCurrent"] = round(loadCurrent, 2)
            latest["powerFactor"] = round(pf, 2)
            latest["pump"] = pump

            print(
                f"Pred:{predicted_temp:.1f}°C | "
                f"Load:{load}% | LC:{loadCurrent:.2f}A | {pump}"
            )

        except Exception as e:
            print("Serial Error:", e)

# =========================
# API ROUTES
# =========================
@app.route("/")
def home():
    return "Smart Mist Cooling Backend Running"

@app.route("/api/data")
def get_data():
    return jsonify(latest)

# =========================
# MAIN
# =========================
if __name__ == "__main__":
    ser = serial.Serial(PORT, BAUD, timeout=2)
    time.sleep(2)
    ser.reset_input_buffer()

    threading.Thread(target=read_serial, daemon=True).start()

    print(f"Listening on {PORT} ({BAUD} baud)")
    app.run(host="127.0.0.1", port=5000, debug=False)