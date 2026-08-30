from flask import Flask, jsonify
from flask_cors import CORS
import serial
import threading
import time
from predict import predict_oil_temp

# ---------------- CONFIG ----------------
PORT = "COM3"
BAUD = 115200
MIST_THRESHOLD = 90

# ---------------- FLASK ----------------
app = Flask(__name__)
CORS(app)

ser = None

# Live data shared with React
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

# ---------------- SERIAL THREAD ----------------
def read_serial():
    global ser

    while True:
        try:
            line = ser.readline().decode(errors="ignore").strip()

            if not line:
                continue

            values = [float(v) for v in line.split(",")]

            # Expected:
            # humidity,current,load,loadCurrent,powerFactor
            if len(values) != 5:
                print("Invalid:", line)
                continue

            humidity, current, load, load_current, pf = values

            # ML prediction requires 6 features
            features = [
                humidity,
                current,
                load,
                humidity,
                current,
                load
            ]

            predicted_temp = predict_oil_temp(features)

            latest["temperature"] = round(predicted_temp, 1)
            latest["humidity"] = round(humidity, 1)
            latest["current"] = round(current, 2)
            latest["load"] = int(load)
            latest["loadCurrent"] = round(load_current, 2)
            latest["powerFactor"] = round(pf, 2)

            if predicted_temp > MIST_THRESHOLD:
                latest["pump"] = "ON"
                ser.write(b"MIST_ON\n")
            else:
                latest["pump"] = "OFF"
                ser.write(b"MIST_OFF\n")

            print(latest)

        except Exception as e:
            print("Serial Error:", e)

# ---------------- API ----------------
@app.route("/")
def home():
    return "Smart Mist Cooling Backend Running"

@app.route("/api/data")
def get_data():
    return jsonify(latest)

# ---------------- MAIN ----------------
if __name__ == "__main__":

    ser = serial.Serial(PORT, BAUD, timeout=2)
    time.sleep(2)
    ser.reset_input_buffer()

    threading.Thread(target=read_serial, daemon=True).start()

    print(f"Listening on {PORT} at {BAUD} baud")
    app.run(host="127.0.0.1", port=5000, debug=False)