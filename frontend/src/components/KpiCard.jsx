import { T } from "../theme";

const COLORS = { green: T.green, blue: T.blue, purple: T.purple, teal: T.teal, yellow: T.yellow };

export default function KpiCard({ label, value, sub, color = "green" }) {
  const accent = COLORS[color] || T.green;
  return (
    <div style={{
      flex: 1,
      background: "linear-gradient(160deg, rgba(0,0,0,0.15) 0%, #002235 100%)",
      border: "1px solid rgba(255,255,255,0.06)",
      borderTop: `3px solid ${accent}`,
      borderRadius: "0 0 8px 8px",
      padding: "16px 18px 14px",
    }}>
      <div style={{ fontSize: 10, fontWeight: 700, textTransform: "uppercase",
                    letterSpacing: "0.12em", color: T.text3, marginBottom: 8 }}>{label}</div>
      <div style={{ fontSize: 30, fontWeight: 700, color: accent, fontFamily: T.font,
                    lineHeight: 1.05, letterSpacing: "-0.03em" }}>{value}</div>
      {sub && <div style={{ fontSize: 11, color: T.text3, marginTop: 8, fontFamily: T.mono }}>{sub}</div>}
    </div>
  );
}
