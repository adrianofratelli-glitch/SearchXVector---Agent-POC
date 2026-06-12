import { useState } from "react";
import TextInput from "@leafygreen-ui/text-input";
import Button from "@leafygreen-ui/button";
import Badge from "@leafygreen-ui/badge";
import Banner from "@leafygreen-ui/banner";
import Toggle from "@leafygreen-ui/toggle";
import { H3, Body, Subtitle } from "@leafygreen-ui/typography";
import { search } from "../api";
import { T, fmtBRL } from "../theme";
import ProductTable, { priceCol, MqlBlock } from "../components/ProductTable";

// destaca o prefixo digitado (demonstra autocomplete)
function highlight(text, q) {
  if (!text || !q) return text;
  const i = text.toLowerCase().indexOf(q.toLowerCase());
  if (i < 0) return text;
  return (<>{text.slice(0, i)}<b style={{ color: T.green }}>{text.slice(i, i + q.length)}</b>{text.slice(i + q.length)}</>);
}

export default function AtlasSearch() {
  const [q, setQ] = useState("");
  const [synonyms, setSynonyms] = useState(false);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  const run = async () => {
    if (loading || !q.trim()) return;
    setLoading(true);
    try { setData(await search({ query: q, synonyms })); }
    catch (e) { setData({ error: `Falha na busca: ${e.message}` }); }
    finally { setLoading(false); }
  };

  const cols = [
    { key: "nome", label: "Produto", color: T.text, render: (r) => highlight(r.nome, q) },
    priceCol(),
    { key: "categoria", label: "Categoria" },
    { key: "avaliacao_media", label: "Avaliação", render: (r) => `⭐ ${(r.avaliacao_media || 0).toFixed(1)}` },
    { key: "em_estoque", label: "Estoque", align: "center", render: (r) => (r.em_estoque ? "✅" : "❌") },
  ];

  return (
    <div>
      <div className="section-label">Atlas Search · Full-Text</div>
      <H3 id="atlas-search-title" style={{ color: T.text, fontFamily: T.font, letterSpacing: "-0.02em" }}>Busca Inteligente de Produtos</H3>
      <Body style={{ color: T.text2, marginBottom: 16 }}>
        Autocomplete, fuzzy matching e highlight ao vivo — como um e-commerce real.
      </Body>

      <div style={{ display: "flex", gap: 12, alignItems: "flex-end", marginBottom: 8 }}>
        <div style={{ flex: 1 }}>
          <TextInput aria-labelledby="atlas-search-title" placeholder="Nike, notebook, adidass, samsumg…"
            value={q} onChange={(e) => setQ(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && run()} darkMode sizeVariant="default" />
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 8, paddingBottom: 6 }}>
          <Toggle checked={synonyms} onChange={setSynonyms} aria-label="Sinônimos" size="small" darkMode />
          <Body style={{ color: T.text2, fontSize: 13 }}>Sinônimos</Body>
        </div>
        <Button variant="primary" onClick={run} disabled={loading} darkMode>
          {loading ? "Buscando…" : "🔍 Buscar"}
        </Button>
      </div>

      {!data && (
        <div style={{ textAlign: "center", padding: "30px 0", color: T.text3 }}>
          <div style={{ fontSize: 30, marginBottom: 8 }}>🔍</div>
          <Subtitle style={{ color: T.text }}>Busque um produto para começar</Subtitle>
          <Body style={{ color: T.text3, marginTop: 4 }}>
            Tente <b style={{ color: T.text2 }}>adidass</b> ou <b style={{ color: T.text2 }}>samsumg</b> (com erro) para ver o fuzzy matching.
          </Body>
        </div>
      )}

      {data?.synonyms_fallback && (
        <Banner variant="warning" darkMode style={{ marginTop: 12 }}>
          Sinônimos indisponíveis neste índice (campo usa analyzer <code>lucene.portuguese</code>). Exibindo resultados sem sinônimos.
        </Banner>
      )}

      {data?.error && <Banner variant="danger" darkMode style={{ marginTop: 12 }}>{data.error}</Banner>}

      {data?.results?.length > 0 && (
        <>
          <div style={{ display: "flex", gap: 8, margin: "14px 0", flexWrap: "wrap" }}>
            <Badge variant="green">{data.total_matches?.toLocaleString("pt-BR")} no índice</Badge>
            <Badge variant="blue">{data.results.length} exibidos</Badge>
            <Badge variant="lightgray">⏱ {data.elapsed_ms} ms</Badge>
            <Badge variant="lightgray">Menor {fmtBRL(Math.min(...data.results.map((r) => r.preco)))}</Badge>
            <Badge variant="lightgray">Maior {fmtBRL(Math.max(...data.results.map((r) => r.preco)))}</Badge>
          </div>
          <ProductTable rows={data.results.slice(0, 30)} columns={cols} />
          <MqlBlock pipeline={data.pipeline} collection="POC.produtos" />
        </>
      )}
    </div>
  );
}
