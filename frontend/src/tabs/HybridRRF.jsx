import { useState } from "react";
import TextInput from "@leafygreen-ui/text-input";
import Button from "@leafygreen-ui/button";
import Badge from "@leafygreen-ui/badge";
import Banner from "@leafygreen-ui/banner";
import { H3, Body, Subtitle, InlineCode } from "@leafygreen-ui/typography";
import { hybrid } from "../api";
import { T } from "../theme";
import ProductTable, { priceCol } from "../components/ProductTable";

function Slider({ label, value, onChange, min, max, help }) {
  return (
    <div style={{ flex: 1 }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
        <span style={{ fontSize: 12, color: T.text2 }} title={help}>{label}</span>
        <span style={{ fontSize: 12, color: T.green, fontFamily: T.mono }}>{value}</span>
      </div>
      <input type="range" min={min} max={max} value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        style={{ width: "100%", accentColor: T.green }} />
    </div>
  );
}

export default function HybridRRF() {
  const [q, setQ] = useState("");
  const [k, setK] = useState(60);
  const [nS, setNS] = useState(20);
  const [nV, setNV] = useState(20);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  const run = async () => {
    if (!q.trim()) return;
    setLoading(true);
    try { setData(await hybrid({ query: q, k, n_search: nS, n_vector: nV })); }
    finally { setLoading(false); }
  };

  const cols = [
    { key: "nome", label: "Produto", color: T.text },
    priceCol(),
    { key: "rrf", label: "Score RRF", mono: true, color: T.green },
    { key: "rank_search", label: "Rank Search", mono: true, align: "center", render: (r) => r.rank_search ?? "—" },
    { key: "rank_vector", label: "Rank Vector", mono: true, align: "center", render: (r) => r.rank_vector ?? "—" },
    { key: "both", label: "Nos dois", align: "center", render: (r) => (r.both ? "🏆" : "") },
  ];

  return (
    <div>
      <H3 style={{ color: T.text }}>Hybrid Search — Reciprocal Rank Fusion</H3>
      <Body style={{ color: T.text2, marginBottom: 6 }}>
        Combina Atlas Search + Vector Search num único ranking. <InlineCode darkMode>score = Σ 1/(k + rank)</InlineCode>
      </Body>

      <div style={{ display: "flex", gap: 12, alignItems: "flex-end", margin: "12px 0" }}>
        <div style={{ flex: 1 }}>
          <TextInput aria-label="Consulta Hybrid" placeholder="tênis de corrida, fone sem fio…"
            value={q} onChange={(e) => setQ(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && run()} darkMode />
        </div>
        <Button variant="primary" onClick={run} disabled={loading} darkMode>
          {loading ? "Fundindo…" : "Buscar"}
        </Button>
      </div>

      <div style={{ display: "flex", gap: 20, marginBottom: 16 }}>
        <Slider label="k (constante RRF)" value={k} onChange={setK} min={10} max={100}
          help="Suavização do RRF. Padrão da literatura: 60." />
        <Slider label="Resultados Search" value={nS} onChange={setNS} min={10} max={50}
          help="Quantos resultados o Atlas Search contribui." />
        <Slider label="Resultados Vector" value={nV} onChange={setNV} min={10} max={50}
          help="Quantos resultados o Vector Search contribui." />
      </div>

      {!data && (
        <div style={{ textAlign: "center", padding: "28px 0", color: T.text3 }}>
          <div style={{ fontSize: 30, marginBottom: 8 }}>🔀</div>
          <Subtitle style={{ color: T.text }}>Digite uma consulta para ver a fusão</Subtitle>
          <Body style={{ color: T.text3, marginTop: 4 }}>Itens nos dois rankings 🏆 sobem ao topo.</Body>
        </div>
      )}

      {data?.error && <Banner variant="danger" darkMode>{data.error}</Banner>}

      {data?.fused?.length > 0 && (
        <>
          <div style={{ display: "flex", gap: 8, marginBottom: 14, flexWrap: "wrap" }}>
            <Badge variant="green">Atlas Search {data.counts.n_search}</Badge>
            <Badge variant="blue">Vector {data.counts.n_vector}</Badge>
            <Badge variant="darkgray">Fusão {data.fused.length}</Badge>
            <Badge variant="lightgray">⏱ {data.elapsed_ms} ms</Badge>
            <Badge variant="yellow">🏆 nos dois: {data.counts.both}</Badge>
          </div>
          <ProductTable rows={data.fused} columns={cols} />

          {/* Mini chart de scores */}
          <Subtitle style={{ color: T.text, margin: "20px 0 10px", fontSize: 14 }}>Score por produto — Top 10</Subtitle>
          {data.fused.slice(0, 10).map((x, i) => {
            const max = Math.max(...data.fused.map((f) => f.rrf)) || 1;
            return (
              <div key={i} style={{ display: "flex", alignItems: "center", gap: 10, margin: "5px 0" }}>
                <span style={{ width: 200, fontSize: 12, color: T.text2, overflow: "hidden",
                               textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{x.nome}</span>
                <div style={{ flex: 1, display: "flex", height: 14, borderRadius: 3, overflow: "hidden", background: "rgba(255,255,255,0.05)" }}>
                  <div title={`Search ${x.s_score}`} style={{ width: `${(x.s_score / max) * 100}%`, background: T.greenDark }} />
                  <div title={`Vector ${x.v_score}`} style={{ width: `${(x.v_score / max) * 100}%`, background: T.blue }} />
                </div>
                <span style={{ width: 60, fontSize: 11, color: T.green, fontFamily: T.mono, textAlign: "right" }}>{x.rrf}</span>
              </div>
            );
          })}
          <div style={{ display: "flex", gap: 16, marginTop: 8, fontSize: 11, color: T.text3 }}>
            <span><span style={{ color: T.greenDark }}>■</span> Atlas Search</span>
            <span><span style={{ color: T.blue }}>■</span> Vector Search</span>
          </div>
        </>
      )}
    </div>
  );
}
