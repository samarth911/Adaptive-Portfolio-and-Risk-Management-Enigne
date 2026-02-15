import { useEffect, useState } from "react";
import { getEngineLog } from "../api";

export default function EngineLogPanel() {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    const fetchLog = async () => {
      try {
        const res = await getEngineLog(80);
        setLogs(res.data?.logs || []);
      } catch (e) {
        console.error(e);
      }
    };
    fetchLog();
    const interval = setInterval(fetchLog, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="card engine-log-panel">
      <div className="panel-header">AI Decision Log — What the engine did and why</div>
      <div className="log-container">
        {logs.length === 0 ? (
          <div className="log-empty">
            No decisions yet. Run a backtest or start the simulation to see step-by-step explanations of every rebalance and risk action.
          </div>
        ) : (
          [...logs]
            .reverse()
            .slice(0, 80)
            .map((entry, idx) => (
              <div key={idx} className="log-entry-detailed">
                <div className="log-entry-meta">
                  <span className="log-date">{entry.date}</span>
                  <span className={`log-regime regime-badge ${entry.regime || ""}`}>{entry.regime || "—"}</span>
                </div>
                <div className="log-entry-body">
                  <p className="log-what">{entry.what_we_did}</p>
                  <p className="log-why"><strong>Why this matters:</strong> {entry.why_it_matters}</p>
                  {entry.regime_in_plain_english && (
                    <p className="log-regime-desc"><strong>Market right now:</strong> {entry.regime_in_plain_english.replace(/\*\*/g, "")}</p>
                  )}
                </div>
              </div>
            ))
        )}
      </div>
    </div>
  );
}
