# Backend — Search & Vector API (FastAPI)

Exposes the POC's search logic (Atlas Search, Vector Search, Hybrid RRF,
analytics, Reviews RAG, and the LangGraph agent) as REST endpoints consumed by
the React frontend over axios.

## Endpoints

| Method | Path             | Description                                                     |
|--------|------------------|-----------------------------------------------------------------|
| GET    | `/health`        | Health check                                                    |
| GET    | `/stats`         | Collection counts and index status                             |
| POST   | `/search`        | Atlas Search (autocomplete, fuzzy, highlight, counts, synonyms) |
| POST   | `/search/facets` | Real-time facets via `$searchMeta`                              |
| POST   | `/compare`       | Full-text vs vector vs RRF, side by side                        |
| POST   | `/hybrid`        | Tunable RRF (`k`, `n_search`, `n_vector`)                       |
| POST   | `/hybrid-native` | Native `$rankFusion` (Atlas 8.1+) with an RRF fallback          |
| GET    | `/analytics`     | Parallel aggregations via `$facet` (cached for 5 minutes)       |
| POST   | `/similar`       | Vector "more like this" with native pre-filtering               |
| POST   | `/reviews-rag`   | Review retrieval and Claude summarization                       |
| POST   | `/agent`         | LangGraph ReAct agent with a structured MQL trace               |

Interactive API docs: http://localhost:8200/docs

## Setup

```bash
pip install -r requirements.txt
# Reads the .env at the repository root (MONGODB_URI, DB_NAME, ANTHROPIC_API_KEY)
uvicorn main:app --reload --port 8200
```

## Environment variables

| Variable            | Description                                                      |
|---------------------|------------------------------------------------------------------|
| `MONGODB_URI`       | Atlas connection string                                          |
| `DB_NAME`           | Database name (default: `POC`)                                   |
| `ANTHROPIC_API_KEY` | Required by `/agent` and `/reviews-rag`                          |
| `CORS_ORIGINS`      | Comma-separated allowed origins (default: `localhost:5273`)      |

## Modules

```
atlas.py     MongoDB connection and pipelines (search, vector, RRF, facets, analytics)
agent.py     LangGraph ReAct agent with four tools and MQL reconstruction
reviews.py   Reviews RAG: retrieval plus Claude summarization
main.py      FastAPI routes, CORS, and Pydantic request models
```
