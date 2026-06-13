"""
atlas.py — MongoDB Atlas data-access layer.
Atlas Search, Vector Search, Hybrid RRF, and facet pipelines,
exposed as pure functions for the FastAPI layer.
"""

import os
import time
from pymongo import MongoClient
from pymongo.errors import PyMongoError, ExecutionTimeout
from dotenv import load_dotenv

# Load the .env at the project root (self-contained — does not depend on main.py)
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"), override=False)

MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME     = os.getenv("DB_NAME", "POC")
QUERY_TIMEOUT_MS = 10_000

_client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
db = _client[DB_NAME]  # lazy connection — only connects on the first query


# ── Safe execution helper ────────────────────────────────────────────────────
def safe_aggregate(collection: str, pipeline: list):
    """Run an aggregate with friendly error handling. Returns (results, error)."""
    try:
        return list(db[collection].aggregate(pipeline, maxTimeMS=QUERY_TIMEOUT_MS)), None
    except ExecutionTimeout:
        return None, "Operação cancelada — tempo limite de 10s atingido."
    except PyMongoError as e:
        msg = str(e)
        if "index not found" in msg.lower() or "no such index" in msg.lower():
            return None, "Índice não encontrado. Verifique se o Search/Vector index está READY no Atlas."
        if "synonym" in msg.lower():
            return None, "synonym-analyzer"  # flag for graceful fallback
        return None, msg
    except Exception as e:
        return None, str(e)


# ── Collection stats ─────────────────────────────────────────────────────────
def get_stats() -> dict:
    out = {}
    for c in ["produtos", "produtos_vector", "avaliacoes"]:
        try:
            out[c] = db[c].estimated_document_count()
        except Exception:
            out[c] = 0
    return out


# ── Analytics — Aggregation Framework ($facet) ───────────────────────────────
def get_analytics() -> dict:
    """A single $facet runs several aggregations in parallel on the server."""
    pipeline = [
        {"$facet": {
            "por_categoria": [
                {"$group": {"_id": "$categoria", "total": {"$sum": 1},
                            "preco_medio": {"$avg": "$preco"},
                            "avaliacao_media": {"$avg": "$avaliacao_media"}}},
                {"$sort": {"total": -1}},
            ],
            "top_marcas": [
                {"$group": {"_id": "$marca", "total": {"$sum": 1}}},
                {"$sort": {"total": -1}}, {"$limit": 8},
            ],
            "faixa_preco": [
                {"$bucket": {
                    "groupBy": "$preco",
                    "boundaries": [0, 100, 500, 1000, 3000, 5000, 10000, 999999],
                    "default": "outros",
                    "output": {"total": {"$sum": 1}},
                }},
            ],
            "por_mes": [
                {"$match": {"created_at": {"$type": "date"}}},
                {"$group": {"_id": {"$dateToString": {"format": "%Y-%m", "date": "$created_at"}},
                            "total": {"$sum": 1}}},
                {"$sort": {"_id": 1}}, {"$limit": 12},
            ],
            "geral": [
                {"$group": {"_id": None,
                            "total": {"$sum": 1},
                            "preco_medio": {"$avg": "$preco"},
                            "desconto_medio": {"$avg": "$desconto_pct"},
                            "em_estoque": {"$sum": {"$cond": ["$em_estoque", 1, 0]}}}},
            ],
        }},
    ]
    # Run over a representative sample (a full scan over millions of docs would be slow)
    sample_pipeline = [{"$sample": {"size": 12000}}] + pipeline
    t0 = time.time()
    try:
        res = list(db["produtos"].aggregate(sample_pipeline, maxTimeMS=25000))
    except Exception as e:
        return {"error": str(e)}
    elapsed = (time.time() - t0) * 1000
    data = res[0] if res else {}
    geral = (data.get("geral") or [{}])[0]
    faixa_labels = ["R$ 0–100", "R$ 100–500", "R$ 500–1K", "R$ 1K–3K", "R$ 3K–5K", "R$ 5K–10K", "R$ 10K+"]
    faixa = data.get("faixa_preco", [])
    return {
        "por_categoria": data.get("por_categoria", []),
        "top_marcas": data.get("top_marcas", []),
        "faixa_preco": [{"label": faixa_labels[i] if i < len(faixa_labels) else str(b.get("_id")),
                         "total": b.get("total", 0)} for i, b in enumerate(faixa)],
        "por_mes": data.get("por_mes", []),
        "geral": {
            "preco_medio": round(geral.get("preco_medio", 0), 2),
            "desconto_medio": round(geral.get("desconto_medio", 0), 1),
            "em_estoque_pct": round(100 * geral.get("em_estoque", 0) / max(geral.get("total", 1), 1), 1),
            "amostra": geral.get("total", 0),
        },
        "elapsed_ms": round(elapsed),
        "pipeline": pipeline,
    }


# ── Recommendations — Vector "more like this" with PRE-FILTERING ──────────────
def find_similar(produto_id: str = None, nome: str = None, same_category: bool = True) -> dict:
    """Semantically similar products (autoEmbed). Demonstrates VECTOR PRE-FILTERING:
    the filter (category / in-stock) runs INSIDE $vectorSearch — semantic plus
    structured filtering in a single operation, with no application-side post-filter."""
    # Find the base product via Atlas Search (indexed) — NOT via a $match on an
    # unindexed field, which would trigger a collection scan over millions of docs.
    if produto_id:
        base, err = safe_aggregate("produtos", [
            {"$match": {"produto_id": produto_id}}, {"$limit": 1},
            {"$project": {"_id": 0, "nome": 1, "descricao": 1, "categoria": 1, "preco": 1, "produto_id": 1}},
        ])
    else:
        base, err = safe_aggregate("produtos", [
            {"$search": {"index": "produtos_search",
                         "autocomplete": {"query": nome, "path": "nome", "fuzzy": {"maxEdits": 1}}}},
            {"$limit": 1},
            {"$project": {"_id": 0, "nome": 1, "descricao": 1, "categoria": 1, "preco": 1, "produto_id": 1}},
        ])
    if err or not base:
        return {"error": err or "Produto não encontrado", "base": None, "similares": []}
    b = base[0]

    # Vector search on the meaning of the base product's description.
    # NATIVE PRE-FILTERING: the filter (category + in-stock) runs INSIDE
    # $vectorSearch — the index stores those fields as `filter`. Semantic plus
    # structured filtering in a single operation, with no application-side post-filter.
    vector_stage = {"$vectorSearch": {
        "index": "produtos_vector", "path": "descricao",
        "query": b.get("descricao", b["nome"]),
        "numCandidates": 200, "limit": 9,
    }}
    if same_category:
        vector_stage["$vectorSearch"]["filter"] = {
            "categoria": b.get("categoria"), "em_estoque": True,
        }

    sim, err2 = safe_aggregate("produtos_vector", [
        vector_stage,
        {"$project": {"_id": 0, "nome": 1, "marca": 1, "categoria": 1, "preco": 1,
                      "avaliacao_media": 1, "produto_id": 1, "score": {"$meta": "vectorSearchScore"}}},
    ])
    if err2:
        return {"error": err2, "base": b, "similares": []}

    similares = [s for s in (sim or []) if s.get("nome") != b["nome"]][:8]
    return {"base": b, "similares": similares, "filtered": same_category}


# ── Product reviews (for RAG) ────────────────────────────────────────────────
# Only a small subset of products has reviews. Cache that subset's catalog
# (id + name + category) once, so review lookups always land on a product that
# HAS reviews — this keeps the demo from ever hitting an empty "0 reviews" state.
_reviewed_catalog = None

def _get_reviewed_catalog():
    global _reviewed_catalog
    if _reviewed_catalog is None:
        try:
            # distinct uses the produto_id index (~0.2s) instead of a $group scan
            id_list = db["avaliacoes"].distinct("produto_id")
        except Exception:
            id_list = []
        prods, _ = safe_aggregate("produtos", [
            {"$match": {"produto_id": {"$in": id_list}}},
            {"$project": {"_id": 0, "produto_id": 1, "nome": 1, "marca": 1,
                          "categoria": 1, "preco": 1, "avaliacao_media": 1, "total_avaliacoes": 1}},
        ])
        _reviewed_catalog = prods or []
    return _reviewed_catalog


def get_product_and_reviews(query: str, n_reviews: int = 8) -> dict:
    """Find the most relevant product THAT HAS reviews and fetch them (top by helpfulness)."""
    catalog = _get_reviewed_catalog()
    if not catalog:
        return {"error": "Nenhum produto com avaliações", "produto": None, "reviews": []}

    # Simple text-relevance match within the reviewed catalog (case-insensitive,
    # by name/brand/category tokens) — guarantees the chosen product has reviews
    q = query.lower().strip()
    tokens = [t for t in q.split() if len(t) > 2]
    def score(p):
        blob = f"{p.get('nome','')} {p.get('marca','')} {p.get('categoria','')}".lower()
        s = sum(1 for t in tokens if t in blob)
        if q in blob:
            s += 3
        return s
    ranked = sorted(catalog, key=score, reverse=True)
    produto = ranked[0] if score(ranked[0]) > 0 else max(catalog, key=lambda p: int(p.get("total_avaliacoes", 0) or 0))

    reviews, _ = safe_aggregate("avaliacoes", [
        {"$match": {"produto_id": produto["produto_id"]}},
        {"$sort": {"util_count": -1}},
        {"$limit": n_reviews},
        {"$project": {"_id": 0, "nota": 1, "titulo": 1, "texto": 1, "util_count": 1,
                      "verificado": 1, "usuario": 1}},
    ])
    return {"produto": produto, "reviews": reviews or []}


# ── Atlas Search (tab 1) ─────────────────────────────────────────────────────
# BUSINESS-SIGNAL scoring: multiply text relevance by the product rating
# (avaliacao_media). Well-rated products rank higher — e-commerce relevance
# tuning driven by a business rule, not text relevance alone.
def _business_score() -> dict:
    return {"function": {
        "multiply": [
            {"score": "relevance"},
            {"path": {"value": "avaliacao_media", "undefined": 3.0}},
        ]
    }}


def build_search_op(query: str, with_synonyms: bool = False, boost_business: bool = True) -> dict:
    if with_synonyms:
        return {"text": {"query": query, "path": ["nome", "descricao"],
                         "synonyms": "sinonimos_produtos"}}
    nome_score = _business_score() if boost_business else {"boost": {"value": 2}}
    return {
        "compound": {
            "should": [
                {"autocomplete": {"query": query, "path": "nome",
                                  "fuzzy": {"maxEdits": 1}, "score": nome_score}},
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
            "scoreDetails": True,   # transparency: WHY this product ranked where it did
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
            "scoreDetails": {"$meta": "searchScoreDetails"},
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


# ── Search vs Vector vs RRF (tab 2) ──────────────────────────────────────────
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

    # RRF (k=60) with dedup by name
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


# ── Tunable Hybrid RRF (tab 3) ───────────────────────────────────────────────
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


# ── Hybrid via NATIVE $rankFusion (MongoDB 8.1+) — with graceful fallback ─────
def hybrid_native(query: str, limit: int = 20) -> dict:
    """Hybrid search using the NATIVE $rankFusion stage (server-side, no application
    RRF). Requires MongoDB 8.1+. On 8.0 it falls back to the Python RRF and flags it."""
    pipeline = [
        {"$rankFusion": {
            "input": {"pipelines": {
                "textual": [
                    {"$search": {"index": "produtos_search", "compound": {"should": [
                        {"autocomplete": {"query": query, "path": "nome", "fuzzy": {"maxEdits": 1}}},
                        {"text": {"query": query, "path": "descricao", "fuzzy": {"maxEdits": 1}}},
                    ]}}},
                    {"$limit": limit},
                ],
                "semantico": [
                    {"$vectorSearch": {"index": "produtos_vector", "path": "descricao",
                                       "query": query, "numCandidates": limit * 10, "limit": limit}},
                ],
            }},
            "combination": {"weights": {"textual": 1, "semantico": 1}},
        }},
        {"$limit": limit},
        {"$project": {"_id": 0, "nome": 1, "categoria": 1, "preco": 1,
                      "scoreDetails": {"$meta": "scoreDetails"}}},
    ]
    t0 = time.time()
    results, err = safe_aggregate("produtos", pipeline)
    elapsed = (time.time() - t0) * 1000

    if err:
        # 8.0 has no $rankFusion → fall back to the manual RRF and flag it
        fb = hybrid_rrf(query, k=60, n_search=limit, n_vector=limit)
        return {
            "native": False,
            "reason": "$rankFusion requer MongoDB 8.1+ (cluster atual: 8.0) — usando RRF na aplicação.",
            "fused": fb.get("fused", []), "counts": fb.get("counts", {}),
            "elapsed_ms": fb.get("elapsed_ms", 0), "pipeline": pipeline,
        }
    return {
        "native": True,
        "results": results or [], "elapsed_ms": round(elapsed), "pipeline": pipeline,
    }
