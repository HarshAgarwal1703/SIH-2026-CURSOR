import { motion } from "framer-motion";

export default function StatCard({ title, value, unit, color }) {
  return (
    <motion.div className="card" whileHover={{ scale: 1.03 }}>
      <h3>{title}</h3>

      <div className="cardValue" style={{ color }}>
        {value}
        <span>{unit}</span>
      </div>
    </motion.div>
  );
}