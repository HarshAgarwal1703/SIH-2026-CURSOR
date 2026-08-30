import { motion } from "framer-motion";

export default function StatCard({
  title,
  value,
  unit,
  color,
}) {
  const displayValue =
    typeof value === "number"
      ? Number(value).toFixed(value % 1 === 0 ? 0 : 2)
      : value;

  return (
    <motion.div
      className="card"
      whileHover={{ scale: 1.03 }}
      transition={{ duration: 0.2 }}
    >
      <div className="cardHeader">
        <span className="dot" style={{ background: color }}></span>
        <h3>{title}</h3>
      </div>

      <div className="cardValue" style={{ color }}>
        {displayValue}
        <span>{unit}</span>
      </div>
    </motion.div>
  );
}