export default function PortfolioCard({ data }) {
  return (
    <div className="card">
      <h2>Portfolio Value</h2>
      <p>${data.portfolio_value.toLocaleString()}</p>
    </div>
  );
}
