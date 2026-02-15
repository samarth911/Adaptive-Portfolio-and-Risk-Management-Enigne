import { useEffect, useState } from "react";
import { getState, getPortfolio, getBacktestResults } from "../api";
import Header from "../components/Header";
import EquityChart from "../charts/EquityChart";
import DrawdownChart from "../charts/DrawdownChart";
import AllocationPie from "../charts/AllocationPie";
import CorrelationHeatmap from "../charts/CorrelationHeatmap";
import RiskMetricsCard from "../components/RiskMetricsCard";
import StressTestPanel from "../components/StressTestPanel";
import EngineLogPanel from "../engine_log_panel/EngineLogPanel";
import PortfolioControls from "../portfolio_controls/PortfolioControls";

function computeDrawdown(equitySeries) {
  if (!Array.isArray(equitySeries) || equitySeries.length === 0) return [];
  let peak = equitySeries[0];
  return equitySeries.map((v, i) => {
    if (v > peak) peak = v;
    return { date: String(i), drawdown: peak > 0 ? (v - peak) / peak : 0 };
  });
}

export default function Dashboard() {
  const [state, setState] = useState({ value: 0, regime: "UNKNOWN", allocations: {}, history: [], logs: [], risk_level: "MEDIUM" });
  const [status, setStatus] = useState("Stopped");
  const [backtest, setBacktest] = useState(null);
  const [stressResult, setStressResult] = useState(null);

  useEffect(() => {
    const poll = async () => {
      try {
        const res = await getState();
        if (res.data) setState(res.data);
      } catch (e) {
        console.error(e);
      }
    };
    poll();
    const interval = setInterval(poll, 2000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const load = async () => {
      try {
        const [portRes, btRes] = await Promise.all([getPortfolio(), getBacktestResults()]);
        if (portRes.data?.metrics) setBacktest((b) => ({ ...b, metrics_with_risk: portRes.data.metrics }));
        if (btRes.data?.equity_with_risk?.length) setBacktest((b) => ({ ...b, ...btRes.data }));
      } catch (e) {}
    };
    load();
  }, []);

  const equityData = backtest?.equity_with_risk?.length
    ? backtest.equity_with_risk
    : state.history?.map((v, i) => ({ date: String(i), value: v })) || [];
  const drawdownData = computeDrawdown(equityData.map((d) => d.value));

  return (
    <div className="dashboard">
      <Header />
      <div className="status-bar">
        <div>Engine: <b>{status}</b></div>
        <div>Portfolio: <b>${Number(state.value).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</b></div>
        <div>
          Regime: <span className={`regime-badge ${state.regime}`}>{state.regime}</span>
        </div>
        <div>Risk: <b>{state.risk_level}</b></div>
      </div>

      <div className="grid-2" style={{ marginBottom: "1.5rem" }}>
        <PortfolioControls
          setStatus={setStatus}
          onBacktestDone={async () => {
            try {
              const res = await getBacktestResults();
              if (res.data) setBacktest(res.data);
            } catch (e) {}
          }}
          onStressDone={setStressResult}
        />
        <RiskMetricsCard metrics={backtest?.metrics_with_risk} label="(with risk)" />
      </div>

      {backtest?.metrics_without_risk && (
        <div className="grid-2" style={{ marginBottom: "1.5rem" }}>
          <RiskMetricsCard metrics={backtest.metrics_without_risk} label="(without risk)" />
          <StressTestPanel result={stressResult} />
        </div>
      )}
      {!backtest?.metrics_without_risk && <StressTestPanel result={stressResult} />}

      <div className="grid-2" style={{ marginBottom: "1.5rem" }}>
        <EquityChart data={equityData} withRisk />
        <AllocationPie allocations={state.allocations} />
      </div>

      <div className="grid-2" style={{ marginBottom: "1.5rem" }}>
        <DrawdownChart data={drawdownData} />
        <CorrelationHeatmap data={backtest?.correlation_matrix || []} />
      </div>

      <div style={{ marginBottom: "1.5rem" }}>
        <EngineLogPanel />
      </div>
    </div>
  );
}
