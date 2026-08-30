import {
  RadialBarChart,
  RadialBar,
  PolarAngleAxis,
} from "recharts";

export default function Gauge({ value = 0, title, color }) {
  const chartData = [
    {
      name: "Load",
      value: Math.min(Math.max(value, 0), 100),
    },
  ];

  return (
    <div className="gauge">
      <h3>{title}</h3>

      <RadialBarChart
        width={220}
        height={180}
        innerRadius="68%"
        outerRadius="100%"
        data={chartData}
        startAngle={180}
        endAngle={0}
      >
        <PolarAngleAxis
          type="number"
          domain={[0, 100]}
          tick={false}
        />

        <RadialBar
          dataKey="value"
          background
          fill={color}
          cornerRadius={12}
        />
      </RadialBarChart>

      <div className="gaugeValue">
        <h2>{Math.round(value)}%</h2>
        <p>Transformer Load</p>
      </div>
    </div>
  );
}