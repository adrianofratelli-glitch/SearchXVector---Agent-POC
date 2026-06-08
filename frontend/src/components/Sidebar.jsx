import { Overline, Body } from "@leafygreen-ui/typography";
import Leaf from "./Leaf";
import { T, fmtCount } from "../theme";

const NAV = [
  { section: "BUSCA", items: [
    { icon: "🔍", label: "Atlas Search", tab: 0 },
    { icon: "⚡", label: "Search vs Vector", tab: 1 },
    { icon: "🔀", label: "Hybrid RRF", tab: 2 },
    { icon: "🎯", label: "Similares", tab: 3 },
  ]},
  { section: "ANALYTICS & AI", items: [
    { icon: "📊", label: "Analytics", tab: 4 },
    { icon: "💬", label: "Reviews RAG", tab: 5 },
    { icon: "🤖", label: "AI Agent", tab: 6 },
  ]},
];

const COL_COLORS = [T.green, T.blue, T.purple];

export default function Sidebar({ active, onSelect, stats }) {
  const collections = stats?.collections || {};
  const indices = stats?.indices || [];

  return (
    <div style={{
      width: 240, minWidth: 240, background: T.sidebar, minHeight: "100vh",
      borderRight: `1px solid ${T.border}`, padding: "18px 14px", display: "flex",
      flexDirection: "column", gap: 4,
    }}>
      {/* Brand */}
      <div style={{ display: "flex", alignItems: "center", gap: 10, paddingBottom: 14,
                    borderBottom: `1px solid ${T.border}`, marginBottom: 8 }}>
        <Leaf size={26} />
        <div>
          <div style={{ fontFamily: "'MongoDB Value Serif', Georgia, serif", fontSize: 16,
                        fontWeight: 700, color: T.text, lineHeight: 1.15 }}>Search × Vector</div>
          <div style={{ fontFamily: T.mono, fontSize: 9, color: T.text3,
                        textTransform: "uppercase", letterSpacing: "0.15em", marginTop: 2 }}>
            MongoDB Atlas POC
          </div>
        </div>
      </div>

      {/* Nav */}
      {NAV.map((grp) => (
        <div key={grp.section} style={{ marginBottom: 6 }}>
          <Overline style={{ color: T.text3, padding: "12px 4px 4px", display: "block",
                             letterSpacing: "0.16em" }}>{grp.section}</Overline>
          {grp.items.map((it) => {
            const on = active === it.tab;
            return (
              <div key={it.label} onClick={() => onSelect(it.tab)}
                style={{
                  display: "flex", alignItems: "center", gap: 10, padding: "8px 12px",
                  borderRadius: "0 6px 6px 0", cursor: "pointer", marginBottom: 2,
                  borderLeft: `2px solid ${on ? T.green : "transparent"}`,
                  background: on ? "rgba(0,237,100,0.08)" : "transparent",
                  color: on ? T.green : T.text2, fontWeight: on ? 600 : 400, fontSize: 13,
                  transition: "background .15s",
                }}>
                <span style={{ fontSize: 14, opacity: on ? 1 : 0.55 }}>{it.icon}</span>
                <span>{it.label}</span>
              </div>
            );
          })}
        </div>
      ))}

      <div style={{ height: 1, background: T.border, margin: "8px 0 12px" }} />

      {/* Collections */}
      <Overline style={{ color: T.text3, marginBottom: 8, letterSpacing: "0.16em" }}>Collections</Overline>
      {Object.entries(collections).map(([name, count], i) => (
        <div key={name} style={{
          display: "flex", justifyContent: "space-between", alignItems: "center",
          background: T.surface, border: `1px solid rgba(0,237,100,0.07)`,
          borderRadius: 5, padding: "8px 10px", marginBottom: 4,
        }}>
          <span style={{ fontFamily: T.mono, fontSize: 11, color: COL_COLORS[i % 3], fontWeight: 500 }}>{name}</span>
          <span style={{ fontFamily: T.mono, fontSize: 10, color: T.text3 }}>{fmtCount(count)}</span>
        </div>
      ))}

      {/* Índices */}
      <Overline style={{ color: T.text3, margin: "12px 0 8px", letterSpacing: "0.16em" }}>Índices Ativos</Overline>
      {indices.map((idx) => (
        <div key={idx.name} style={{
          background: T.surface, border: `1px solid rgba(0,237,100,0.07)`,
          borderRadius: 5, padding: "8px 10px", marginBottom: 4,
        }}>
          <div style={{ fontFamily: T.mono, fontSize: 11, color: T.green, fontWeight: 500 }}>{idx.name}</div>
          <div style={{ display: "flex", alignItems: "center", gap: 5, fontSize: 10, color: T.text3, marginTop: 2 }}>
            <span style={{ width: 5, height: 5, borderRadius: "50%", background: T.green,
                           boxShadow: `0 0 4px ${T.green}`, display: "inline-block" }} />
            {idx.type} · {idx.status}
          </div>
        </div>
      ))}

      {/* Cluster pill */}
      <div style={{ marginTop: "auto", paddingTop: 16 }}>
        <div style={{ background: "rgba(0,237,100,0.06)", border: `1px solid rgba(0,237,100,0.18)`,
                      borderRadius: 6, padding: "10px 12px" }}>
          <div style={{ fontSize: 9, color: T.text3, textTransform: "uppercase",
                        letterSpacing: "0.14em", marginBottom: 5 }}>Cluster</div>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <span style={{ fontFamily: T.mono, fontSize: 13, fontWeight: 700, color: T.green }}>POC</span>
            <span style={{ display: "flex", alignItems: "center", gap: 5, fontSize: 11, color: T.green, fontWeight: 600 }}>
              <span style={{ width: 6, height: 6, borderRadius: "50%", background: T.green,
                             boxShadow: `0 0 6px ${T.green}` }} />Online
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
