import {
  RadialBarChart,
  RadialBar,
  PolarAngleAxis
} from "recharts";

export default function Gauge({ value, title, color }) {

  const data = [{ value }];

  return (
    <div className="gauge">
      <h3>{title}</h3>

      <RadialBarChart
        width={220}
        height={180}
        innerRadius="70%"
        outerRadius="100%"
        data={data}
        startAngle={180}
        endAngle={0}
      >
        <PolarAngleAxis
          type="number"
          domain={[0,100]}
          tick={false}
        />

        <RadialBar
          background
          dataKey="value"
          fill={color}
          cornerRadius={10}
        />
      </RadialBarChart>

      <h2>{value}%</h2>
    </div>
  );
}