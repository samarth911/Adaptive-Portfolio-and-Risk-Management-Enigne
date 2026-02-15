import { useEffect, useState } from "react";
import API from "../api";

import Header from "./Header";
import EquityChart from "./EquityChart";
import AllocationPie from "./AllocationPie";
import ActivityLog from "./ActivityLog";
import ControlPanel from "./ControlPanel";

export default function Dashboard() {

  const [equityData, setEquityData] = useState([]);
  const [allocations, setAllocations] = useState({});
  const [logs, setLogs] = useState([]);
  const [status, setStatus] = useState("Stopped");
  const [portfolioValue, setPortfolioValue] = useState(0);
  const [regime, setRegime] = useState("Unknown");

  // Poll backend every 2 seconds
  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const res = await API.get("/state");

        if (res.data) {
          setPortfolioValue(res.data.value);
          setAllocations(res.data.allocations || {});
          setLogs(res.data.logs || []);
          setRegime(res.data.regime || "Unknown");

          if (res.data.history) {
            const formatted = res.data.history.map((v, i) => ({
              time: i,
              value: v
            }));
            setEquityData(formatted);
          }
        }
      } catch (err) {
        console.error("Polling error:", err);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="dashboard">

      <Header />

      <div className="status-bar">
        <div>Engine Status: <b>{status}</b></div>
        <div>Portfolio Value: <b>${portfolioValue?.toFixed(2)}</b></div>
        <div>Market Regime: <b>{regime}</b></div>
      </div>

      <ControlPanel setStatus={setStatus} />

      <div className="grid">
        <EquityChart data={equityData} />
        <AllocationPie allocations={allocations} />
      </div>

      <ActivityLog logs={logs} />

    </div>
  );
}
