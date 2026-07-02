"""
main.py — FastAPI API for the Search & Vector POC.
Serves the endpoints consumed by the React frontend (axios).

Run:  uvicorn main:app --reload --port 8200
"""

import os
import time
import uuid
import warnings
from dotenv import load_dotenv

# Load the .env at the project root (one level above backend/)
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"), override=True)
warnings.filterwarnings("ignore")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import atlas
from agent import run_agent
from reviews import summarize_reviews

app = FastAPI(title="Search × Vector POC API", version="1.0")

# Allowed origins — configurable via CORS_ORIGINS (comma-separated list)
_origins = os.getenv("CORS_ORIGINS", "http://localhost:5273,http://127.0.0.1:5273").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _origins if o.strip()],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)


# ── Request models ───────────────────────────────────────────────────────────
class SearchReq(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    categorias: list[str] | None = None
    preco_min: float = Field(0, ge=0)
    preco_max: float = Field(15000, ge=0)
    only_stock: bool = True
    synonyms: bool = False

class CompareReq(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    mode: str = Field("phrase", pattern="^(phrase|compound)$")

class HybridReq(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    k: int = Field(60, ge=1, le=1000)
    n_search: int = Field(20, ge=1, le=100)
    n_vector: int = Field(20, ge=1, le=100)

class AgentReq(BaseModel):
    message: str
    thread_id: str | None = None

class SimilarReq(BaseModel):
    produto_id: str | None = None
    nome: str | None = None
    same_category: bool = True

class ReviewsReq(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)


# ── Routes ───────────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok", "db": atlas.DB_NAME}

@app.get("/stats")
def stats():
    counts = atlas.get_stats()
    # Real status via $listSearchIndexes — a building/failed index shows as such
    indices = atlas.get_index_status()
    if not indices:  # cluster without $listSearchIndexes support / no indexes yet
        indices = [
            {"name": "produtos_search", "type": "Atlas Search", "status": "UNKNOWN"},
            {"name": "produtos_vector", "type": "Vector Search", "status": "UNKNOWN"},
        ]
    return {"collections": counts, "indices": indices}

@app.post("/search")
def search(req: SearchReq):
    return atlas.atlas_search(
        req.query, categorias=req.categorias, preco_min=req.preco_min,
        preco_max=req.preco_max, only_stock=req.only_stock, with_synonyms=req.synonyms,
    )

@app.post("/search/facets")
def facets(req: SearchReq):
    return atlas.search_facets(req.query, with_synonyms=req.synonyms)

@app.post("/compare")
def compare(req: CompareReq):
    return atlas.compare_search_vector(req.query, mode=req.mode)

@app.post("/hybrid")
def hybrid(req: HybridReq):
    return atlas.hybrid_rrf(req.query, k=req.k, n_search=req.n_search, n_vector=req.n_vector)

@app.post("/hybrid-native")
def hybrid_native(req: CompareReq):
    """Hybrid search using the NATIVE $rankFusion stage (8.1+), with an RRF fallback on 8.0."""
    return atlas.hybrid_native(req.query)

@app.post("/agent")
def agent_route(req: AgentReq):
    thread_id = req.thread_id or str(uuid.uuid4())
    out = run_agent(req.message, thread_id)
    out["thread_id"] = thread_id
    return out

# The analytics $facet is costly to repeat on every refresh; cache 5 min per mode
_analytics_cache = {}  # "sample"/"full" -> {"data": dict, "ts": float}

@app.get("/analytics")
def analytics(full: bool = False):
    key = "full" if full else "sample"
    hit = _analytics_cache.get(key)
    if hit is None or time.time() - hit["ts"] > 300:
        data = atlas.get_analytics(full=full)
        if isinstance(data, dict) and data.get("error"):
            return data  # do not cache errors
        _analytics_cache[key] = {"data": data, "ts": time.time()}
        return data
    return hit["data"]

@app.post("/similar")
def similar(req: SimilarReq):
    return atlas.find_similar(produto_id=req.produto_id, nome=req.nome, same_category=req.same_category)

@app.post("/reviews-rag")
def reviews_rag(req: ReviewsReq):
    return summarize_reviews(req.query)
