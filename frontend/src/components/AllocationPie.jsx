import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer
} from "recharts";

const COLORS = [
  "#00ff88",
  "#0088ff",
  "#ffbb28",
  "#ff4d4f",
  "#aa66ff",
  "#ff7f50"
];

export default function AllocationPie({ allocations }) {

  const data = Object.keys(allocations || {}).map((key) => ({
    name: key,
    value: allocations[key]
  }));

  return (
    <div className="card">
      <h2>Asset Allocation</h2>

      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={data}
            dataKey="value"
            nameKey="name"
            outerRadius={100}
            fill="#8884d8"
            label
          >
            {data.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={COLORS[index % COLORS.length]}
              />
            ))}
          </Pie>
          <Tooltip />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
