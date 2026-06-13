import { useState, useEffect } from "react";
import LeafyGreenProvider from "@leafygreen-ui/leafygreen-provider";
import { Tabs, Tab } from "@leafygreen-ui/tabs";
import { getStats } from "./api";
import { T, fmtCount } from "./theme";
import Sidebar from "./components/Sidebar";
import KpiCard from "./components/KpiCard";
import Leaf from "./components/Leaf";
import AtlasSearch from "./tabs/AtlasSearch";
import SearchVsVector from "./tabs/SearchVsVector";
import HybridRRF from "./tabs/HybridRRF";
import AiAgent from "./tabs/AiAgent";
import Analytics from "./tabs/Analytics";
import Similares from "./tabs/Similares";
import ReviewsRag from "./tabs/ReviewsRag";

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
    getStats().then(setStats).catch(() => setOffline(true));
  }, []);

  const c = stats?.collections || {};

  return (
    <LeafyGreenProvider darkMode>
      <div style={{ display: "flex", minHeight: "100vh" }}>
        <Sidebar active={tab} onSelect={setTab} stats={stats} offline={offline} />

        <div style={{ flex: 1, padding: "0 28px 40px", maxWidth: 1320 }}>
          {/* Header */}
          <div style={{ padding: "26px 0 18px", borderBottom: `1px solid ${T.border}`, marginBottom: 20 }}>
            <div className="kicker" style={{ marginBottom: 10 }}>MongoDB Atlas · Proof of Concept</div>
            <div style={{ display: "flex", alignItems: "center", gap: 14, flexWrap: "wrap" }}>
              <Leaf size={28} />
              <span style={{ fontSize: 34, fontWeight: 800, color: T.text,
                             letterSpacing: "-0.04em", lineHeight: 1.05 }}>
                Marketplace <span style={{ color: T.green }}>×</span> Atlas Search
              </span>
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
              Backend não respondeu em <code>http://localhost:8200</code>. Rode{" "}
              <code>bash start.sh</code> na raiz, ou <code>uvicorn main:app --port 8200</code> dentro de <code>backend/</code>.
            </div>
          )}

          {/* KPIs — segmented stat-bar, pitch style */}
          <div className="stat-bar" style={{ marginBottom: 22 }}>
            <KpiCard label="Documentos" value={fmtCount(c.produtos)} sub="produtos indexados" color="green" />
            <KpiCard label="Vetores Indexados" value={fmtCount(c.produtos_vector)} sub="embeddings · voyage-4" color="blue" />
            <KpiCard label="Avaliações" value={fmtCount(c.avaliacoes)} sub="reviews p/ o AI Agent" color="purple" />
            <KpiCard label="Índices Ativos" value="2" sub="Atlas Search + Vector · READY" color="teal" />
          </div>

          {/* Tabs */}
          <Tabs aria-label="Funcionalidades" value={tab} onValueChange={setTab} darkMode>
            <Tab name="🔍 Atlas Search"><div className="fade-up" style={{ paddingTop: 18 }}><AtlasSearch /></div></Tab>
            <Tab name="⚡ Search vs Vector"><div className="fade-up" style={{ paddingTop: 18 }}><SearchVsVector /></div></Tab>
            <Tab name="🔀 Hybrid RRF"><div className="fade-up" style={{ paddingTop: 18 }}><HybridRRF /></div></Tab>
            <Tab name="🎯 Similares"><div className="fade-up" style={{ paddingTop: 18 }}><Similares /></div></Tab>
            <Tab name="📊 Analytics"><div className="fade-up" style={{ paddingTop: 18 }}><Analytics /></div></Tab>
            <Tab name="💬 Reviews RAG"><div className="fade-up" style={{ paddingTop: 18 }}><ReviewsRag /></div></Tab>
            <Tab name="🤖 AI Agent"><div className="fade-up" style={{ paddingTop: 18 }}><AiAgent /></div></Tab>
          </Tabs>
        </div>
      </div>
    </LeafyGreenProvider>
  );
}
