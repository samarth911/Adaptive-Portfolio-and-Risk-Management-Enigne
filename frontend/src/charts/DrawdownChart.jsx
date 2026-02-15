import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";

/** data: [{ date, drawdown }] where drawdown is 0 to -1 */
export default function DrawdownChart({ data }) {
  const series = Array.isArray(data) ? data : [];
  return (
    <div className="card chart-container">
      <h2>Drawdown</h2>
      <ResponsiveContainer width="100%" height={280}>
        <AreaChart data={series} margin={{ top: 5, right: 5, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,0,0,0.06)" />
          <XAxis dataKey="date" stroke="#86868b" fontSize={12} tick={{ fill: "#6e6e73" }} />
          <YAxis stroke="#86868b" fontSize={12} tick={{ fill: "#6e6e73" }} tickFormatter={(v) => `${(v * 100).toFixed(0)}%`} domain={["dataMin", 0]} />
          <Tooltip
            contentStyle={{ background: "#fff", border: "1px solid rgba(0,0,0,0.08)", borderRadius: 12, boxShadow: "0 4px 20px rgba(0,0,0,0.08)" }}
            formatter={(v) => [`${(Number(v) * 100).toFixed(2)}%`, "Drawdown"]}
          />
          <Area type="monotone" dataKey="drawdown" stroke="#ff3b30" fill="rgba(255,59,48,0.12)" strokeWidth={1.5} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
