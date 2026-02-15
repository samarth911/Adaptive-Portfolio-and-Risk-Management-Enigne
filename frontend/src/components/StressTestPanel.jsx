export default function StressTestPanel({ result }) {
  if (!result) {
    return (
      <div className="card">
        <h2>Stress test results</h2>
        <p style={{ color: "#6e6e73", fontSize: "0.9375rem" }}>Run stress test to see how your portfolio would hold up in a -5% daily shock.</p>
      </div>
    );
  }
  const m = result.metrics_after_stress || {};
  return (
    <div className="card">
      <h2>Stress test results</h2>
      <p style={{ color: "#6e6e73", marginBottom: "0.75rem", fontSize: "0.9375rem" }}>{result.scenario || "-5% daily shock for 5 days"}</p>
      <div className="metrics-table">
        <table>
          <tbody>
            <tr><td>Max drawdown after shock</td><td>{(m["Max Drawdown"] != null ? m["Max Drawdown"] * 100 : 0).toFixed(2)}%</td></tr>
            <tr><td>CAGR (stressed)</td><td>{(m.CAGR != null ? m.CAGR * 100 : 0).toFixed(2)}%</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}
