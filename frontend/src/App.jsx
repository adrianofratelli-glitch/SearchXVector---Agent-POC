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
      <div style={{ display: "flex", minHeight: "100vh", background: T.bg }}>
        <Sidebar active={tab} onSelect={setTab} stats={stats} />

        <div style={{ flex: 1, padding: "0 28px 40px", maxWidth: 1320 }}>
          {/* Header */}
          <div style={{ display: "flex", alignItems: "center", gap: 13, flexWrap: "wrap",
                        padding: "18px 0 14px", borderBottom: `1px solid ${T.border}`, marginBottom: 18 }}>
            <Leaf size={24} />
            <span style={{ fontFamily: "'MongoDB Value Serif', Georgia, serif", fontSize: 23,
                           fontWeight: 700, color: T.text, letterSpacing: "-0.015em" }}>
              Marketplace × MongoDB Atlas
            </span>
            <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
              {PILLS.map((p) => (
                <span key={p.label} style={{ fontSize: 10, fontWeight: 700, padding: "3px 10px",
                  borderRadius: 4, border: `1px solid ${p.color}44`, background: `${p.color}1A`,
                  color: p.color, textTransform: "uppercase", letterSpacing: "0.07em" }}>{p.label}</span>
              ))}
            </div>
            <div style={{ marginLeft: "auto", fontSize: 12, color: T.text3, fontFamily: T.mono }}>
              {offline ? "⚠ backend offline" : "db: POC · voyage-4 autoEmbed · LangGraph ReAct"}
            </div>
          </div>

          {offline && (
            <div style={{ background: "rgba(255,105,96,0.1)", border: `1px solid ${T.red}44`,
                          borderRadius: 8, padding: 16, color: T.red, marginBottom: 18 }}>
              Backend não respondeu em <code>http://localhost:8000</code>. Rode{" "}
              <code>uvicorn main:app --port 8000</code> dentro de <code>backend/</code>.
            </div>
          )}

          {/* KPIs */}
          <div style={{ display: "flex", gap: 14, marginBottom: 20 }}>
            <KpiCard label="Documentos" value={fmtCount(c.produtos)} sub="produtos indexados" color="green" />
            <KpiCard label="Vetores Indexados" value={fmtCount(c.produtos_vector)} sub="embeddings · voyage-4" color="blue" />
            <KpiCard label="Avaliações" value={fmtCount(c.avaliacoes)} sub="reviews p/ o AI Agent" color="purple" />
            <KpiCard label="Índices Ativos" value="2" sub="Atlas Search + Vector · READY" color="teal" />
          </div>

          {/* Tabs */}
          <Tabs aria-label="Funcionalidades" selected={tab} setSelected={setTab} darkMode>
            <Tab name="🔍 Atlas Search"><div style={{ paddingTop: 18 }}><AtlasSearch /></div></Tab>
            <Tab name="⚡ Search vs Vector"><div style={{ paddingTop: 18 }}><SearchVsVector /></div></Tab>
            <Tab name="🔀 Hybrid RRF"><div style={{ paddingTop: 18 }}><HybridRRF /></div></Tab>
            <Tab name="🎯 Similares"><div style={{ paddingTop: 18 }}><Similares /></div></Tab>
            <Tab name="📊 Analytics"><div style={{ paddingTop: 18 }}><Analytics /></div></Tab>
            <Tab name="💬 Reviews RAG"><div style={{ paddingTop: 18 }}><ReviewsRag /></div></Tab>
            <Tab name="🤖 AI Agent"><div style={{ paddingTop: 18 }}><AiAgent /></div></Tab>
          </Tabs>
        </div>
      </div>
    </LeafyGreenProvider>
  );
}
