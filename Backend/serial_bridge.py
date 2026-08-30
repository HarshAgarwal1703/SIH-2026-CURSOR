from flask import Flask, jsonify
from flask_cors import CORS
import serial
import threading
import time
from predict import predict_oil_temp

PORT = "COM3"
BAUD = 115200
MIST_THRESHOLD = 90

app = Flask(__name__)
CORS(app)

ser = None

latest = {
    "temperature": 0,
    "humidity": 0,
    "load": 0,
    "current": 0,
    "voltage": 220,
    "powerFactor": 0.75,
    "pump": "OFF"
}

def read_serial():
    global ser

    while True:
        line = ser.readline().decode(errors="ignore").strip()

        if not line:
            continue

        try:
            values = [float(x) for x in line.split(",")]
        except:
            continue

        if len(values) != 3:
            continue

        humidity, current, load = values

        temp = predict_oil_temp(values * 2)

        latest["temperature"] = round(temp, 1)
        latest["humidity"] = humidity
        latest["current"] = round(current, 2)
        latest["load"] = int(load)

        if temp > MIST_THRESHOLD:
            latest["pump"] = "ON"
            ser.write(b"MIST_ON\n")
        else:
            latest["pump"] = "OFF"
            ser.write(b"MIST_OFF\n")


@app.route("/")
def home():
    return "Mist Cooling Backend Running"


@app.route("/api/data", methods=["GET"])
def get_data():
    return jsonify(latest)


if __name__ == "__main__":
    ser = serial.Serial(PORT, BAUD, timeout=2)
    time.sleep(2)

    threading.Thread(target=read_serial, daemon=True).start()

    app.run(host="127.0.0.1", port=5000, debug=False)