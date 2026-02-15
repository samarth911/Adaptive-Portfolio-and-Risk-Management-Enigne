export default function RiskMetricsCard({ metrics, label = "With risk engine" }) {
  const m = metrics || {};
  const rows = [
    ["CAGR", m.CAGR != null ? `${(m.CAGR * 100).toFixed(2)}%` : "—"],
    ["Sharpe Ratio", m["Sharpe Ratio"] != null ? m["Sharpe Ratio"].toFixed(2) : "—"],
    ["Sortino Ratio", m["Sortino Ratio"] != null ? m["Sortino Ratio"].toFixed(2) : "—"],
    ["Max Drawdown", m["Max Drawdown"] != null ? `${(m["Max Drawdown"] * 100).toFixed(2)}%` : "—"],
    ["Calmar Ratio", m["Calmar Ratio"] != null ? m["Calmar Ratio"].toFixed(2) : "—"],
  ];
  return (
    <div className="card">
      <h2>Risk metrics {label}</h2>
      <div className="metrics-table">
        <table>
          <tbody>
            {rows.map(([k, v]) => (
              <tr key={k}>
                <td>{k}</td>
                <td style={{ color: "var(--text)" }}>{v}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
