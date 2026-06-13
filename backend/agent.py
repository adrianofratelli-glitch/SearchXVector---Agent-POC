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

from atlas import db, safe_aggregate, _client, DB_NAME

llm = ChatAnthropic(model="claude-sonnet-4-6", temperature=0)


# ── Tools ────────────────────────────────────────────────────────────────────
@tool
def busca_semantica(consulta: str) -> str:
    """Busca produtos por similaridade semântica. Use para: 'academia em casa',
    'presente para o dia dos pais', 'home office', etc."""
    results, err = safe_aggregate("produtos_vector", [
        {"$vectorSearch": {"index": "produtos_vector", "path": "descricao", "query": consulta,
                           "numCandidates": 150, "limit": 10}},
        {"$project": {"nome": 1, "marca": 1, "categoria": 1, "preco": 1,
                      "avaliacao_media": 1, "score": {"$meta": "vectorSearchScore"}}},
    ])
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
    results, err = safe_aggregate("produtos", [
        {"$search": {"index": "produtos_search",
                     "autocomplete": {"query": nome, "path": "nome", "fuzzy": {"maxEdits": 1}}}},
        {"$limit": 10},
        {"$project": {"nome": 1, "marca": 1, "categoria": 1, "preco": 1,
                      "avaliacao_media": 1, "em_estoque": 1, "score": {"$meta": "searchScore"}}},
    ])
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
    results, err = safe_aggregate("produtos", [
        {"$match": {"categoria": categoria, "em_estoque": True}},
        {"$sort": {"avaliacao_media": -1, "total_avaliacoes": -1}},
        {"$limit": limite},
        {"$project": {"nome": 1, "marca": 1, "preco": 1, "avaliacao_media": 1, "total_avaliacoes": 1}},
    ])
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
    results, err = safe_aggregate("produtos", [
        {"$match": {"categoria": categoria, "em_estoque": True,
                    "preco": {"$gte": preco_min, "$lte": preco_max}}},
        {"$sort": {"avaliacao_media": -1}},
        {"$limit": 10},
        {"$project": {"nome": 1, "marca": 1, "preco": 1, "avaliacao_media": 1}},
    ])
    if err:
        return f"Erro: {err}"
    if not results:
        return f"Nenhum produto em {categoria} entre R$ {preco_min:.0f} e R$ {preco_max:.0f}."
    return f"Produtos em {categoria} entre R$ {preco_min:.0f}–{preco_max:.0f}:\n" + "\n".join(
        f"- {r['nome']} | R$ {r['preco']:.2f} | ⭐ {r['avaliacao_media']:.1f}" for r in results)


# ── MQL reconstruction for the trace ─────────────────────────────────────────
TOOL_META = {
    "busca_semantica":         {"engine": "Vector Search", "collection": "produtos_vector"},
    "buscar_produto":          {"engine": "Atlas Search",  "collection": "produtos"},
    "comparar_categoria":      {"engine": "Aggregation",   "collection": "produtos"},
    "produtos_por_faixa_preco":{"engine": "Aggregation",   "collection": "produtos"},
}

def reconstruct_mql(tool_name: str, args: dict) -> list:
    if tool_name == "busca_semantica":
        return [
            {"$vectorSearch": {"index": "produtos_vector", "path": "descricao",
                               "query": args.get("consulta", ""), "numCandidates": 150, "limit": 10}},
            {"$project": {"nome": 1, "preco": 1, "categoria": 1, "score": {"$meta": "vectorSearchScore"}}},
        ]
    if tool_name == "buscar_produto":
        return [
            {"$search": {"index": "produtos_search",
                         "autocomplete": {"query": args.get("nome", ""), "path": "nome", "fuzzy": {"maxEdits": 1}}}},
            {"$limit": 10},
            {"$project": {"nome": 1, "preco": 1, "em_estoque": 1, "score": {"$meta": "searchScore"}}},
        ]
    if tool_name == "comparar_categoria":
        return [
            {"$match": {"categoria": args.get("categoria", ""), "em_estoque": True}},
            {"$sort": {"avaliacao_media": -1, "total_avaliacoes": -1}},
            {"$limit": args.get("limite", 10)},
            {"$project": {"nome": 1, "preco": 1, "avaliacao_media": 1}},
        ]
    if tool_name == "produtos_por_faixa_preco":
        return [
            {"$match": {"categoria": args.get("categoria", ""), "em_estoque": True,
                        "preco": {"$gte": args.get("preco_min", 0), "$lte": args.get("preco_max", 0)}}},
            {"$sort": {"avaliacao_media": -1}}, {"$limit": 10},
            {"$project": {"nome": 1, "preco": 1, "avaliacao_media": 1}},
        ]
    return []


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
            trace.append({
                "tool": info["name"], "args": info["args"],
                "engine": meta["engine"], "collection": meta["collection"],
                "mql": reconstruct_mql(info["name"], info["args"]),
                "result": str(m.content)[:600],
            })
    return {"answer": answer, "trace": trace}
