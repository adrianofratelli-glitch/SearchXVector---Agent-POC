import { useState } from "react";
import TextInput from "@leafygreen-ui/text-input";
import Button from "@leafygreen-ui/button";
import Banner from "@leafygreen-ui/banner";
import { H3, Body, Subtitle } from "@leafygreen-ui/typography";
import { compare } from "../api";
import { T } from "../theme";
import ProductTable, { priceCol } from "../components/ProductTable";

const SUGGESTIONS = ["academia em casa", "presente dia dos pais", "proteção solar rosto"];

export default function SearchVsVector() {
  const [q, setQ] = useState("");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  const run = async (query) => {
    const text = query ?? q;
    if (loading || !text.trim()) return;
    setQ(text);
    setLoading(true);
    try { setData(await compare(text)); }
    catch (e) { setData({ error: `Falha na comparação: ${e.message}` }); }
    finally { setLoading(false); }
  };

  const baseCols = [
    { key: "nome", label: "Produto", color: T.text },
    { key: "categoria", label: "Categoria" },
    priceCol(),
  ];
  const hybridCols = [
    { key: "nome", label: "Produto", color: T.text },
    priceCol(),
    { key: "rrf", label: "RRF", mono: true, color: T.green },
    { key: "both", label: "Nos dois", align: "center", render: (r) => (r.both ? "🏆" : "") },
  ];

  return (
    <div>
      <div className="section-label">Lexical vs Semântico</div>
      <H3 id="svv-title" style={{ color: T.text, fontFamily: T.font, letterSpacing: "-0.02em" }}>Atlas Search vs Vector Search</H3>
      <Body style={{ color: T.text2, marginBottom: 12 }}>
        Busca por palavra-chave vs significado semântico — lado a lado, mais a fusão RRF.
      </Body>

      <Banner variant="info" darkMode style={{ marginBottom: 12 }}>
        💡 Tente uma frase conceitual: a busca textual retorna <b>zero</b>, mas a vetorial entende o significado.
      </Banner>

      <div style={{ display: "flex", gap: 12, alignItems: "flex-end", marginBottom: 10 }}>
        <div style={{ flex: 1 }}>
          <TextInput aria-labelledby="svv-title" placeholder="academia em casa, home office…"
            value={q} onChange={(e) => setQ(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && run()} darkMode />
        </div>
        <Button variant="primary" onClick={() => run()} disabled={loading} darkMode>
          {loading ? "Comparando…" : "Comparar"}
        </Button>
      </div>

      {!data && (
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginTop: 6 }}>
          {SUGGESTIONS.map((s) => (
            <Button key={s} size="small" variant="default" darkMode onClick={() => run(s)}>{s}</Button>
          ))}
        </div>
      )}

      {data && (
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 14, marginTop: 16 }}>
          <Col title="🔤 Atlas Search" subtitle="frase literal" accent={T.green}
               count={data.search.results.length} ms={data.elapsed_ms}>
            {data.search.results.length === 0
              ? <Banner variant="warning" darkMode>Sem resultados — a frase não existe nos nomes.</Banner>
              : <ProductTable rows={data.search.results} columns={baseCols} />}
          </Col>
          <Col title="🧠 Vector Search" subtitle="significado" accent={T.blue}
               count={data.vector.results.length} ms={data.elapsed_ms}>
            <ProductTable rows={data.vector.results} columns={baseCols} />
          </Col>
          <Col title="🏆 Hybrid RRF" subtitle="fusão k=60" accent={T.purple}
               count={data.hybrid.length} ms={data.elapsed_ms}>
            <ProductTable rows={data.hybrid} columns={hybridCols} />
          </Col>
        </div>
      )}
    </div>
  );
}

function Col({ title, subtitle, accent, count, ms, children }) {
  return (
    <div>
      <div style={{ borderLeft: `2px solid ${accent}`, paddingLeft: 10, marginBottom: 10 }}>
        <Subtitle style={{ color: T.text, fontSize: 15 }}>{title}</Subtitle>
        <div style={{ fontSize: 11, color: T.text3, fontFamily: T.mono }}>{count} resultados · {ms} ms · {subtitle}</div>
      </div>
      {children}
    </div>
  );
}
