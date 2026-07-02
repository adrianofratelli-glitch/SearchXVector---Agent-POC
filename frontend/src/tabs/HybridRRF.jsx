import { useState } from "react";
import TextInput from "@leafygreen-ui/text-input";
import Button from "@leafygreen-ui/button";
import Badge from "@leafygreen-ui/badge";
import Banner from "@leafygreen-ui/banner";
import { H3, Body, Subtitle, InlineCode } from "@leafygreen-ui/typography";
import { hybrid, hybridNative } from "../api";
import { T } from "../theme";
import ProductTable, { priceCol, MqlBlock } from "../components/ProductTable";

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
  const [engine, setEngine] = useState("native"); // "native" ($rankFusion) | "app" (RRF em Python)
  const [k, setK] = useState(60);
  const [nS, setNS] = useState(20);
  const [nV, setNV] = useState(20);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  const run = async (eng) => {
    const useEngine = eng ?? engine;
    if (loading || !q.trim()) return;
    setLoading(true);
    try {
      setData(useEngine === "native"
        ? await hybridNative(q)
        : await hybrid({ query: q, k, n_search: nS, n_vector: nV }));
    } catch (e) { setData({ error: `Falha na busca híbrida: ${e.message}` }); }
    finally { setLoading(false); }
  };

  const switchEngine = (eng) => {
    setEngine(eng);
    if (q.trim()) run(eng);
  };

  const cols = [
    { key: "nome", label: "Produto", color: T.text },
    priceCol(),
    { key: "rrf", label: "Score", mono: true, color: T.green },
    { key: "rank_search", label: "Rank Search", mono: true, align: "center", render: (r) => r.rank_search ?? "—" },
    { key: "rank_vector", label: "Rank Vector", mono: true, align: "center", render: (r) => r.rank_vector ?? "—" },
    { key: "both", label: "Nos dois", align: "center", render: (r) => (r.both ? "🏆" : "") },
  ];

  const isNativeResult = data?.native === true;

  return (
    <div>
      <div className="section-label">Hybrid · $rankFusion</div>
      <H3 id="hybrid-title" style={{ color: T.text, fontFamily: T.font, letterSpacing: "-0.02em" }}>Hybrid Search — Reciprocal Rank Fusion</H3>
      <Body style={{ color: T.text2, marginBottom: 6 }}>
        Combina Atlas Search + Vector Search num único ranking. <InlineCode darkMode>score = Σ 1/(k + rank)</InlineCode>
      </Body>

      <div style={{ display: "flex", gap: 12, alignItems: "flex-end", margin: "12px 0" }}>
        <div style={{ flex: 1 }}>
          <TextInput aria-labelledby="hybrid-title" placeholder="tênis de corrida, fone sem fio…"
            value={q} onChange={(e) => setQ(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && run()} darkMode />
        </div>
        <div style={{ display: "flex", borderRadius: 6, overflow: "hidden", border: `1px solid ${T.border}` }}>
          {[["native", "$rankFusion nativo"], ["app", "RRF na aplicação"]].map(([eng, label]) => (
            <button key={eng} onClick={() => switchEngine(eng)} style={{
              cursor: "pointer", fontSize: 12, fontFamily: T.font, padding: "9px 12px", border: "none",
              background: engine === eng ? "rgba(0,237,100,0.15)" : T.surface,
              color: engine === eng ? T.green : T.text3, fontWeight: engine === eng ? 700 : 400,
            }}>{label}</button>
          ))}
        </div>
        <Button variant="primary" onClick={() => run()} disabled={loading} darkMode>
          {loading ? "Fundindo…" : "Buscar"}
        </Button>
      </div>

      {engine === "app" && (
        <div style={{ display: "flex", gap: 20, marginBottom: 16 }}>
          <Slider label="k (constante RRF)" value={k} onChange={setK} min={10} max={100}
            help="Suavização do RRF. Padrão da literatura: 60." />
          <Slider label="Resultados Search" value={nS} onChange={setNS} min={10} max={50}
            help="Quantos resultados o Atlas Search contribui." />
          <Slider label="Resultados Vector" value={nV} onChange={setNV} min={10} max={50}
            help="Quantos resultados o Vector Search contribui." />
        </div>
      )}
      {engine === "native" && (
        <Body style={{ color: T.text3, fontSize: 12, marginBottom: 16 }}>
          Modo nativo: a fusão roda <b>no servidor</b>, num único aggregation stage — sem código de fusão na
          aplicação. Use o modo "RRF na aplicação" para ensinar o algoritmo com k e limites ajustáveis.
        </Body>
      )}

      {!data && (
        <div style={{ textAlign: "center", padding: "28px 0", color: T.text3 }}>
          <div style={{ fontSize: 30, marginBottom: 8 }}>🔀</div>
          <Subtitle style={{ color: T.text }}>Digite uma consulta para ver a fusão</Subtitle>
          <Body style={{ color: T.text3, marginTop: 4 }}>Itens nos dois rankings 🏆 sobem ao topo.</Body>
        </div>
      )}

      {data?.error && <Banner variant="danger" darkMode>{data.error}</Banner>}

      {engine === "native" && data && data.native === false && (
        <Banner variant="warning" darkMode style={{ marginBottom: 12 }}>{data.reason}</Banner>
      )}

      {data?.fused?.length > 0 && (
        <>
          <div style={{ display: "flex", gap: 8, marginBottom: 14, flexWrap: "wrap" }}>
            {engine === "native" && (
              <Badge variant={isNativeResult ? "green" : "yellow"}>
                {isNativeResult ? "⚙️ $rankFusion no servidor" : "fallback: RRF na aplicação"}
              </Badge>
            )}
            <Badge variant="green">Atlas Search {data.counts.n_search}</Badge>
            <Badge variant="blue">Vector {data.counts.n_vector}</Badge>
            <Badge variant="darkgray">Fusão {data.fused.length}</Badge>
            <Badge variant="lightgray">⏱ {data.elapsed_ms} ms</Badge>
            <Badge variant="yellow">🏆 nos dois: {data.counts.both}</Badge>
            {data.same_corpus === false && (
              <Badge variant="yellow">corpora distintos (crie o índice search em produtos_vector)</Badge>
            )}
          </div>
          <ProductTable rows={data.fused} columns={cols} />

          {/* Mini score chart */}
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

          {engine === "native" && data.pipeline && (
            <MqlBlock pipeline={data.pipeline} collection="POC.produtos_vector" />
          )}
        </>
      )}
    </div>
  );
}
