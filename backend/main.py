"""
main.py — API FastAPI da POC Search × Vector.
Sobe os endpoints que o frontend React (axios) consome.

Rodar:  uvicorn main:app --reload --port 8200
"""

import os
import time
import uuid
import warnings
from dotenv import load_dotenv

# Carrega .env da raiz do projeto (um nível acima de backend/)
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"), override=True)
warnings.filterwarnings("ignore")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import atlas
from agent import run_agent
from reviews import summarize_reviews

app = FastAPI(title="Search × Vector POC API", version="1.0")

# Origens liberadas — configurável via CORS_ORIGINS (lista separada por vírgula)
_origins = os.getenv("CORS_ORIGINS", "http://localhost:5273,http://127.0.0.1:5273").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _origins if o.strip()],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)


# ── Modelos ──────────────────────────────────────────────────────────────────
class SearchReq(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    categorias: list[str] | None = None
    preco_min: float = Field(0, ge=0)
    preco_max: float = Field(15000, ge=0)
    only_stock: bool = True
    synonyms: bool = False

class CompareReq(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)

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


# ── Rotas ────────────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok", "db": atlas.DB_NAME}

@app.get("/stats")
def stats():
    counts = atlas.get_stats()
    return {
        "collections": counts,
        "indices": [
            {"name": "produtos_search", "type": "Atlas Search", "status": "READY"},
            {"name": "produtos_vector", "type": "Vector Search", "status": "READY"},
        ],
    }

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
    return atlas.compare_search_vector(req.query)

@app.post("/hybrid")
def hybrid(req: HybridReq):
    return atlas.hybrid_rrf(req.query, k=req.k, n_search=req.n_search, n_vector=req.n_vector)

@app.post("/hybrid-native")
def hybrid_native(req: CompareReq):
    """Hybrid search com o stage NATIVO $rankFusion (8.1+), fallback p/ RRF em 8.0."""
    return atlas.hybrid_native(req.query)

@app.post("/agent")
def agent_route(req: AgentReq):
    thread_id = req.thread_id or str(uuid.uuid4())
    out = run_agent(req.message, thread_id)
    out["thread_id"] = thread_id
    return out

# O $facet do analytics samplea 12k docs — caro p/ repetir a cada refresh; cache de 5 min
_analytics_cache = {"data": None, "ts": 0.0}

@app.get("/analytics")
def analytics():
    if _analytics_cache["data"] is None or time.time() - _analytics_cache["ts"] > 300:
        data = atlas.get_analytics()
        if isinstance(data, dict) and data.get("error"):
            return data  # erro não entra no cache
        _analytics_cache["data"] = data
        _analytics_cache["ts"] = time.time()
    return _analytics_cache["data"]

@app.post("/similar")
def similar(req: SimilarReq):
    return atlas.find_similar(produto_id=req.produto_id, nome=req.nome, same_category=req.same_category)

@app.post("/reviews-rag")
def reviews_rag(req: ReviewsReq):
    return summarize_reviews(req.query)
