"""
agent.py — LangGraph ReAct agent with four MongoDB tools.
Exposes the trace (tool → MQL → result) for the frontend to render.
The tool docstrings and system prompt stay in Portuguese, since they drive the
model's tool selection and the language of its answers.
"""

import os
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.mongodb import MongoDBSaver

from atlas import db, safe_aggregate, _client, DB_NAME, get_search_indexes

llm = ChatAnthropic(model="claude-sonnet-4-6", temperature=0)


# ── Pipeline builders — SINGLE source of truth ───────────────────────────────
# The tools execute these pipelines and the trace shows them: what the UI
# displays is byte-for-byte what ran (no separate "reconstruction" to drift).
def _pipe_busca_semantica(consulta: str) -> list:
    return [
        {"$vectorSearch": {"index": "produtos_vector", "path": "descricao", "query": consulta,
                           "numCandidates": 150, "limit": 10}},
        {"$project": {"_id": 0, "nome": 1, "marca": 1, "categoria": 1, "preco": 1,
                      "avaliacao_media": 1, "score": {"$meta": "vectorSearchScore"}}},
    ]

def _pipe_buscar_produto(nome: str) -> list:
    return [
        {"$search": {"index": "produtos_search",
                     "autocomplete": {"query": nome, "path": "nome", "fuzzy": {"maxEdits": 1}}}},
        {"$limit": 10},
        {"$project": {"_id": 0, "nome": 1, "marca": 1, "categoria": 1, "preco": 1,
                      "avaliacao_media": 1, "em_estoque": 1, "score": {"$meta": "searchScore"}}},
    ]

def _pipe_comparar_categoria(categoria: str, limite: int = 10) -> list:
    return [
        {"$match": {"categoria": categoria, "em_estoque": True}},
        {"$sort": {"avaliacao_media": -1, "total_avaliacoes": -1}},
        {"$limit": limite},
        {"$project": {"_id": 0, "nome": 1, "marca": 1, "preco": 1,
                      "avaliacao_media": 1, "total_avaliacoes": 1}},
    ]

def _pipe_produtos_por_faixa_preco(categoria: str, preco_min: float, preco_max: float) -> list:
    return [
        {"$match": {"categoria": categoria, "em_estoque": True,
                    "preco": {"$gte": preco_min, "$lte": preco_max}}},
        {"$sort": {"avaliacao_media": -1}},
        {"$limit": 10},
        {"$project": {"_id": 0, "nome": 1, "marca": 1, "preco": 1, "avaliacao_media": 1}},
    ]

def _index_ready(collection: str, name: str | None = None, vector: bool = False) -> bool:
    """Mirrors atlas.py's index-gating for the UI tabs — the agent's tools
    must degrade the same way instead of throwing a raw PyMongo error at the
    LLM when an index is missing, building, or the cluster is unreachable."""
    for ix in get_search_indexes(collection):
        is_vector = ix.get("type") == "vectorSearch"
        if is_vector != vector:
            continue
        if name and ix.get("name") != name:
            continue
        if ix.get("status") == "READY":
            return True
    return False


PIPELINE_BUILDERS = {
    "busca_semantica":          lambda a: _pipe_busca_semantica(a.get("consulta", "")),
    "buscar_produto":           lambda a: _pipe_buscar_produto(a.get("nome", "")),
    "comparar_categoria":       lambda a: _pipe_comparar_categoria(a.get("categoria", ""), a.get("limite", 10)),
    "produtos_por_faixa_preco": lambda a: _pipe_produtos_por_faixa_preco(
        a.get("categoria", ""), a.get("preco_min", 0), a.get("preco_max", 0)),
}


# ── Tools ────────────────────────────────────────────────────────────────────
@tool
def busca_semantica(consulta: str) -> str:
    """Busca produtos por similaridade semântica. Use para: 'academia em casa',
    'presente para o dia dos pais', 'home office', etc."""
    if not _index_ready("produtos_vector", vector=True):
        return "Erro: índice de busca vetorial (produtos_vector) não está pronto ou o cluster está inacessível."
    results, err = safe_aggregate("produtos_vector", _pipe_busca_semantica(consulta))
    if err:
        return f"Erro na busca semântica: {err}"
    if not results:
        return "Nenhum produto encontrado."
    return "\n".join(
        f"- {r['nome']} | R$ {r['preco']:.2f} | {r['categoria']} | ⭐ {r.get('avaliacao_media',0):.1f}"
        for r in results)


@tool
def buscar_produto(nome: str) -> str:
    """Busca produtos pelo nome usando Atlas Search full-text com fuzzy matching."""
    if not _index_ready("produtos", name="produtos_search"):
        return "Erro: índice de busca textual (produtos_search) não está pronto ou o cluster está inacessível."
    results, err = safe_aggregate("produtos", _pipe_buscar_produto(nome))
    if err:
        return f"Erro na busca: {err}"
    if not results:
        return f"Nenhum produto encontrado para '{nome}'."
    return "\n".join(
        f"- {r['nome']} | R$ {r['preco']:.2f} | {'✅' if r.get('em_estoque') else '❌'} | ⭐ {r.get('avaliacao_media',0):.1f}"
        for r in results)


@tool
def comparar_categoria(categoria: str, limite: int = 10) -> str:
    """Retorna os produtos mais bem avaliados de uma categoria."""
    results, err = safe_aggregate("produtos", _pipe_comparar_categoria(categoria, limite))
    if err:
        return f"Erro: {err}"
    if not results:
        return f"Categoria '{categoria}' não encontrada."
    return f"Top {limite} em {categoria}:\n" + "\n".join(
        f"{i+1}. {r['nome']} | R$ {r['preco']:.2f} | ⭐ {r['avaliacao_media']:.1f} ({r['total_avaliacoes']:,} avaliações)"
        for i, r in enumerate(results))


@tool
def produtos_por_faixa_preco(categoria: str, preco_min: float, preco_max: float) -> str:
    """Busca produtos em uma categoria dentro de uma faixa de preço específica."""
    results, err = safe_aggregate("produtos", _pipe_produtos_por_faixa_preco(categoria, preco_min, preco_max))
    if err:
        return f"Erro: {err}"
    if not results:
        return f"Nenhum produto em {categoria} entre R$ {preco_min:.0f} e R$ {preco_max:.0f}."
    return f"Produtos em {categoria} entre R$ {preco_min:.0f}–{preco_max:.0f}:\n" + "\n".join(
        f"- {r['nome']} | R$ {r['preco']:.2f} | ⭐ {r['avaliacao_media']:.1f}" for r in results)


# ── Trace metadata ───────────────────────────────────────────────────────────
TOOL_META = {
    "busca_semantica":         {"engine": "Vector Search", "collection": "produtos_vector"},
    "buscar_produto":          {"engine": "Atlas Search",  "collection": "produtos"},
    "comparar_categoria":      {"engine": "Aggregation",   "collection": "produtos"},
    "produtos_por_faixa_preco":{"engine": "Aggregation",   "collection": "produtos"},
}

def build_tool_pipeline(tool_name: str, args: dict) -> list:
    """The exact pipeline a tool ran for these args (same builder the tool used)."""
    builder = PIPELINE_BUILDERS.get(tool_name)
    return builder(args) if builder else []


SYSTEM_PROMPT = """Você é um assistente especialista em recomendações de produtos de um marketplace.
Responda SEMPRE em português brasileiro de forma concisa e objetiva.
Use as ferramentas disponíveis para buscar dados reais antes de responder.
Ao apresentar preços, use o formato R$ X.XXX,XX.
Sempre mencione avaliações e se o produto está em estoque ao recomendar."""

_checkpointer = MongoDBSaver(_client, db_name=DB_NAME)
_agent = create_react_agent(
    llm, [busca_semantica, buscar_produto, comparar_categoria, produtos_por_faixa_preco],
    checkpointer=_checkpointer, prompt=SYSTEM_PROMPT,
)


def run_agent(message: str, thread_id: str) -> dict:
    """Run the agent and return the answer plus a structured ReAct trace."""
    response = _agent.invoke(
        {"messages": [("human", message)]},
        config={"configurable": {"thread_id": thread_id}},
    )
    msgs = response["messages"]
    answer = msgs[-1].content
    if isinstance(answer, list):
        answer = " ".join(b.get("text", "") for b in answer if isinstance(b, dict))

    # Trace: pair each tool_call with its result
    pending, trace = {}, []
    for m in msgs:
        for tc in (getattr(m, "tool_calls", None) or []):
            pending[tc.get("id")] = {"name": tc.get("name"), "args": tc.get("args", {})}
        if m.__class__.__name__ == "ToolMessage":
            info = pending.get(getattr(m, "tool_call_id", None), {"name": getattr(m, "name", "?"), "args": {}})
            meta = TOOL_META.get(info["name"], {"engine": "Tool", "collection": "?"})
            result = str(m.content)[:600]
            # Tools return a plain string for the LLM to read (see busca_semantica /
            # buscar_produto), but the trace needs a machine-readable flag so the UI
            # can badge "degraded" instead of just showing the raw error text.
            degraded = result.startswith("Erro")
            trace.append({
                "tool": info["name"], "args": info["args"],
                "engine": meta["engine"], "collection": meta["collection"],
                "mql": build_tool_pipeline(info["name"], info["args"]),
                "result": result,
                "degraded": degraded,
                "reason": result if degraded else None,
            })
    return {"answer": answer, "trace": trace}
