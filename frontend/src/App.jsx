import { useEffect, useState } from "react";
import axios from "axios";
import "./App.css";

import Gauge from "./Components/Gauge";
import StatCard from "./Components/StatCard";

export default function App() {
  const [data, setData] = useState({
    temperature: 0,
    humidity: 0,
    load: 0,
    current: 0,
    voltage: 220,
    powerFactor: 0.75,
    pump: "OFF",
  });

  const [status, setStatus] = useState("Connecting...");

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await axios.get("/api/data");
        setData(res.data);
        setStatus("Live");
      } catch (err) {
        console.log(err);
        setStatus("Offline");
      }
    };

    fetchData();
    const timer = setInterval(fetchData, 1000);

    return () => clearInterval(timer);
  }, []);

  return (
    <div className="app">
      <div className="header">
        <div>
          <h1>SMART MIST COOLING SYSTEM</h1>
          <p>AI Based Transformer Monitoring Dashboard</p>
        </div>

        <div className={status === "Live" ? "live" : "offline"}>
          ● {status}
        </div>
      </div>

      <div className="grid">
        <StatCard
          title="Oil Temperature"
          value={data.temperature}
          unit="°C"
          color="#ff6b6b"
        />

        <StatCard
          title="Humidity"
          value={data.humidity}
          unit="%"
          color="#4cc9f0"
        />

        <StatCard
          title="Current"
          value={data.current}
          unit="A"
          color="#80ed99"
        />

        <StatCard
          title="Voltage"
          value={data.voltage}
          unit="V"
          color="#ffd166"
        />
      </div>

      <div className="bottomSection">
        <div className="gaugeCard">
          <Gauge
            title="Transformer Load"
            value={data.load}
            color="#4f8cff"
          />
        </div>

        <div className="statusCard">
          <h2>Mist Pump Status</h2>

          <div className={data.pump === "ON" ? "pumpOn" : "pumpOff"}>
            {data.pump}
          </div>

          <div className="pfBox">
            <p>Power Factor</p>
            <h1>{data.powerFactor}</h1>
          </div>

          <div className="info">
            <div>
              <span>System</span>
              <strong>ESP32</strong>
            </div>

            <div>
              <span>Refresh</span>
              <strong>1 sec</strong>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}