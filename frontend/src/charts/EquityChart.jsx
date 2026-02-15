import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";

export default function EquityChart({ data, withRisk = true }) {
  const series = Array.isArray(data) ? data : [];
  return (
    <div className="card chart-container">
      <h2>Equity Curve {withRisk ? "(with risk engine)" : "(no risk)"}</h2>
      <ResponsiveContainer width="100%" height={280}>
        <LineChart data={series} margin={{ top: 5, right: 5, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,0,0,0.06)" />
          <XAxis dataKey="date" stroke="#86868b" fontSize={12} tick={{ fill: "#6e6e73" }} />
          <YAxis stroke="#86868b" fontSize={12} tick={{ fill: "#6e6e73" }} tickFormatter={(v) => `$${(v / 1e6).toFixed(2)}M`} />
          <Tooltip
            contentStyle={{ background: "#fff", border: "1px solid rgba(0,0,0,0.08)", borderRadius: 12, boxShadow: "0 4px 20px rgba(0,0,0,0.08)" }}
            labelStyle={{ color: "#1d1d1f" }}
            formatter={(v) => [`$${Number(v).toLocaleString("en-US", { minimumFractionDigits: 2 })}`, "Value"]}
          />
          <Line
            type="monotone"
            dataKey="value"
            stroke="#0071e3"
            strokeWidth={2}
            dot={false}
            name="Portfolio"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
