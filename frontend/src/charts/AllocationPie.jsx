import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from "recharts";

const COLORS = ["#34c759", "#0071e3", "#ff9500", "#af52de", "#ff3b30", "#5ac8fa"];

export default function AllocationPie({ allocations }) {
  const data = Object.entries(allocations || {}).map(([name, value]) => ({
    name,
    value: Math.round(Number(value) * 100) / 100,
  })).filter((d) => d.value > 0);
  if (data.length === 0) {
    return (
      <div className="card chart-container">
        <h2>Asset Allocation</h2>
        <div style={{ height: 280, display: "flex", alignItems: "center", justifyContent: "center", color: "#6e6e73" }}>
          No allocation data
        </div>
      </div>
    );
  }
  return (
    <div className="card chart-container">
      <h2>Asset Allocation</h2>
      <ResponsiveContainer width="100%" height={280}>
        <PieChart>
          <Pie
            data={data}
            dataKey="value"
            nameKey="name"
            cx="50%"
            cy="50%"
            outerRadius={90}
            label={({ name, value }) => `${name} ${(value * 100).toFixed(0)}%`}
          >
            {data.map((entry, index) => (
              <Cell key={entry.name} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{ background: "#fff", border: "1px solid rgba(0,0,0,0.08)", borderRadius: 12, boxShadow: "0 4px 20px rgba(0,0,0,0.08)" }}
            formatter={(v) => [`${(Number(v) * 100).toFixed(2)}%`, "Weight"]}
          />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
