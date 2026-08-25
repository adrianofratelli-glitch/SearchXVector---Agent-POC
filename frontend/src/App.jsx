import { lazy, Suspense, useEffect, useState } from "react";
import LeafyGreenProvider from "@leafygreen-ui/leafygreen-provider";
import { getStats } from "./api";
import { T, fmtCount } from "./theme";
import Leaf from "./components/Leaf";

const AtlasSearch = lazy(() => import("./tabs/AtlasSearch"));
const SearchVsVector = lazy(() => import("./tabs/SearchVsVector"));
const HybridRRF = lazy(() => import("./tabs/HybridRRF"));
const AiAgent = lazy(() => import("./tabs/AiAgent"));
const Analytics = lazy(() => import("./tabs/Analytics"));
const Similares = lazy(() => import("./tabs/Similares"));
const ReviewsRag = lazy(() => import("./tabs/ReviewsRag"));

const TABS = [AtlasSearch, SearchVsVector, HybridRRF, Similares, Analytics, ReviewsRag, AiAgent];
const TAB_LABELS = ["Search", "Search × Vector", "Híbrida", "Similares", "Analytics", "Reviews", "Agente"];

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

  return (
    <LeafyGreenProvider darkMode>
      <div className="search-shell" data-pov-shell style={{ display: "flex", minHeight: "100vh" }}>
        <a className="pov-skip-link" href="#conteudo-principal">Pular para o conteúdo</a>
        <main id="conteudo-principal" tabIndex={-1} className="search-main" style={{ flex: 1, padding: "0 28px 40px", maxWidth: 1320, margin: "0 auto" }}>
          {/* Header */}
          <div style={{ padding: "26px 0 18px", borderBottom: `1px solid ${T.border}`, marginBottom: 20 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 14, flexWrap: "wrap" }}>
              <Leaf size={28} />
              <h1 style={{ margin: 0, fontSize: 30, fontWeight: 800, color: T.text,
                           letterSpacing: "-0.04em", lineHeight: 1.05 }}>
                Search <span style={{ color: T.green }}>×</span> Vector
              </h1>
              <div style={{ marginLeft: "auto", fontSize: 11.5, color: T.text3, fontFamily: T.mono }}>
                {offline ? "⚠ offline" : `${fmtCount(c.produtos)} docs · ${readyCount}/${indices.length || '—'} índices prontos`}
              </div>
            </div>
            <div className="search-tabs" role="navigation" aria-label="Cenários de busca">
              {TAB_LABELS.map((label, index) => (
                <button key={label} className={tab === index ? "active" : ""} aria-current={tab === index ? "page" : undefined} onClick={() => setTab(index)}>{label}</button>
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

          <div className="fade-up" key={tab}>
            <Suspense fallback={<div style={{ color: T.text2, padding: "28px 0" }}>Carregando módulo…</div>}>
              <ActiveTab />
            </Suspense>
          </div>
        </main>
      </div>
    </LeafyGreenProvider>
  );
}
