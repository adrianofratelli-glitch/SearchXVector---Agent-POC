import os
import uuid
import streamlit as st
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.mongodb import MongoDBSaver

load_dotenv(override=True)

MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME     = os.getenv("DB_NAME")

# Config por collection
COLLECTIONS = {
    "💳 Transações": {
        "collection":    "transacoes",
        "index":         "transacoes",
        "desc_field":    "amos_mt_desc",
        "amount_field":  "amos_mt_amount",
        "cat_field":     "amos_mt_category_code",
        "extra_fields":  []
    },
    "🧾 Faturas": {
        "collection":    "fatura",
        "index":         "Fatura",
        "desc_field":    "amss_mt_desc",
        "amount_field":  "amss_mt_amount",
        "cat_field":     "amss_mt_category_code",
        "extra_fields":  ["amss_mt_rpt_desc"]
    }
}

MCC_NAMES = {
    "5300": "Atacado",       "5411": "Supermercado",  "5912": "Farmácia",
    "5942": "Eletrônicos",   "5812": "Restaurante",   "5814": "Fast Food",
    "5977": "Cosméticos",    "5999": "Varejo",        "5045": "Computadores",
    "5311": "Loja Dept.",    "5651": "Roupas",        "5661": "Calçados",
    "5732": "Eletrônicos",   "5734": "Software",      "7011": "Hotel",
    "4816": "Internet",      "5065": "Eletrônicos",   "5816": "Jogos",
    "5200": "Mat. Construção","5251": "Ferragens",
}

st.set_page_config(
    page_title="Banco Inter × MongoDB Atlas",
    page_icon="🏦",
    layout="wide"
)

@st.cache_resource
def init_resources():
    mongo = MongoClient(MONGODB_URI)
    llm   = ChatAnthropic(model="claude-sonnet-4-6", temperature=0, api_key=os.getenv("ANTHROPIC_API_KEY"))
    return mongo, llm

mongo_client, llm = init_resources()
db = mongo_client[DB_NAME]

def render_highlight(text, query):
    if not text or not query:
        return text
    idx = text.upper().find(query.upper())
    if idx == -1:
        return text
    match = text[idx:idx+len(query)]
    return (text[:idx] +
            f"<b style='color:#f97316;font-weight:bold;'>{match}</b>" +
            text[idx+len(query):])


# ── Tools ────────────────────────────────────────────────────────────
@tool
def busca_semantica(consulta: str) -> str:
    """Busca transações por similaridade semântica. Use para: 'supermercado',
    'compras online', 'tecnologia', 'restaurante', etc."""
    results = list(db.transacoes_sample.aggregate([
        {"$vectorSearch": {
            "index":        "transacoes_vector",
            "path":         "amos_mt_desc",
            "query":         consulta,
            "numCandidates": 150,
            "limit":        10
        }},
        {"$project": {
            "amos_mt_desc": 1, "amos_mt_amount": 1,
            "amos_mt_category_code": 1, "segmento": 1,
            "score": {"$meta": "vectorSearchScore"}
        }}
    ]))
    if not results:
        return "Nenhuma transação encontrada."
    return "\n".join([
        f"- {r['amos_mt_desc']} | R$ {r['amos_mt_amount']} | "
        f"seg:{r['segmento']} | score:{r.get('score', 0):.3f}"
        for r in results
    ])

@tool
def analisar_conta(numero_conta: str) -> str:
    """Analisa o perfil de gastos de uma conta pelo número da conta."""
    results = list(db.transacoes.aggregate([
        {"$match": {"account_number": numero_conta}},
        {"$group": {
            "_id":       "$amos_mt_category_code",
            "total":     {"$sum": {"$toDouble": "$amos_mt_amount"}},
            "qtd":       {"$sum": 1},
            "media":     {"$avg": {"$toDouble": "$amos_mt_amount"}}
        }},
        {"$sort": {"total": -1}},
        {"$limit": 5}
    ]))
    if not results:
        return f"Conta {numero_conta} não encontrada."
    rows = "\n".join([
        f"- Categoria {r['_id']}: R$ {r['total']:.2f} "
        f"em {r['qtd']} transações (média R$ {r['media']:.2f})"
        for r in results
    ])
    return f"Perfil da conta {numero_conta}:\n{rows}"

@tool
def top_gastos_segmento(segmento: str, quantidade: int = 10) -> str:
    """Retorna as maiores transações de um segmento (s1, s2, s3 ou s4)."""
    results = list(db.transacoes.aggregate([
        {"$match": {"segmento": segmento}},
        {"$addFields": {"valor": {"$toDouble": "$amos_mt_amount"}}},
        {"$sort": {"valor": -1}},
        {"$limit": quantidade},
        {"$project": {"amos_mt_desc": 1, "amos_mt_amount": 1, "account_number": 1}}
    ]))
    if not results:
        return f"Segmento {segmento} não encontrado."
    rows = "\n".join([
        f"{i+1}. {r['amos_mt_desc']} | R$ {r['amos_mt_amount']} | conta: {r['account_number']}"
        for i, r in enumerate(results)
    ])
    return f"Top {quantidade} gastos do segmento {segmento}:\n{rows}"

@tool
def buscar_por_estabelecimento(nome: str) -> str:
    """Busca transações pelo nome do estabelecimento usando Atlas Search full-text."""
    results = list(db.transacoes.aggregate([
        {"$search": {
            "index": "transacoes",
            "autocomplete": {"query": nome, "path": "amos_mt_desc", "fuzzy": {"maxEdits": 1}}
        }},
        {"$limit": 10},
        {"$project": {
            "amos_mt_desc": 1, "amos_mt_amount": 1, "segmento": 1,
            "score": {"$meta": "searchScore"}
        }}
    ]))
    if not results:
        return f"Nenhuma transação para '{nome}'."
    return "\n".join([
        f"- {r['amos_mt_desc']} | R$ {r['amos_mt_amount']} | seg:{r['segmento']}"
        for r in results
    ])

# ── Agent ────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """Você é um assistente especialista em análise de dados financeiros do Banco Inter.
Responda SEMPRE em português brasileiro de forma concisa e objetiva.
Use as ferramentas disponíveis para buscar dados reais antes de responder.
Ao apresentar valores monetários, use o formato R$ X.XXX,XX."""

checkpointer   = MongoDBSaver(mongo_client, db_name="banco_inter")
agent_executor = create_react_agent(
    llm,
    [busca_semantica, analisar_conta, top_gastos_segmento, buscar_por_estabelecimento],
    checkpointer=checkpointer,
    prompt=SYSTEM_PROMPT
)

# ── UI ───────────────────────────────────────────────────────────────
st.title("🏦 Banco Inter × MongoDB Atlas")
st.caption("Demo técnica — Atlas Search + AI Agent sobre dados transacionais reais")

tab_search, tab_compare, tab_agent = st.tabs([
    "🔍 Atlas Search", "⚡ Search vs Vector", "🤖 AI Agent"
])

# ═══════════════════════════════════════════════════════════════════
# Tab 1: Atlas Search (Transações + Faturas)
# ═══════════════════════════════════════════════════════════════════
with tab_search:
    st.subheader("Busca Inteligente em Transações e Faturas")
    st.write("Full-text search com **highlight**, **facets**, **fuzzy matching** e **ordenação**.")

    col_q, col_col, col_sort = st.columns([3, 1.2, 1.2])
    with col_q:
        search_query = st.text_input(
            "Busca", placeholder="🔍  shopee, atacadista, farmácia...",
            label_visibility="collapsed"
        )
    with col_col:
        col_choice = st.selectbox("Collection", list(COLLECTIONS.keys()))
    with col_sort:
        sort_by = st.selectbox("Ordenar por", ["Relevância", "Maior Valor", "Menor Valor"])

    cfg = COLLECTIONS[col_choice]

    if search_query:
        # ── Facets ──
        try:
            facet_data = list(db[cfg["collection"]].aggregate([
                {"$searchMeta": {
                    "index": cfg["index"],
                    "facet": {
                        "operator": {
                            "autocomplete": {"query": search_query, "path": cfg["desc_field"]}
                        },
                        "facets": {
                            "segFacet": {"type": "string", "path": "segmento", "numBuckets": 10},
                            "catFacet": {"type": "string", "path": cfg["cat_field"], "numBuckets": 10}
                        }
                    }
                }}
            ]))
            facet_counts = {}
            cat_counts   = {}
            if facet_data:
                for b in facet_data[0].get("facet", {}).get("segFacet", {}).get("buckets", []):
                    facet_counts[b["_id"]] = b["count"]
                for b in facet_data[0].get("facet", {}).get("catFacet", {}).get("buckets", []):
                    cat_counts[b["_id"]] = b["count"]
        except Exception:
            facet_counts = {}
            cat_counts   = {}

        # Facets display
        if facet_counts:
            st.write("**Resultados por segmento:**")
            fcols = st.columns(len(facet_counts))
            for i, (seg, cnt) in enumerate(sorted(facet_counts.items())):
                fcols[i].metric(seg.upper(), f"{cnt:,}")

        seg_options = ["Todos"] + [
            f"{k}  ({v:,})" for k, v in sorted(facet_counts.items())
        ]
        seg_raw    = st.selectbox("Filtrar segmento", seg_options)
        seg_filter = seg_raw.split(" ")[0] if seg_raw != "Todos" else "Todos"

        # ── Busca principal ──
        project_fields = {
            cfg["desc_field"]: 1, cfg["amount_field"]: 1,
            cfg["cat_field"]: 1, "segmento": 1,
            "score":      {"$meta": "searchScore"},
        }
        for f in cfg["extra_fields"]:
            project_fields[f] = 1

        pipeline = [
            {"$search": {
                "index": cfg["index"],
                "autocomplete": {
                    "query": search_query,
                    "path":  cfg["desc_field"],
                    "fuzzy": {"maxEdits": 1}
                },
                "highlight": {"path": cfg["desc_field"]}
            }},
            {"$limit": 100},
            {"$project": project_fields}
        ]
        if seg_filter != "Todos":
            pipeline.append({"$match": {"segmento": seg_filter}})

        try:
            results = list(db[cfg["collection"]].aggregate(pipeline))

            if sort_by == "Maior Valor":
                results.sort(key=lambda x: float(x.get(cfg["amount_field"], 0)), reverse=True)
            elif sort_by == "Menor Valor":
                results.sort(key=lambda x: float(x.get(cfg["amount_field"], 0)))

            if results:
                amounts = [float(r.get(cfg["amount_field"], 0)) for r in results]
                m1, m2, m3 = st.columns(3)
                m1.metric("Resultados",   f"{len(results):,}")
                m2.metric("Volume Total", f"R$ {sum(amounts):,.2f}")
                m3.metric("Ticket Médio", f"R$ {sum(amounts)/len(amounts):,.2f}")

                st.divider()

                # Header
                has_extra = len(cfg["extra_fields"]) > 0
                if has_extra:
                    st.markdown(
                        "<div style='display:grid;grid-template-columns:2.5fr 1.5fr 1fr 1fr 1fr;"
                        "font-weight:bold;padding:6px 0;border-bottom:1px solid #444;'>"
                        "<span>Estabelecimento</span><span>Descrição</span>"
                        "<span>Valor</span><span>Categoria</span><span>Segmento</span></div>",
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        "<div style='display:grid;grid-template-columns:3fr 1fr 1fr 1fr;"
                        "font-weight:bold;padding:6px 0;border-bottom:1px solid #444;'>"
                        "<span>Estabelecimento</span><span>Valor</span>"
                        "<span>Categoria</span><span>Segmento</span></div>",
                        unsafe_allow_html=True
                    )

                for r in results[:30]:
                    name     = render_highlight(r.get(cfg["desc_field"], ""), search_query)
                    cat_code = r.get(cfg["cat_field"], "")
                    cat_name = MCC_NAMES.get(cat_code, cat_code)
                    amount   = float(r.get(cfg["amount_field"], 0))
                    seg      = r.get("segmento", "")

                    if has_extra:
                        extra_val = r.get(cfg["extra_fields"][0], "") if cfg["extra_fields"] else ""
                        c1, c2, c3, c4, c5 = st.columns([2.5, 1.5, 1, 1, 1])
                        c1.markdown(name, unsafe_allow_html=True)
                        c2.write(extra_val)
                        c3.write(f"R$ {amount:,.2f}")
                        c4.write(cat_name)
                        c5.write(seg)
                    else:
                        c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
                        c1.markdown(name, unsafe_allow_html=True)
                        c2.write(f"R$ {amount:,.2f}")
                        c3.write(cat_name)
                        c4.write(seg)
            else:
                st.info("Nenhum resultado encontrado.")
        except Exception as e:
            st.error(f"Erro na busca: {e}")

# ═══════════════════════════════════════════════════════════════════
# Tab 2: Search vs Vector
# ═══════════════════════════════════════════════════════════════════
with tab_compare:
    st.subheader("Atlas Search vs Vector Search — lado a lado")
    st.write("Compare busca por **palavra-chave** com busca por **significado semântico**.")

    compare_query = st.text_input(
        "Consulta", placeholder="ex: alimentação, compras online, tecnologia...",
        key="compare", label_visibility="collapsed"
    )

    if compare_query:
        col_l, col_r = st.columns(2)

        with col_l:
            st.markdown("### 🔤 Atlas Search\n*Encontra onde a palavra aparece literalmente*")
            try:
                text_res = list(db.transacoes.aggregate([
                    {"$search": {
                        "index": "transacoes",
                        "autocomplete": {
                            "query": compare_query,
                            "path":  "amos_mt_desc",
                            "fuzzy": {"maxEdits": 1}
                        }
                    }},
                    {"$limit": 8},
                    {"$project": {
                        "amos_mt_desc": 1, "amos_mt_amount": 1,
                        "segmento": 1, "score": {"$meta": "searchScore"}
                    }}
                ]))
                if text_res:
                    st.dataframe(pd.DataFrame([{
                        "Estabelecimento": r["amos_mt_desc"],
                        "Valor":    f"R$ {float(r['amos_mt_amount']):,.2f}",
                        "Segmento": r.get("segmento", ""),
                        "Score":    round(r.get("score", 0), 3)
                    } for r in text_res]), use_container_width=True, hide_index=True)
                else:
                    st.info("Sem resultados para essa palavra.")
            except Exception as e:
                st.error(f"Erro: {e}")

        with col_r:
            st.markdown("### 🧠 Vector Search\n*Encontra pelo significado, mesmo sem a palavra exata*")
            try:
                vec_res = list(db.transacoes_sample.aggregate([
                    {"$vectorSearch": {
                        "index":         "transacoes_vector",
                        "path":          "amos_mt_desc",
                        "query":          compare_query,
                        "numCandidates": 150,
                        "limit":         8
                    }},
                    {"$project": {
                        "amos_mt_desc": 1, "amos_mt_amount": 1,
                        "segmento": 1, "score": {"$meta": "vectorSearchScore"}
                    }}
                ]))
                if vec_res:
                    st.dataframe(pd.DataFrame([{
                        "Estabelecimento": r["amos_mt_desc"],
                        "Valor":    f"R$ {float(r['amos_mt_amount']):,.2f}",
                        "Segmento": r.get("segmento", ""),
                        "Score":    round(r.get("score", 0), 3)
                    } for r in vec_res]), use_container_width=True, hide_index=True)
                else:
                    st.info("Sem resultados semânticos.")
            except Exception as e:
                st.error(f"Erro: {e}")

        st.info(
            "💡 **Dica:** tente *'alimentação'* — Atlas Search não acha nada (palavra não existe nos dados), "
            "mas Vector Search acha SUPERMERCADO, IFOOD, ATACADISTA pelo significado.",
            icon="🔍"
        )

# ═══════════════════════════════════════════════════════════════════
# Tab 3: AI Agent
# ═══════════════════════════════════════════════════════════════════
with tab_agent:
    st.subheader("Consultas em Linguagem Natural")
    st.write("LangGraph Agent + Claude claude-sonnet-4-6 + Atlas Vector Search (voyage-4) + MongoDB.")
    st.info(
        "💾 **Memória ativa** — histórico gravado em tempo real em `banco_inter.checkpoints`",
        icon="🧠"
    )

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        st.session_state.thread_id    = str(uuid.uuid4())

    if not st.session_state.chat_history:
        st.write("**💡 Experimente:**")
        suggestions = [
            "Quais os maiores gastos do segmento s2?",
            "Me mostra o perfil do cliente 2659850271393050232",
            "Encontre transações parecidas com compras em supermercado",
            "Tem transações suspeitas acima de R$4000 no segmento s1?"
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
    user_input = st.chat_input("Pergunte sobre as transações...") or pending

    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            with st.spinner("🤔 Analisando dados..."):
                try:
                    response = agent_executor.invoke(
                        {"messages": [("human", user_input)]},
                        config={"configurable": {"thread_id": st.session_state.thread_id}}
                    )
                    answer = response["messages"][-1].content
                    st.write(answer)
                    st.session_state.chat_history.append({"role": "assistant", "content": answer})
                except Exception as e:
                    st.error(f"Erro no agent: {e}")

    st.caption(f"Session ID: `{st.session_state.thread_id}`")
