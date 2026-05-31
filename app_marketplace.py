import os
import uuid
import json
import time
import warnings
import streamlit as st
import pandas as pd
from pymongo import MongoClient
from pymongo.errors import PyMongoError, ExecutionTimeout
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.mongodb import MongoDBSaver

# Console limpo — esconde warnings de deprecation do LangGraph/LangChain
warnings.filterwarnings("ignore")

load_dotenv(override=True)

MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME     = os.getenv("DB_NAME", "POC")

st.set_page_config(page_title="Marketplace × MongoDB Atlas", page_icon="🛒", layout="wide")

# ══════════════════════════════════════════════════════════════════
# MONGODB THEME
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #001E2B; color: #FFFFFF; }
    section[data-testid="stSidebar"] { background-color: #00141C; }
    .stTabs [data-baseweb="tab-list"] { background-color: #00283A; border-radius: 8px; padding: 4px; gap: 4px; }
    .stTabs [data-baseweb="tab"] { background-color: transparent; color: #B8C4C2; border-radius: 6px; font-weight: 500; padding: 8px 16px; }
    .stTabs [aria-selected="true"] { background-color: #00ED64 !important; color: #001E2B !important; font-weight: 700; }
    .stButton > button { background-color: #00ED64; color: #001E2B; font-weight: 700; border: none; border-radius: 6px; }
    .stButton > button:hover { background-color: #00BA4A; color: #001E2B; border: none; }
    .stFormSubmitButton > button { background-color: #00ED64 !important; color: #001E2B !important; font-weight: 700 !important; border: none !important; border-radius: 6px !important; }
    .stTextInput > div > div > input { background-color: #00283A; color: #FFFFFF; border: 1px solid #00684A; border-radius: 6px; }
    .stTextInput > div > div > input:focus { border-color: #00ED64; box-shadow: 0 0 0 1px #00ED64; }
    .stTextArea textarea { background-color: #00283A !important; color: #00ED64 !important; border: 1px solid #00684A !important; border-radius: 6px !important; font-family: 'Courier New', monospace !important; font-size: 13px !important; }
    .stSelectbox > div > div, .stMultiSelect > div > div { background-color: #00283A; border: 1px solid #00684A; border-radius: 6px; }
    [data-testid="metric-container"] { background-color: #00283A; border: 1px solid #00684A; border-radius: 8px; padding: 12px 16px; }
    [data-testid="metric-container"] label { color: #B8C4C2 !important; }
    [data-testid="metric-container"] [data-testid="stMetricValue"] { color: #00ED64 !important; font-weight: 700; }
    .stDataFrame { border: 1px solid #00684A; border-radius: 8px; }
    .streamlit-expanderHeader { background-color: #00283A !important; color: #00ED64 !important; border-radius: 6px !important; font-weight: 600 !important; }
    .streamlit-expanderContent { background-color: #00283A !important; border: 1px solid #00684A !important; }
    hr { border-color: #00684A; }
    h1 { color: #00ED64 !important; font-weight: 700; }
    h2, h3 { color: #FFFFFF !important; }
    code { background-color: #00283A; color: #00ED64; border-radius: 4px; }
    .mongo-badge { background-color: #00ED64; color: #001E2B; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 700; }
    .status-ok { color: #00ED64; font-weight: 600; }
    .status-bad { color: #FF6B6B; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# INIT — com validação de conexão
# ══════════════════════════════════════════════════════════════════
@st.cache_resource
def init_resources():
    mongo = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    mongo.admin.command("ping")  # valida conexão
    llm   = ChatAnthropic(model="claude-haiku-4-5", temperature=0)
    return mongo, llm

try:
    mongo_client, llm = init_resources()
    db = mongo_client[DB_NAME]
    CONNECTED = True
except Exception as e:
    CONNECTED = False
    st.error(f"❌ Não foi possível conectar ao MongoDB ou inicializar o LLM.\n\nDetalhe: {e}")
    st.info("Verifique o arquivo `.env` — MONGODB_URI, DB_NAME e ANTHROPIC_API_KEY.")
    st.stop()

# ══════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════
def render_highlight(text, query):
    if not text or not query:
        return text
    idx = text.upper().find(query.upper())
    if idx == -1:
        return text
    match = text[idx:idx+len(query)]
    return text[:idx] + f"<b style='color:#00ED64;font-weight:bold;'>{match}</b>" + text[idx+len(query):]

QUERY_TIMEOUT_MS = 10_000  # mata qualquer operação que passe de 10s

def safe_aggregate(collection, pipeline):
    """Executa aggregate com tratamento de erro amigável. Retorna (results, error)."""
    try:
        return list(db[collection].aggregate(pipeline, maxTimeMS=QUERY_TIMEOUT_MS)), None
    except ExecutionTimeout:
        return None, (
            "⏱ Operação cancelada — tempo limite de 10s atingido. "
            "Tente reduzir o volume de resultados, refinar os filtros ou verificar os índices."
        )
    except PyMongoError as e:
        msg = str(e)
        if "index not found" in msg.lower() or "no such index" in msg.lower():
            return None, "Índice não encontrado. Verifique se o Search/Vector index existe e está READY no Atlas UI."
        if "mongot" in msg.lower():
            return None, "O Atlas Search está reiniciando (mongot). Aguarde 1-2 min e tente novamente."
        return None, msg
    except Exception as e:
        return None, str(e)

def show_mql_editor(pipeline: list, collection: str, key: str):
    with st.expander("🔧 Pipeline MQL — Ver & Editar", expanded=False):
        st.caption(f"Collection: `{DB_NAME}.{collection}` — edite o JSON e clique em Executar")
        edited = st.text_area(
            "Pipeline", value=json.dumps(pipeline, indent=2, ensure_ascii=False, default=str),
            height=260, key=f"mql_{key}", label_visibility="collapsed"
        )
        col_btn, _ = st.columns([1, 4])
        with col_btn:
            run = st.button("▶ Executar", key=f"run_{key}", use_container_width=True)
        if run:
            try:
                custom = json.loads(edited)
            except json.JSONDecodeError as e:
                st.error(f"JSON inválido: {e}")
                return
            t0 = time.time()
            results, err = safe_aggregate(collection, custom)
            elapsed = (time.time() - t0) * 1000
            if err:
                st.error(f"Erro: {err}")
            else:
                st.success(f"✅  {len(results)} documentos em **{elapsed:.0f} ms**")
                if results:
                    st.dataframe(
                        pd.DataFrame([{k: v for k, v in r.items() if k != "_id"} for r in results[:20]]),
                        use_container_width=True, hide_index=True
                    )

def show_searchmeta(search_op: dict):
    """Contagem de facets em tempo real com $searchMeta — usa o mesmo operador do $search principal."""
    meta_pipeline = [{"$searchMeta": {
        "index": "produtos_search",
        "facet": {
            "operator": search_op,
            "facets": {
                "categorias":   {"type": "string", "path": "categoria", "numBuckets": 10},
                "faixas_preco": {"type": "number", "path": "preco",
                                 "boundaries": [0, 100, 500, 1000, 3000, 5000, 10000, 15000]}
            }
        }
    }}]

    meta, err = safe_aggregate("produtos", meta_pipeline)
    if err or not meta:
        if err:
            st.caption(f"⚠️ $searchMeta indisponível: {err}")
        return

    data     = meta[0]
    total    = data.get("count", {}).get("lowerBound", 0)
    facets   = data.get("facet", {})
    cat_bkts = facets.get("categorias", {}).get("buckets", [])
    prc_bkts = facets.get("faixas_preco", {}).get("buckets", [])

    with st.expander(f"📊 $searchMeta — Facets em tempo real ({total:,} resultados)", expanded=True):
        col_cat, col_prc = st.columns(2)
        with col_cat:
            st.markdown("**Por Categoria**")
            if cat_bkts:
                mx = max(b["count"] for b in cat_bkts) or 1
                for b in cat_bkts:
                    pct = b["count"] / mx
                    st.markdown(
                        f"<div style='display:flex;align-items:center;gap:8px;margin:4px 0;'>"
                        f"<span style='width:160px;font-size:12px;color:#B8C4C2;'>{b['_id']}</span>"
                        f"<div style='flex:1;background:#00283A;border-radius:4px;height:8px;'>"
                        f"<div style='width:{pct*100:.0f}%;background:#00ED64;border-radius:4px;height:8px;'></div></div>"
                        f"<span style='width:50px;font-size:12px;color:#00ED64;text-align:right;'>{b['count']:,}</span>"
                        f"</div>", unsafe_allow_html=True
                    )
            else:
                st.caption("Sem dados de categoria.")
        with col_prc:
            st.markdown("**Por Faixa de Preço**")
            if prc_bkts:
                labels = ["R$ 0–100","R$ 100–500","R$ 500–1K","R$ 1K–3K","R$ 3K–5K","R$ 5K–10K","R$ 10K–15K"]
                mx = max(b["count"] for b in prc_bkts) or 1
                for i, b in enumerate(prc_bkts):
                    pct   = b["count"] / mx
                    label = labels[i] if i < len(labels) else f"Faixa {i+1}"
                    st.markdown(
                        f"<div style='display:flex;align-items:center;gap:8px;margin:4px 0;'>"
                        f"<span style='width:100px;font-size:12px;color:#B8C4C2;'>{label}</span>"
                        f"<div style='flex:1;background:#00283A;border-radius:4px;height:8px;'>"
                        f"<div style='width:{pct*100:.0f}%;background:#00684A;border-radius:4px;height:8px;'></div></div>"
                        f"<span style='width:50px;font-size:12px;color:#B8C4C2;text-align:right;'>{b['count']:,}</span>"
                        f"</div>", unsafe_allow_html=True
                    )
            else:
                st.caption("Sem dados de preço.")

def show_explain(pipeline: list, collection: str, key: str):
    """Explain visual do plano de execução."""
    with st.expander("🔬 Explain — Plano de Execução", expanded=False):
        col_btn, _ = st.columns([1, 4])
        with col_btn:
            run = st.button("Gerar Explain", key=f"explain_{key}", use_container_width=True)
        if run:
            try:
                t0 = time.time()
                result = db.command(
                    "explain",
                    {"aggregate": collection, "pipeline": pipeline, "cursor": {}},
                    verbosity="queryPlanner"
                )
                elapsed = (time.time() - t0) * 1000
                st.caption(f"⏱ Explain gerado em {elapsed:.0f} ms")

                stages = result.get("stages")
                if not stages:
                    qp = result.get("queryPlanner", {})
                    stages = [{"$cursor": qp}] if qp else [{"pipeline": "n/a"}]

                st.markdown("**Pipeline de execução:**")
                for i, stage in enumerate(stages):
                    stage_name = list(stage.keys())[0] if stage else "unknown"
                    clean = stage_name.replace("$_internalSearchMongotRemote", "$search (mongot)")
                    clean = clean.replace("$_internalSearchIdLookup", "$search idLookup")
                    color = "#00ED64" if ("search" in clean.lower() or "vector" in clean.lower()) else "#00684A"
                    st.markdown(
                        f"<div style='background:{color}22;border-left:3px solid {color};"
                        f"padding:8px 12px;border-radius:0 6px 6px 0;margin:4px 0;"
                        f"font-family:monospace;font-size:13px;color:#FFFFFF;'>"
                        f"<b style='color:{color};'>Stage {i+1}:</b> {clean}"
                        f"</div>", unsafe_allow_html=True
                    )

                st.divider()
                with st.expander("📄 JSON completo do Explain", expanded=False):
                    st.code(json.dumps(result, indent=2, default=str), language="json")
            except Exception as e:
                st.warning(
                    "Explain detalhado é limitado para pipelines com $search/$vectorSearch no Atlas. "
                    f"Detalhe: {e}"
                )

# ══════════════════════════════════════════════════════════════════
# TOOLS — AI Agent
# ══════════════════════════════════════════════════════════════════
@tool
def busca_semantica(consulta: str) -> str:
    """Busca produtos por similaridade semântica. Use para: 'academia em casa',
    'presente para o dia dos pais', 'home office', etc."""
    results, err = safe_aggregate("produtos_vector", [
        {"$vectorSearch": {"index": "produtos_vector", "path": "descricao", "query": consulta,
                           "numCandidates": 150, "limit": 10}},
        {"$project": {"nome": 1, "marca": 1, "categoria": 1, "preco": 1,
                      "avaliacao_media": 1, "score": {"$meta": "vectorSearchScore"}}}
    ])
    if err:
        return f"Erro na busca semântica: {err}"
    if not results:
        return "Nenhum produto encontrado."
    return "\n".join([
        f"- {r['nome']} | R$ {r['preco']:.2f} | {r['categoria']} | ⭐ {r.get('avaliacao_media',0):.1f} | score:{r.get('score',0):.3f}"
        for r in results
    ])

@tool
def buscar_produto(nome: str) -> str:
    """Busca produtos pelo nome usando Atlas Search full-text com fuzzy matching."""
    results, err = safe_aggregate("produtos", [
        {"$search": {"index": "produtos_search",
                     "autocomplete": {"query": nome, "path": "nome", "fuzzy": {"maxEdits": 1}}}},
        {"$limit": 10},
        {"$project": {"nome": 1, "marca": 1, "categoria": 1, "preco": 1,
                      "avaliacao_media": 1, "em_estoque": 1, "score": {"$meta": "searchScore"}}}
    ])
    if err:
        return f"Erro na busca: {err}"
    if not results:
        return f"Nenhum produto encontrado para '{nome}'."
    return "\n".join([
        f"- {r['nome']} | R$ {r['preco']:.2f} | {'✅' if r.get('em_estoque') else '❌'} | ⭐ {r.get('avaliacao_media',0):.1f}"
        for r in results
    ])

@tool
def comparar_categoria(categoria: str, limite: int = 10) -> str:
    """Retorna os produtos mais bem avaliados de uma categoria."""
    results, err = safe_aggregate("produtos", [
        {"$match": {"categoria": categoria, "em_estoque": True}},
        {"$sort": {"avaliacao_media": -1, "total_avaliacoes": -1}},
        {"$limit": limite},
        {"$project": {"nome": 1, "marca": 1, "preco": 1, "avaliacao_media": 1, "total_avaliacoes": 1}}
    ])
    if err:
        return f"Erro: {err}"
    if not results:
        return f"Categoria '{categoria}' não encontrada."
    return f"Top {limite} em {categoria}:\n" + "\n".join([
        f"{i+1}. {r['nome']} | R$ {r['preco']:.2f} | ⭐ {r['avaliacao_media']:.1f} ({r['total_avaliacoes']:,} avaliações)"
        for i, r in enumerate(results)
    ])

@tool
def produtos_por_faixa_preco(categoria: str, preco_min: float, preco_max: float) -> str:
    """Busca produtos em uma categoria dentro de uma faixa de preço específica."""
    results, err = safe_aggregate("produtos", [
        {"$match": {"categoria": categoria, "em_estoque": True,
                    "preco": {"$gte": preco_min, "$lte": preco_max}}},
        {"$sort": {"avaliacao_media": -1}},
        {"$limit": 10},
        {"$project": {"nome": 1, "marca": 1, "preco": 1, "avaliacao_media": 1}}
    ])
    if err:
        return f"Erro: {err}"
    if not results:
        return f"Nenhum produto em {categoria} entre R$ {preco_min:.0f} e R$ {preco_max:.0f}."
    return f"Produtos em {categoria} entre R$ {preco_min:.0f}–{preco_max:.0f}:\n" + "\n".join([
        f"- {r['nome']} | R$ {r['preco']:.2f} | ⭐ {r['avaliacao_media']:.1f}" for r in results
    ])

SYSTEM_PROMPT = """Você é um assistente especialista em recomendações de produtos de um marketplace.
Responda SEMPRE em português brasileiro de forma concisa e objetiva.
Use as ferramentas disponíveis para buscar dados reais antes de responder.
Ao apresentar preços, use o formato R$ X.XXX,XX.
Sempre mencione avaliações e se o produto está em estoque ao recomendar."""

@st.cache_resource
def build_agent():
    checkpointer = MongoDBSaver(mongo_client, db_name=DB_NAME)
    return create_react_agent(
        llm,
        [busca_semantica, buscar_produto, comparar_categoria, produtos_por_faixa_preco],
        checkpointer=checkpointer, prompt=SYSTEM_PROMPT
    )

agent_executor = build_agent()

# ══════════════════════════════════════════════════════════════════
# SIDEBAR — Status do Cluster
# ══════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### 🍃 Status do Cluster")
    st.markdown(f"**Database:** `{DB_NAME}`")
    st.markdown(f"**Conexão:** <span class='status-ok'>● Online</span>", unsafe_allow_html=True)
    st.divider()
    st.markdown("**Collections**")
    try:
        for col in ["produtos", "produtos_vector", "avaliacoes"]:
            cnt = db[col].estimated_document_count()
            st.markdown(f"`{col}` — {cnt:,} docs")
    except Exception:
        st.caption("Não foi possível contar os documentos.")
    st.divider()
    st.markdown("**Índices necessários**")
    st.markdown("`produtos_search` — Atlas Search")
    st.markdown("`produtos_vector` — Vector Search")
    st.caption("Confirme que ambos estão READY no Atlas UI.")

# ══════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<h1 style='margin-bottom:0'>🛒 Marketplace × MongoDB Atlas</h1>
<p style='color:#B8C4C2;margin-top:4px;'>
    <span class='mongo-badge'>Atlas Search</span>&nbsp;
    <span class='mongo-badge'>Vector Search</span>&nbsp;
    <span class='mongo-badge'>Hybrid RRF</span>&nbsp;
    <span class='mongo-badge'>AI Agent</span>&nbsp;
    <span style='color:#5C7080;font-size:13px;margin-left:8px;'>5M docs · voyage-4 autoEmbed · LangGraph ReAct</span>
</p>
""", unsafe_allow_html=True)
st.divider()

tab_search, tab_compare, tab_rrf, tab_agent = st.tabs([
    "🔍 Atlas Search", "⚡ Search vs Vector", "🔀 Hybrid RRF", "🤖 AI Agent"
])

# ══════════════════════════════════════════════════════════════════
# TAB 1 — Atlas Search
# ══════════════════════════════════════════════════════════════════
with tab_search:
    st.subheader("Busca Inteligente de Produtos")
    st.write("**Autocomplete**, **fuzzy matching**, **facets**, **sinônimos** e **explain** ao vivo.")

    with st.form("search_form"):
        col_q, col_sort, col_stock = st.columns([3, 1.5, 1.2])
        with col_q:
            search_query = st.text_input(
                "Busca", placeholder="🔍  Nike, notebook, adidass, samsumg...",
                label_visibility="collapsed"
            )
        with col_sort:
            sort_by = st.selectbox("Ordenar por",
                ["Relevância", "Menor Preço", "Maior Preço", "Melhor Avaliação"],
                label_visibility="collapsed")
        with col_stock:
            only_stock = st.checkbox("Só em estoque", value=True)

        col_cat, col_price, col_syn = st.columns([2, 2, 1])
        with col_cat:
            cat_filter = st.multiselect("Categoria", [
                "Eletrônicos", "Esportes & Fitness", "Moda & Estilo",
                "Casa & Cozinha", "Beleza & Saúde", "Pets", "Livros & Cultura"
            ])
        with col_price:
            price_range = st.slider("Faixa de preço (R$)", 0, 15000, (0, 15000), step=100)
        with col_syn:
            use_synonyms = st.toggle("🔤 Sinônimos", value=False,
                help="Ativa sinônimos: 'notebook'→'laptop', 'tênis'→'calçado', 'celular'→'smartphone'")

        submitted = st.form_submit_button("🔍 Buscar", use_container_width=True)

    if submitted and search_query:
        mql_filter = {"preco": {"$gte": price_range[0], "$lte": price_range[1]}}
        if only_stock:
            mql_filter["em_estoque"] = True
        if cat_filter:
            mql_filter["categoria"] = {"$in": cat_filter}

        # synonyms NÃO pode coexistir com fuzzy no mesmo operador
        if use_synonyms:
            search_op = {"text": {"query": search_query, "path": ["nome", "descricao"], "synonyms": "sinonimos_produtos"}}
        else:
            # compound: autocomplete em nome (boost) + text em descricao
            # assim "notebook" acha produtos mesmo sem a palavra no nome
            search_op = {
                "compound": {
                    "should": [
                        {"autocomplete": {"query": search_query, "path": "nome",
                                          "fuzzy": {"maxEdits": 1},
                                          "score": {"boost": {"value": 2}}}},
                        {"text": {"query": search_query, "path": "descricao",
                                  "fuzzy": {"maxEdits": 1}}}
                    ],
                    "minimumShouldMatch": 1
                }
            }

        pipeline = [
            {"$search": {"index": "produtos_search", **search_op}},
            {"$match": mql_filter},
            {"$limit": 50},
            {"$project": {
                "nome": 1, "marca": 1, "categoria": 1, "subcategoria": 1,
                "preco": 1, "preco_original": 1, "desconto_pct": 1,
                "avaliacao_media": 1, "total_avaliacoes": 1,
                "em_estoque": 1, "score": {"$meta": "searchScore"}
            }}
        ]

        t0 = time.time()
        results, err = safe_aggregate("produtos", pipeline)
        elapsed = (time.time() - t0) * 1000

        if err:
            st.error(f"Erro na busca: {err}")
        elif results:
            if sort_by == "Menor Preço":
                results.sort(key=lambda x: x.get("preco", 0))
            elif sort_by == "Maior Preço":
                results.sort(key=lambda x: x.get("preco", 0), reverse=True)
            elif sort_by == "Melhor Avaliação":
                results.sort(key=lambda x: x.get("avaliacao_media", 0), reverse=True)

            prices = [r.get("preco", 0) for r in results]
            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("Resultados",  f"{len(results):,}")
            m2.metric("Menor Preço", f"R$ {min(prices):,.2f}")
            m3.metric("Maior Preço", f"R$ {max(prices):,.2f}")
            m4.metric("Preço Médio", f"R$ {sum(prices)/len(prices):,.2f}")
            m5.metric("Latência",    f"{elapsed:.0f} ms")

            if use_synonyms:
                st.info("🔤 **Sinônimos ativos** — ex: 'notebook' expande para 'laptop', 'computador'", icon="✅")

            st.divider()
            show_searchmeta(search_op)
            st.divider()

            st.markdown(
                "<div style='display:grid;grid-template-columns:3fr 1fr 1fr 1fr 1fr;"
                "font-weight:600;padding:6px 0;border-bottom:1px solid #00684A;"
                "color:#B8C4C2;font-size:13px;'>"
                "<span>Produto</span><span>Preço</span><span>Categoria</span>"
                "<span>Avaliação</span><span>Estoque</span></div>",
                unsafe_allow_html=True
            )
            for r in results[:30]:
                nome_hl   = render_highlight(r.get("nome", ""), search_query)
                preco     = r.get("preco", 0)
                desc      = r.get("desconto_pct")
                preco_str = f"R$ {preco:,.2f}"
                if desc:
                    preco_str += f" <small style='color:#00ED64'>-{desc}%</small>"
                c1, c2, c3, c4, c5 = st.columns([3, 1, 1, 1, 1])
                c1.markdown(nome_hl, unsafe_allow_html=True)
                c2.markdown(preco_str, unsafe_allow_html=True)
                c3.write(r.get("subcategoria", r.get("categoria", "")))
                c4.write(f"⭐ {r.get('avaliacao_media', 0):.1f} ({r.get('total_avaliacoes', 0):,})")
                c5.write("✅" if r.get("em_estoque") else "❌")

            st.divider()
            # salva para o explain funcionar após rerender
            st.session_state["s1_pipeline"] = pipeline
            st.session_state["s1_query"]    = search_query
        elif not err:
            st.info("Nenhum resultado encontrado para os filtros aplicados.")
            st.session_state["s1_pipeline"] = pipeline
            st.session_state["s1_query"]    = search_query

    # MQL editor + Explain ficam FORA do if submitted — persistem entre rerenders
    if "s1_pipeline" in st.session_state:
        col_mql, col_exp = st.columns(2)
        with col_mql:
            show_mql_editor(st.session_state["s1_pipeline"], "produtos",
                            f"s1_{st.session_state.get('s1_query','')}")
        with col_exp:
            show_explain(st.session_state["s1_pipeline"], "produtos",
                         f"s1_{st.session_state.get('s1_query','')}")

# ══════════════════════════════════════════════════════════════════
# TAB 2 — Search vs Vector
# ══════════════════════════════════════════════════════════════════
with tab_compare:
    st.subheader("Atlas Search vs Vector Search — lado a lado")
    st.write("Compare busca por **palavra-chave** com busca por **significado semântico**.")

    compare_query = st.text_input(
        "Consulta", placeholder="ex: academia em casa, presente dia dos pais, home office...",
        key="compare", label_visibility="collapsed"
    )
    st.info(
        "💡 Tente *'academia em casa'* — Atlas Search (frase exata) retorna zero; "
        "Vector Search retorna halteres, whey, kettlebell pelo significado.", icon="🔍"
    )

    if compare_query:
        # phrase só em nome → queries conceituais retornam ZERO no search
        # (nomes de produto não contêm "academia em casa", "home office", etc.)
        # isso cria o gap dramático que o vector search preenche
        search_pipeline = [
            {"$search": {"index": "produtos_search",
                         "phrase": {"query": compare_query, "path": "nome"}}},
            {"$limit": 8},
            {"$project": {"nome": 1, "marca": 1, "categoria": 1, "preco": 1,
                          "avaliacao_media": 1, "score": {"$meta": "searchScore"}}}
        ]
        vector_pipeline = [
            {"$vectorSearch": {"index": "produtos_vector", "path": "descricao",
                               "query": compare_query, "numCandidates": 150, "limit": 8}},
            {"$project": {"nome": 1, "marca": 1, "categoria": 1, "preco": 1,
                          "avaliacao_media": 1, "score": {"$meta": "vectorSearchScore"}}}
        ]

        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown("### 🔤 Atlas Search\n*Encontra onde a frase aparece literalmente*")
            t0 = time.time()
            text_res, err = safe_aggregate("produtos", search_pipeline)
            elapsed = (time.time() - t0) * 1000
            if err:
                st.error(f"Erro: {err}")
            else:
                st.caption(f"⏱ {elapsed:.0f} ms · {len(text_res)} resultados")
                if text_res:
                    st.dataframe(pd.DataFrame([{
                        "Produto": r["nome"], "Categoria": r.get("categoria",""),
                        "Preço": f"R$ {r['preco']:,.2f}", "⭐": f"{r.get('avaliacao_media',0):.1f}",
                        "Score": round(r.get("score",0), 3)
                    } for r in text_res]), use_container_width=True, hide_index=True)
                else:
                    st.warning("⚠️ Sem resultados — a frase não existe nos documentos.")

        with col_r:
            st.markdown("### 🧠 Vector Search\n*Encontra pelo significado, mesmo sem a palavra exata*")
            t0 = time.time()
            vec_res, err = safe_aggregate("produtos_vector", vector_pipeline)
            elapsed = (time.time() - t0) * 1000
            if err:
                st.error(f"Erro: {err}")
            else:
                st.caption(f"⏱ {elapsed:.0f} ms · {len(vec_res)} resultados")
                if vec_res:
                    st.dataframe(pd.DataFrame([{
                        "Produto": r["nome"], "Categoria": r.get("categoria",""),
                        "Preço": f"R$ {r['preco']:,.2f}", "⭐": f"{r.get('avaliacao_media',0):.1f}",
                        "Score": round(r.get("score",0), 4)
                    } for r in vec_res]), use_container_width=True, hide_index=True)
                else:
                    st.info("Sem resultados semânticos.")

        st.divider()
        col_sl, col_vl = st.columns(2)
        with col_sl:
            show_mql_editor(search_pipeline, "produtos", f"cmp_s_{compare_query}")
        with col_vl:
            show_mql_editor(vector_pipeline, "produtos_vector", f"cmp_v_{compare_query}")

# ══════════════════════════════════════════════════════════════════
# TAB 3 — Hybrid RRF
# ══════════════════════════════════════════════════════════════════
with tab_rrf:
    st.subheader("Hybrid Search — Reciprocal Rank Fusion (RRF)")
    st.write("Combina **Atlas Search** + **Vector Search** em um único ranking via RRF.")
    st.markdown("> `score_rrf = Σ 1 / (k + rank_i)` &nbsp; onde `k = 60`  \n"
                "Produtos nos **dois rankings** somam score de ambos — ganham no topo. 🏆")

    rrf_query = st.text_input(
        "Consulta Hybrid", placeholder="ex: tênis de corrida, fone sem fio, cadeira gamer...",
        key="rrf", label_visibility="collapsed"
    )
    col_k1, col_k2, col_k3 = st.columns(3)
    with col_k1: rrf_k    = st.slider("k (RRF constant)", 10, 100, 60)
    with col_k2: n_search = st.slider("Resultados Search", 10, 50, 20)
    with col_k3: n_vector = st.slider("Resultados Vector", 10, 50, 20)

    if rrf_query:
        s_pipe = [
            {"$search": {"index": "produtos_search", "compound": {"should": [
                {"autocomplete": {"query": rrf_query, "path": "nome",
                                  "fuzzy": {"maxEdits": 1}, "score": {"boost": {"value": 3}}}},
                {"text": {"query": rrf_query, "path": "descricao", "fuzzy": {"maxEdits": 1}}}
            ]}}},
            {"$limit": n_search},
            {"$project": {"nome": 1, "marca": 1, "categoria": 1, "preco": 1,
                          "avaliacao_media": 1, "search_score": {"$meta": "searchScore"}}}
        ]
        v_pipe = [
            {"$vectorSearch": {"index": "produtos_vector", "path": "descricao",
                               "query": rrf_query, "numCandidates": n_vector * 10, "limit": n_vector}},
            {"$project": {"nome": 1, "marca": 1, "categoria": 1, "preco": 1,
                          "avaliacao_media": 1, "vector_score": {"$meta": "vectorSearchScore"}}}
        ]

        t0 = time.time()
        search_res, err_s = safe_aggregate("produtos", s_pipe)
        vector_res, err_v = safe_aggregate("produtos_vector", v_pipe)
        elapsed = (time.time() - t0) * 1000

        if err_s or err_v:
            st.error(f"Erro: {err_s or err_v}")
        else:
            rrf_scores = {}
            for rank, doc in enumerate(search_res):
                k = doc["nome"]
                rrf_scores.setdefault(k, {"doc": doc, "rrf": 0, "search_rank": None, "vector_rank": None})
                rrf_scores[k]["rrf"] += 1 / (rrf_k + rank + 1)
                rrf_scores[k]["search_rank"] = rank + 1
            for rank, doc in enumerate(vector_res):
                k = doc["nome"]
                rrf_scores.setdefault(k, {"doc": doc, "rrf": 0, "search_rank": None, "vector_rank": None})
                rrf_scores[k]["rrf"] += 1 / (rrf_k + rank + 1)
                rrf_scores[k]["vector_rank"] = rank + 1

            fused = sorted(rrf_scores.values(), key=lambda x: x["rrf"], reverse=True)[:20]

            if fused:
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Atlas Search",  len(search_res))
                m2.metric("Vector Search", len(vector_res))
                m3.metric("Fusão RRF",     len(fused))
                m4.metric("Latência",      f"{elapsed:.0f} ms")

                st.caption(
                    "ℹ️ O Vector Search retorna itens **semanticamente próximos**. "
                    "Exemplo: 'academia' em português tem dois significados — *gym* e *instituição acadêmica* — "
                    "então o vetorial pode trazer livros junto com equipamentos fitness. "
                    "Use queries mais específicas como 'academia fitness' ou 'equipamentos musculação'. "
                    "Itens marcados 🏆 apareceram nos dois rankings."
                )
                st.divider()

                rows = [{"Produto": x["doc"].get("nome",""), "Categoria": x["doc"].get("categoria",""),
                         "Preço": f"R$ {x['doc'].get('preco',0):,.2f}", "Score RRF": round(x["rrf"],5),
                         "Rank Search": x["search_rank"] or "—", "Rank Vector": x["vector_rank"] or "—",
                         "Em ambos": "🏆" if x["search_rank"] and x["vector_rank"] else ""}
                        for x in fused]
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

                only_s = sum(1 for x in fused if x["search_rank"] and not x["vector_rank"])
                only_v = sum(1 for x in fused if x["vector_rank"] and not x["search_rank"])
                both   = sum(1 for x in fused if x["search_rank"] and x["vector_rank"])
                st.divider()
                st.markdown("**Origem dos resultados:**")
                c1, c2, c3 = st.columns(3)
                c1.metric("Só Atlas Search",  only_s)
                c2.metric("Só Vector Search", only_v)
                c3.metric("Nos dois 🏆",       both)
                st.divider()
                col_sl, col_vl = st.columns(2)
                with col_sl:
                    show_mql_editor(s_pipe, "produtos", f"rrf_s_{rrf_query}")
                with col_vl:
                    show_mql_editor(v_pipe, "produtos_vector", f"rrf_v_{rrf_query}")
            else:
                st.info("Nenhum resultado encontrado.")

# ══════════════════════════════════════════════════════════════════
# TAB 4 — AI Agent
# ══════════════════════════════════════════════════════════════════
with tab_agent:
    st.subheader("Recomendações em Linguagem Natural")
    st.write("LangGraph ReAct Agent + Claude Haiku + Atlas Vector Search + MongoDB Aggregation.")
    col_i1, col_i2 = st.columns(2)
    with col_i1:
        st.info("💾 **Memória ativa** — histórico gravado em `checkpoints` por `thread_id`", icon="🧠")
    with col_i2:
        st.info("🔧 **4 ferramentas** — busca semântica, textual, por categoria e faixa de preço", icon="⚙️")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        st.session_state.thread_id    = str(uuid.uuid4())

    col_new, _ = st.columns([1, 4])
    with col_new:
        if st.button("🔄 Nova conversa", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.thread_id    = str(uuid.uuid4())
            st.rerun()

    if not st.session_state.chat_history:
        st.write("**💡 Experimente:**")
        suggestions = [
            "Me recomende um notebook para programação até R$ 3.000",
            "Qual o melhor smartphone custo-benefício até R$ 2.500?",
            "Preciso de um presente para alguém que gosta de academia",
            "Compare os melhores tênis de corrida disponíveis",
        ]
        cols = st.columns(2)
        for i, sug in enumerate(suggestions):
            if cols[i % 2].button(sug, use_container_width=True):
                st.session_state.pending_prompt = sug
        st.divider()

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    pending    = st.session_state.pop("pending_prompt", None)
    user_input = st.chat_input("Pergunte sobre produtos...") or pending

    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)
        with st.chat_message("assistant"):
            with st.spinner("🤔 Buscando produtos..."):
                try:
                    t0       = time.time()
                    response = agent_executor.invoke(
                        {"messages": [("human", user_input)]},
                        config={"configurable": {"thread_id": st.session_state.thread_id}}
                    )
                    elapsed = (time.time() - t0) * 1000
                    answer  = response["messages"][-1].content

                    # Transparência: quais ferramentas o agent chamou
                    tools_used = []
                    for m in response["messages"]:
                        tcs = getattr(m, "tool_calls", None)
                        if tcs:
                            for tc in tcs:
                                tools_used.append(tc.get("name", "?"))

                    st.write(answer)
                    cap = f"⏱ {elapsed:.0f} ms"
                    if tools_used:
                        cap += f" · 🔧 ferramentas: {', '.join(dict.fromkeys(tools_used))}"
                    st.caption(cap)
                    st.session_state.chat_history.append({"role": "assistant", "content": answer})
                except Exception as e:
                    st.error(f"Erro no agent: {e}")

    st.caption(f"Session ID: `{st.session_state.thread_id}`")
