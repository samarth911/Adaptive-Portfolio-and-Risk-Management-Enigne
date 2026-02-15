export default function MetricsTable({ metrics }) {
  return (
    <div className="card">
      <h2>Performance Metrics</h2>
      <table>
        <tbody>
          {Object.entries(metrics).map(([key, value]) => (
            <tr key={key}>
              <td>{key}</td>
              <td>{(value * 100).toFixed(2)}%</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
