import { T, fmtBRL } from "../theme";

// Tabela de produtos consistente, usada em todas as abas
export default function ProductTable({ rows, columns }) {
  if (!rows || rows.length === 0) {
    return <div style={{ color: T.text3, fontSize: 13, padding: "12px 4px" }}>Sem resultados.</div>;
  }
  return (
    <div style={{ border: `1px solid ${T.border}`, borderRadius: 8, overflow: "hidden" }}>
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr style={{ background: "#002A40" }}>
            {columns.map((c) => (
              <th key={c.key} style={{
                textAlign: c.align || "left", padding: "9px 12px", fontSize: 10, fontWeight: 700,
                color: T.text3, textTransform: "uppercase", letterSpacing: "0.08em",
                borderBottom: `1px solid ${T.border}`,
              }}>{c.label}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={i} style={{ borderBottom: `1px solid ${T.borderSub}` }}>
              {columns.map((c) => (
                <td key={c.key} style={{
                  textAlign: c.align || "left", padding: "9px 12px", fontSize: 12,
                  color: c.color || T.text2, fontFamily: c.mono ? T.mono : T.font,
                }}>
                  {c.render ? c.render(r) : r[c.key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function priceCol() {
  return { key: "preco", label: "Preço", mono: true, color: T.text, render: (r) => fmtBRL(r.preco) };
}

export function MqlBlock({ pipeline, collection }) {
  return (
    <details style={{ marginTop: 14, background: T.surface, border: `1px solid ${T.border}`, borderRadius: 8 }}>
      <summary style={{ cursor: "pointer", padding: "10px 14px", fontSize: 13, color: T.text2, listStyle: "none" }}>
        🔧 Pipeline MQL executado no MongoDB {collection ? `· ${collection}` : ""}
      </summary>
      <pre style={{ margin: 0, padding: 14, borderTop: `1px solid ${T.border}`, overflow: "auto",
                    fontSize: 12, color: T.green, fontFamily: T.mono, maxHeight: 320 }}>
        {JSON.stringify(pipeline, null, 2)}
      </pre>
    </details>
  );
}
