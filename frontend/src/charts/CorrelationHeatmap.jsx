/** Simple correlation heatmap placeholder - API can later provide matrix */
export default function CorrelationHeatmap({ data }) {
  const matrix = data || [];
  const labels = matrix.length && matrix[0] ? Object.keys(matrix[0]) : [];
  const getColor = (v) => {
    const x = (Number(v) + 1) / 2;
    const r = Math.round(255 - x * 200);
    const g = Math.round(255 - x * 120);
    const b = Math.round(255 - x * 80);
    return `rgb(${r},${g},${b})`;
  };
  return (
    <div className="card chart-container">
      <h2>Correlation Matrix</h2>
      <p style={{ margin: "0 0 0.75rem", fontSize: "0.9375rem", color: "#6e6e73" }}>
        How much assets move together (−1 to 1). Run backtest to see.
      </p>
      {labels.length === 0 ? (
        <div style={{ height: 200, display: "flex", alignItems: "center", justifyContent: "center", color: "#6e6e73" }}>
          Run backtest to load correlation data
        </div>
      ) : (
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.8rem" }}>
            <thead>
              <tr>
                <th style={{ padding: "0.5rem 0.6rem", color: "#6e6e73", textAlign: "left", fontSize: "0.875rem" }}></th>
                {labels.map((l) => (
                  <th key={l} style={{ padding: "0.5rem 0.6rem", color: "#6e6e73", minWidth: 52, fontSize: "0.875rem" }}>{l}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {matrix.slice(0, labels.length).map((row, i) => (
                <tr key={i}>
                  <td style={{ padding: "0.5rem 0.6rem", color: "#6e6e73", fontSize: "0.875rem" }}>{labels[i]}</td>
                  {labels.map((l, j) => (
                    <td
                      key={l}
                      style={{
                        padding: "0.5rem 0.6rem",
                        background: getColor(row[labels[j]] ?? 0),
                        color: "#1d1d1f",
                        textAlign: "center",
                        borderRadius: 4,
                      }}
                    >
                      {row[labels[j]] != null ? Number(row[labels[j]]).toFixed(2) : "-"}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
