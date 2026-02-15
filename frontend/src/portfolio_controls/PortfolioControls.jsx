import { useState } from "react";
import API, { startEngine, stopEngine, runBacktest, runStressTest, setRiskLevel } from "../api";
import PaymentModal from "../payment_modal/PaymentModal";

export default function PortfolioControls({ setStatus, onBacktestDone, onStressDone }) {
  const [paymentModal, setPaymentModal] = useState(null);
  const [backtestLoading, setBacktestLoading] = useState(false);
  const [stressLoading, setStressLoading] = useState(false);
  const [riskLevel, setRiskLevelLocal] = useState("MEDIUM");

  const start = async () => {
    try {
      await startEngine();
      setStatus("Running");
    } catch (e) {
      console.error(e);
    }
  };

  const stop = async () => {
    try {
      await stopEngine();
      setStatus("Stopped");
    } catch (e) {
      console.error(e);
    }
  };

  const runBacktestClick = async () => {
    setBacktestLoading(true);
    try {
      await runBacktest({
        start_date: "2015-01-01",
        end_date: "2024-01-01",
        tickers: ["SPY", "TLT", "GLD"],
        risk_level: riskLevel,
      });
      onBacktestDone && onBacktestDone();
    } catch (e) {
      console.error(e);
    } finally {
      setBacktestLoading(false);
    }
  };

  const runStressClick = async () => {
    setStressLoading(true);
    try {
      const res = await runStressTest({});
      onStressDone && onStressDone(res.data);
    } catch (e) {
      console.error(e);
    } finally {
      setStressLoading(false);
    }
  };

  const setRisk = async (level) => {
    setRiskLevelLocal(level);
    try {
      await setRiskLevel(level);
    } catch (e) {
      console.error(e);
    }
  };

  const handlePaymentSuccess = () => {
    setPaymentModal(null);
  };

  return (
    <>
      <div className="card portfolio-controls-card">
        <h2>Controls</h2>
        <p className="portfolio-controls-desc">Run the engine, backtest, and manage risk and funds.</p>

        <section className="controls-section">
          <span className="controls-section-label">Simulation</span>
          <div className="controls-row">
            <button type="button" className="btn btn-start" onClick={start}>
              Start
            </button>
            <button type="button" className="btn btn-stop" onClick={stop}>
              Stop
            </button>
            <button type="button" className="btn btn-secondary" onClick={() => API.post("/rebalance")}>
              Rebalance
            </button>
          </div>
        </section>

        <section className="controls-section">
          <span className="controls-section-label">Analysis</span>
          <div className="controls-row">
            <button
              type="button"
              className="btn btn-primary"
              onClick={runBacktestClick}
              disabled={backtestLoading}
            >
              {backtestLoading ? "Running…" : "Run backtest"}
            </button>
            <button
              type="button"
              className="btn btn-amber"
              onClick={runStressClick}
              disabled={stressLoading}
            >
              {stressLoading ? "Running…" : "Stress test"}
            </button>
          </div>
        </section>

        <section className="controls-section">
          <span className="controls-section-label">Risk level</span>
          <div className="segmented-control" role="group" aria-label="Risk level">
            {["LOW", "MEDIUM", "HIGH"].map((level) => (
              <button
                key={level}
                type="button"
                className={"segmented-option" + (riskLevel === level ? " selected" : "")}
                onClick={() => setRisk(level)}
              >
                {level}
              </button>
            ))}
          </div>
        </section>

        <section className="controls-section controls-section-last">
          <span className="controls-section-label">Funds</span>
          <div className="controls-row">
            <button type="button" className="btn btn-secondary" onClick={() => setPaymentModal("add")}>
              Add funds
            </button>
            <button type="button" className="btn btn-secondary" onClick={() => setPaymentModal("withdraw")}>
              Withdraw
            </button>
          </div>
        </section>
      </div>

      {paymentModal && (
        <PaymentModal
          mode={paymentModal}
          onClose={() => setPaymentModal(null)}
          onSuccess={handlePaymentSuccess}
        />
      )}
    </>
  );
}
