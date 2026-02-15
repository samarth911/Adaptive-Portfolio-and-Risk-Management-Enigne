export default function RiskCard({ risk }) {
  return (
    <div className="card">
      <h2>Risk Status</h2>
      <p>{risk}</p>
    </div>
  );
}
