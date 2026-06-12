import { T } from "../theme";

const COLORS = { green: T.green, blue: T.blue, purple: T.purple, teal: T.teal, yellow: T.yellow };

// Segmento da stat-bar (estilo five-pillar): valor mono pesado + label uppercase
export default function KpiCard({ label, value, sub, color = "green" }) {
  const accent = COLORS[color] || T.green;
  return (
    <div className="stat-item">
      <div className="stat-val" style={{ color: accent }}>{value}</div>
      <div className="stat-label">{label}</div>
      {sub && <div className="stat-sub">{sub}</div>}
    </div>
  );
}
