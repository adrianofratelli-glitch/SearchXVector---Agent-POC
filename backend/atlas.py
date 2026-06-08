"""
atlas.py — Camada de acesso ao MongoDB Atlas.
Pipelines de Atlas Search, Vector Search, Hybrid RRF e facets,
expostos como funções puras para a API FastAPI.
"""

import os
import time
from pymongo import MongoClient
from pymongo.errors import PyMongoError, ExecutionTimeout
from dotenv import load_dotenv

# Carrega .env da raiz do projeto (autossuficiente — não depende do main.py)
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"), override=False)

MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME     = os.getenv("DB_NAME", "POC")
QUERY_TIMEOUT_MS = 10_000

_client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
db = _client[DB_NAME]  # conexão lazy — só conecta de fato na 1ª query


# ── Helper de execução segura ────────────────────────────────────────────────
def safe_aggregate(collection: str, pipeline: list):
    """Executa aggregate com tratamento de erro amigável. Retorna (results, error)."""
    try:
        return list(db[collection].aggregate(pipeline, maxTimeMS=QUERY_TIMEOUT_MS)), None
    except ExecutionTimeout:
        return None, "Operação cancelada — tempo limite de 10s atingido."
    except PyMongoError as e:
        msg = str(e)
        if "index not found" in msg.lower() or "no such index" in msg.lower():
            return None, "Índice não encontrado. Verifique se o Search/Vector index está READY no Atlas."
        if "synonym" in msg.lower():
            return None, "synonym-analyzer"  # sinalizador para fallback gracioso
        return None, msg
    except Exception as e:
        return None, str(e)


# ── Stats das collections ────────────────────────────────────────────────────
def get_stats() -> dict:
    out = {}
    for c in ["produtos", "produtos_vector", "avaliacoes"]:
        try:
            out[c] = db[c].estimated_document_count()
        except Exception:
            out[c] = 0
    return out


# ── Atlas Search (Tab 1) ─────────────────────────────────────────────────────
def build_search_op(query: str, with_synonyms: bool = False) -> dict:
    if with_synonyms:
        return {"text": {"query": query, "path": ["nome", "descricao"],
                         "synonyms": "sinonimos_produtos"}}
    return {
        "compound": {
            "should": [
                {"autocomplete": {"query": query, "path": "nome",
                                  "fuzzy": {"maxEdits": 1}, "score": {"boost": {"value": 2}}}},
                {"text": {"query": query, "path": "descricao", "fuzzy": {"maxEdits": 1}}},
            ],
            "minimumShouldMatch": 1,
        }
    }


def build_search_pipeline(search_op: dict, mql_filter: dict) -> list:
    return [
        {"$search": {
            "index": "produtos_search",
            **search_op,
            "count": {"type": "total"},
            "highlight": {"path": ["nome", "descricao"], "maxCharsToExamine": 500, "maxNumPassages": 1},
        }},
        {"$match": mql_filter},
        {"$limit": 50},
        {"$addFields": {"_total_matches": "$$SEARCH_META.count.total"}},
        {"$project": {
            "_id": 0,
            "nome": 1, "marca": 1, "categoria": 1, "subcategoria": 1,
            "preco": 1, "preco_original": 1, "desconto_pct": 1,
            "avaliacao_media": 1, "total_avaliacoes": 1,
            "em_estoque": 1, "score": {"$meta": "searchScore"},
            "highlights": {"$meta": "searchHighlights"},
            "_total_matches": 1,
        }},
    ]


def atlas_search(query: str, categorias=None, preco_min=0, preco_max=15000,
                 only_stock=True, with_synonyms=False) -> dict:
    mql_filter = {"preco": {"$gte": preco_min, "$lte": preco_max}}
    if only_stock:
        mql_filter["em_estoque"] = True
    if categorias:
        mql_filter["categoria"] = {"$in": categorias}

    search_op = build_search_op(query, with_synonyms)
    pipeline  = build_search_pipeline(search_op, mql_filter)

    t0 = time.time()
    results, err = safe_aggregate("produtos", pipeline)
    elapsed = (time.time() - t0) * 1000

    synonyms_fallback = False
    if err == "synonym-analyzer" and with_synonyms:
        synonyms_fallback = True
        search_op = build_search_op(query, False)
        pipeline  = build_search_pipeline(search_op, mql_filter)
        t0 = time.time()
        results, err = safe_aggregate("produtos", pipeline)
        elapsed = (time.time() - t0) * 1000

    if err:
        return {"error": err, "results": [], "pipeline": pipeline}

    total = results[0].get("_total_matches") if results else 0
    return {
        "results": results or [],
        "total_matches": total,
        "elapsed_ms": round(elapsed),
        "synonyms_fallback": synonyms_fallback,
        "pipeline": pipeline,
    }


# ── $searchMeta facets ───────────────────────────────────────────────────────
def search_facets(query: str, with_synonyms=False) -> dict:
    search_op = build_search_op(query, with_synonyms)
    meta_pipeline = [{"$searchMeta": {
        "index": "produtos_search",
        "facet": {
            "operator": search_op,
            "facets": {
                "categorias":   {"type": "string", "path": "categoria", "numBuckets": 10},
                "faixas_preco": {"type": "number", "path": "preco",
                                 "boundaries": [0, 100, 500, 1000, 3000, 5000, 10000, 15000]},
            },
        },
    }}]
    meta, err = safe_aggregate("produtos", meta_pipeline)
    if err or not meta:
        return {"error": err, "categorias": [], "faixas_preco": []}
    data = meta[0]
    return {
        "total": data.get("count", {}).get("lowerBound", 0),
        "categorias":   data.get("facet", {}).get("categorias", {}).get("buckets", []),
        "faixas_preco": data.get("facet", {}).get("faixas_preco", {}).get("buckets", []),
    }


# ── Search vs Vector vs RRF (Tab 2) ──────────────────────────────────────────
def compare_search_vector(query: str) -> dict:
    search_pipeline = [
        {"$search": {"index": "produtos_search", "phrase": {"query": query, "path": "nome"}}},
        {"$limit": 10},
        {"$project": {"_id": 0, "nome": 1, "marca": 1, "categoria": 1, "preco": 1,
                      "avaliacao_media": 1, "score": {"$meta": "searchScore"}}},
    ]
    vector_pipeline = [
        {"$vectorSearch": {"index": "produtos_vector", "path": "descricao",
                           "query": query, "numCandidates": 150, "limit": 10}},
        {"$project": {"_id": 0, "nome": 1, "marca": 1, "categoria": 1, "preco": 1,
                      "avaliacao_media": 1, "score": {"$meta": "vectorSearchScore"}}},
    ]

    t0 = time.time()
    text_res, err_s = safe_aggregate("produtos", search_pipeline)
    vec_res,  err_v = safe_aggregate("produtos_vector", vector_pipeline)
    elapsed = (time.time() - t0) * 1000

    # RRF (k=60) com dedup por nome
    rrf_map, seen_s, seen_v = {}, set(), set()
    for rank, doc in enumerate(text_res or []):
        k = doc["nome"]
        if k in seen_s:
            continue
        seen_s.add(k)
        rrf_map.setdefault(k, {"doc": doc, "rrf": 0, "s": None, "v": None})
        rrf_map[k]["rrf"] += 1 / (60 + rank + 1)
        rrf_map[k]["s"] = rank + 1
    for rank, doc in enumerate(vec_res or []):
        k = doc["nome"]
        if k in seen_v:
            continue
        seen_v.add(k)
        rrf_map.setdefault(k, {"doc": doc, "rrf": 0, "s": None, "v": None})
        rrf_map[k]["rrf"] += 1 / (60 + rank + 1)
        rrf_map[k]["v"] = rank + 1
    fused = sorted(rrf_map.values(), key=lambda x: x["rrf"], reverse=True)[:10]

    return {
        "search":  {"results": text_res or [], "error": err_s, "pipeline": search_pipeline},
        "vector":  {"results": vec_res or [],  "error": err_v, "pipeline": vector_pipeline},
        "hybrid":  [{"nome": x["doc"].get("nome"), "categoria": x["doc"].get("categoria"),
                     "preco": x["doc"].get("preco"), "rrf": round(x["rrf"], 5),
                     "rank_search": x["s"], "rank_vector": x["v"],
                     "both": bool(x["s"] and x["v"])} for x in fused],
        "elapsed_ms": round(elapsed),
    }


# ── Hybrid RRF tunável (Tab 3) ───────────────────────────────────────────────
def hybrid_rrf(query: str, k=60, n_search=20, n_vector=20) -> dict:
    s_pipe = [
        {"$search": {"index": "produtos_search", "compound": {"should": [
            {"autocomplete": {"query": query, "path": "nome",
                              "fuzzy": {"maxEdits": 1}, "score": {"boost": {"value": 3}}}},
            {"text": {"query": query, "path": "descricao", "fuzzy": {"maxEdits": 1}}},
        ]}}},
        {"$limit": n_search},
        {"$project": {"_id": 0, "nome": 1, "categoria": 1, "preco": 1,
                      "search_score": {"$meta": "searchScore"}}},
    ]
    v_pipe = [
        {"$vectorSearch": {"index": "produtos_vector", "path": "descricao",
                           "query": query, "numCandidates": n_vector * 10, "limit": n_vector}},
        {"$project": {"_id": 0, "nome": 1, "categoria": 1, "preco": 1,
                      "vector_score": {"$meta": "vectorSearchScore"}}},
    ]

    t0 = time.time()
    search_res, err_s = safe_aggregate("produtos", s_pipe)
    vector_res, err_v = safe_aggregate("produtos_vector", v_pipe)
    elapsed = (time.time() - t0) * 1000

    if err_s or err_v:
        return {"error": err_s or err_v, "fused": []}

    rrf, seen_s, seen_v = {}, set(), set()
    for rank, doc in enumerate(search_res):
        key = doc["nome"]
        if key in seen_s:
            continue
        seen_s.add(key)
        rrf.setdefault(key, {"doc": doc, "rrf": 0, "s": None, "v": None})
        rrf[key]["rrf"] += 1 / (k + rank + 1)
        rrf[key]["s"] = rank + 1
    for rank, doc in enumerate(vector_res):
        key = doc["nome"]
        if key in seen_v:
            continue
        seen_v.add(key)
        rrf.setdefault(key, {"doc": doc, "rrf": 0, "s": None, "v": None})
        rrf[key]["rrf"] += 1 / (k + rank + 1)
        rrf[key]["v"] = rank + 1
    fused = sorted(rrf.values(), key=lambda x: x["rrf"], reverse=True)[:20]

    only_s = sum(1 for x in fused if x["s"] and not x["v"])
    only_v = sum(1 for x in fused if x["v"] and not x["s"])
    both   = sum(1 for x in fused if x["s"] and x["v"])

    return {
        "fused": [{"nome": x["doc"].get("nome"), "categoria": x["doc"].get("categoria"),
                   "preco": x["doc"].get("preco"), "rrf": round(x["rrf"], 5),
                   "rank_search": x["s"], "rank_vector": x["v"],
                   "both": bool(x["s"] and x["v"]),
                   "s_score": round(1/(k + x["s"]), 5) if x["s"] else 0,
                   "v_score": round(1/(k + x["v"]), 5) if x["v"] else 0} for x in fused],
        "counts": {"only_search": only_s, "only_vector": only_v, "both": both,
                   "n_search": len(search_res), "n_vector": len(vector_res)},
        "elapsed_ms": round(elapsed),
        "k": k,
    }
