# Backend — Search × Vector API (FastAPI)

API que expõe a lógica de busca da POC (Atlas Search, Vector Search, Hybrid RRF e
o agente LangGraph) como endpoints REST para o frontend React consumir via axios.

## Endpoints

| Método | Rota | Descrição |
|---|---|---|
| GET  | `/health` | Healthcheck |
| GET  | `/stats` | Contagem das collections + índices |
| POST | `/search` | Atlas Search (autocomplete, fuzzy, highlight, count, sinônimos) |
| POST | `/search/facets` | Facets em tempo real (`$searchMeta`) |
| POST | `/compare` | Search vs Vector vs RRF (lado a lado) |
| POST | `/hybrid` | RRF tunável (k, n_search, n_vector) |
| POST | `/agent` | Agente LangGraph ReAct + trace estruturado |

Docs interativas: `http://localhost:8000/docs`

## Setup

```bash
pip install -r requirements.txt
# usa o .env da raiz do projeto (MONGODB_URI, DB_NAME, ANTHROPIC_API_KEY)
uvicorn main:app --reload --port 8000
```

## Variáveis de ambiente

| Variável | Descrição |
|---|---|
| `MONGODB_URI` | Connection string do Atlas |
| `DB_NAME` | Database (default: `POC`) |
| `ANTHROPIC_API_KEY` | Para o endpoint `/agent` |
| `CORS_ORIGINS` | Origens liberadas, separadas por vírgula (default: localhost:5173) |

## Arquitetura

```
atlas.py   → conexão MongoDB + pipelines (search, vector, RRF, facets)
agent.py   → agente LangGraph ReAct com 4 ferramentas + reconstrução de MQL
main.py    → FastAPI: rotas, CORS, modelos pydantic
```
