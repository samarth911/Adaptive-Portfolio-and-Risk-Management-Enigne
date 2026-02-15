
import { useState } from "react";
import API from "../api";

export default function ControlPanel({ setStatus }) {

  const startEngine = async () => {
    try {
      await API.post("/start");
      setStatus("Running");
    } catch (err) {
      console.error(err);
    }
  };

  const stopEngine = async () => {
    try {
      await API.post("/stop");
      setStatus("Stopped");
    } catch (err) {
      console.error(err);
    }
  };

  const rebalance = async () => {
    try {
      await API.post("/rebalance");
    } catch (err) {
      console.error(err);
    }
  };

  const stressTest = async () => {
    try {
      await API.post("/stress-test");
    } catch (err) {
      console.error(err);
    }
  };
    const [newFund, setNewFund] = useState("");

    const addFund = async () => {
    await API.post("/add-fund", null, {
        params: { ticker: newFund }
    });
    };

  return (
    <div className="card">
      <h2>Engine Controls</h2>

      <div className="button-group">
        <button className="btn start" onClick={startEngine}>
          ▶ Start Engine
        </button>

        <button className="btn stop" onClick={stopEngine}>
          ⏹ Stop Engine
        </button>

        <button className="btn rebalance" onClick={rebalance}>
          🔁 Rebalance
        </button>

        <button className="btn stress" onClick={stressTest}>
          🌪 Stress Test
        </button>
            <input
                value={newFund}
                onChange={(e) => setNewFund(e.target.value)}
                placeholder="Add Fund (e.g., TSLA)"
                />

                <button onClick={addFund}>
                ➕ Add Fund
                </button>

      </div>
    </div>
  );
}
