"""
main.py — API FastAPI da POC Search × Vector.
Sobe os endpoints que o frontend React (axios) consome.

Rodar:  uvicorn main:app --reload --port 8000
"""

import os
import uuid
import warnings
from dotenv import load_dotenv

# Carrega .env da raiz do projeto (um nível acima de backend/)
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"), override=True)
warnings.filterwarnings("ignore")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import atlas
from agent import run_agent

app = FastAPI(title="Search × Vector POC API", version="1.0")

# Origens liberadas — configurável via CORS_ORIGINS (lista separada por vírgula)
_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _origins if o.strip()],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Modelos ──────────────────────────────────────────────────────────────────
class SearchReq(BaseModel):
    query: str
    categorias: list[str] | None = None
    preco_min: float = 0
    preco_max: float = 15000
    only_stock: bool = True
    synonyms: bool = False

class CompareReq(BaseModel):
    query: str

class HybridReq(BaseModel):
    query: str
    k: int = 60
    n_search: int = 20
    n_vector: int = 20

class AgentReq(BaseModel):
    message: str
    thread_id: str | None = None


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

@app.post("/agent")
def agent_route(req: AgentReq):
    thread_id = req.thread_id or str(uuid.uuid4())
    out = run_agent(req.message, thread_id)
    out["thread_id"] = thread_id
    return out
