import { lazy, Suspense, useEffect, useState } from "react";
import LeafyGreenProvider from "@leafygreen-ui/leafygreen-provider";
import { getStats } from "./api";
import { T, fmtCount } from "./theme";
import Sidebar from "./components/Sidebar";
import KpiCard from "./components/KpiCard";
import Leaf from "./components/Leaf";

const AtlasSearch = lazy(() => import("./tabs/AtlasSearch"));
const SearchVsVector = lazy(() => import("./tabs/SearchVsVector"));
const HybridRRF = lazy(() => import("./tabs/HybridRRF"));
const AiAgent = lazy(() => import("./tabs/AiAgent"));
const Analytics = lazy(() => import("./tabs/Analytics"));
const Similares = lazy(() => import("./tabs/Similares"));
const ReviewsRag = lazy(() => import("./tabs/ReviewsRag"));

const TABS = [AtlasSearch, SearchVsVector, HybridRRF, Similares, Analytics, ReviewsRag, AiAgent];

const PILLS = [
  { label: "Atlas Search", color: T.green },
  { label: "Vector Search", color: T.blue },
  { label: "Hybrid RRF", color: T.purple },
  { label: "Aggregation", color: T.teal },
  { label: "RAG", color: T.yellow },
];

export default function App() {
  const [tab, setTab] = useState(0);
  const [stats, setStats] = useState(null);
  const [offline, setOffline] = useState(false);

  useEffect(() => {
    getStats()
      .then((s) => { setStats(s); setOffline(!!s.degraded); })
      .catch(() => setOffline(true));
  }, []);

  const ActiveTab = TABS[tab];
  const c = stats?.collections || {};
  const indices = stats?.indices || [];
  const readyCount = indices.filter((i) => i.status === "READY").length;
  const allReady = indices.length > 0 && readyCount === indices.length;
  const indexSub = indices.length === 0
    ? "aguardando conexão"
    : allReady ? "Search + Vector · READY"
    : indices.filter((i) => i.status !== "READY").map((i) => `${i.name}: ${i.status}`).join(" · ");

  return (
    <LeafyGreenProvider darkMode>
      <div className="search-shell" style={{ display: "flex", minHeight: "100vh" }}>
        <Sidebar active={tab} onSelect={setTab} stats={stats} offline={offline} />

        <main className="search-main" style={{ flex: 1, padding: "0 28px 40px", maxWidth: 1320 }}>
          {/* Header */}
          <div style={{ padding: "26px 0 18px", borderBottom: `1px solid ${T.border}`, marginBottom: 20 }}>
            <div className="kicker" style={{ marginBottom: 10 }}>MongoDB Atlas · Proof of Concept</div>
            <div style={{ display: "flex", alignItems: "center", gap: 14, flexWrap: "wrap" }}>
              <Leaf size={28} />
              <h1 style={{ margin: 0, fontSize: 34, fontWeight: 800, color: T.text,
                           letterSpacing: "-0.04em", lineHeight: 1.05 }}>
                Marketplace <span style={{ color: T.green }}>×</span> Atlas Search
              </h1>
              <div style={{ marginLeft: "auto", fontSize: 11.5, color: T.text3, fontFamily: T.mono }}>
                {offline ? "⚠ backend offline" : "db: POC · voyage-4 autoEmbed · LangGraph ReAct"}
              </div>
            </div>
            <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginTop: 14 }}>
              {PILLS.map((p) => (
                <span key={p.label} className="hdr-pill"
                  style={{ borderColor: `${p.color}44`, background: `${p.color}14`, color: p.color }}>
                  {p.label}
                </span>
              ))}
            </div>
          </div>

          {offline && (
            <div style={{ background: "rgba(255,105,96,0.1)", border: `1px solid ${T.red}44`,
                          borderRadius: 8, padding: 16, color: T.red, marginBottom: 18 }}>
              {stats
                ? <>Backend no ar, mas o cluster Atlas está inacessível — verifique a conexão/IP access list. Os dados abaixo estão zerados.</>
                : <>Backend não respondeu em <code>http://localhost:8200</code>. Rode{" "}
                    <code>bash start.sh</code> na raiz, ou <code>uvicorn main:app --port 8200</code> dentro de <code>backend/</code>.</>}
            </div>
          )}

          {/* KPIs — segmented stat-bar, pitch style */}
          <div className="stat-bar" style={{ marginBottom: 22 }}>
            <KpiCard label="Documentos" value={fmtCount(c.produtos)} sub="produtos indexados" color="green" />
            <KpiCard label="Vetores Indexados" value={fmtCount(c.produtos_vector)} sub="embeddings · voyage-4" color="blue" />
            <KpiCard label="Avaliações" value={fmtCount(c.avaliacoes)} sub="reviews p/ o AI Agent" color="purple" />
            <KpiCard label="Índices Ativos" value={indices.length ? `${readyCount}/${indices.length}` : "—"}
                     sub={indexSub} color={allReady || indices.length === 0 ? "teal" : "purple"} />
          </div>

          {/* Active tab — navigation lives only in the sidebar, no duplicate tab strip */}
          <div className="fade-up" key={tab} style={{ paddingTop: 18 }}>
            <Suspense fallback={<div style={{ color: T.text2, padding: "28px 0" }}>Carregando módulo…</div>}>
              <ActiveTab />
            </Suspense>
          </div>
        </main>
      </div>
    </LeafyGreenProvider>
  );
}
