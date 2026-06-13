# Search & AI Agent POC — MongoDB Atlas

A technical proof of concept showing how MongoDB Atlas can serve as the complete
backend for search and AI workloads. It combines full-text search, semantic
(vector) search, hybrid ranking, real-time analytics, RAG, and a tool-using AI
agent over a synthetic marketplace catalog — all on a single platform.

The demo is configurable for any dataset through environment variables
(`MONGODB_URI`, `DB_NAME`).

## Architecture

```
React + LeafyGreen  ──axios──►  FastAPI  ──►  MongoDB Atlas
  (frontend/ :5273)             (backend/ :8200)      (POC)
```

| Layer       | Technology                                              |
|-------------|---------------------------------------------------------|
| UI          | React 18 + Vite + LeafyGreen (MongoDB design system)    |
| API         | FastAPI (`backend/`)                                    |
| AI agent    | LangGraph (ReAct pattern)                               |
| LLM         | Claude Sonnet 4.6 (Anthropic)                           |
| Embeddings  | Voyage AI `voyage-4` via Atlas autoEmbed                |
| Database    | MongoDB Atlas 8.0+                                       |
| Agent memory| `MongoDBSaver` — checkpoints keyed by `thread_id`       |

## Features

The UI is organized into seven tabs, each demonstrating a distinct Atlas capability.

**Atlas Search** — Full-text search over the product catalog: autocomplete,
fuzzy matching (`"adidass"` → Adidas), faceted navigation via `$searchMeta`,
native highlighting, total match counts, compound queries, and an optional
synonym mapping.

**Search vs Vector** — Side-by-side comparison of lexical search and semantic
search. Conceptual queries such as `"academia em casa"` return nothing under
full-text search but surface dumbbells, whey protein, and kettlebells under
vector search, illustrating the value of autoEmbed.

**Hybrid RRF** — Combines full-text and vector results with Reciprocal Rank
Fusion (`score = Σ 1 / (k + rankᵢ)`). The `k` constant and per-engine result
counts are adjustable, and each result shows its origin (search only, vector
only, or both).

**Similares** — Vector "more like this" using a product's description as the
query, with native pre-filtering: the category and stock filters run inside
`$vectorSearch` rather than as a post-processing step.

**Analytics** — A single `$facet` pipeline runs several aggregations in parallel
on the server, positioning MongoDB as an analytical engine over the catalog.

**Reviews RAG** — Atlas Search locates a product, its real reviews are pulled
from MongoDB, and Claude summarizes them grounded strictly in that data.

**AI Agent** — A LangGraph ReAct agent with four MongoDB tools
(`busca_semantica`, `buscar_produto`, `comparar_categoria`,
`produtos_por_faixa_preco`), long-term memory via `MongoDBSaver`, and a
transparent trace exposing each tool call, the generated MQL, and the result
returned to the model.

## Collections

```
POC (database)
├── produtos          Product catalog        — Atlas Search index: produtos_search
├── produtos_vector   Embedded subset        — Vector Search index: produtos_vector (voyage-4)
├── avaliacoes        Product reviews         — used by Reviews RAG and the agent
└── checkpoints       LangGraph agent memory
```

## Setup

### Prerequisites

- MongoDB Atlas cluster 8.0+
- Anthropic API key (Claude)
- Python 3.11+ and Node 18+

### Environment variables

Create a `.env` file at the repository root:

```env
MONGODB_URI=mongodb+srv://<user>:<password>@<cluster>.mongodb.net/
DB_NAME=POC
ANTHROPIC_API_KEY=sk-ant-...
```

### Run (backend + frontend)

```bash
bash start.sh
```

Then open http://localhost:5273. Ports are configurable:
`BACKEND_PORT=8201 FRONTEND_PORT=5274 bash start.sh`.

### Run manually (two terminals)

```bash
# Terminal 1 — backend
cd backend && pip install -r requirements.txt && uvicorn main:app --port 8200

# Terminal 2 — frontend
cd frontend && npm install && npm run dev
```

See [`frontend/README.md`](frontend/README.md) and
[`backend/README.md`](backend/README.md) for component-level details.

## Configuring synonyms in the Atlas UI

The synonyms toggle in the Atlas Search tab relies on a mapping named
`sinonimos_produtos` on the `produtos_search` index.

1. Atlas UI → cluster → Atlas Search → `produtos_search` → Synonyms →
   Add synonym mapping.
2. Name: `sinonimos_produtos`; source collection: `sinonimos`; analyzer:
   `lucene.portuguese`.
3. Insert the following documents into the `sinonimos` collection (Atlas UI or
   Compass):

```json
[
  { "mappingType": "equivalent", "synonyms": ["notebook", "laptop", "computador portátil"] },
  { "mappingType": "equivalent", "synonyms": ["tênis", "calçado esportivo", "sneaker"] },
  { "mappingType": "equivalent", "synonyms": ["celular", "smartphone", "telefone"] },
  { "mappingType": "equivalent", "synonyms": ["fone", "headphone", "fone de ouvido", "earphone"] },
  { "mappingType": "equivalent", "synonyms": ["tv", "televisão", "televisor"] },
  { "mappingType": "equivalent", "synonyms": ["geladeira", "refrigerador", "frigobar"] },
  { "mappingType": "equivalent", "synonyms": ["academia", "musculação", "ginástica"] },
  { "mappingType": "explicit", "input": ["presente"], "synonyms": ["kit", "combo", "caixa"] }
]
```

The index rebuilds after the mapping is saved (about two minutes). The toggle
shows a notice if the index is still building.

> Note: the application UI is intentionally in Portuguese, since the demo
> targets a Brazilian audience.

## Project structure

```
.
├── frontend/                 React 18 + Vite + LeafyGreen
│   ├── src/tabs/             One component per feature tab
│   └── src/components/       Sidebar, KpiCard, ProductTable, Leaf
├── backend/                  FastAPI
│   ├── atlas.py              MongoDB connection and pipelines (search, vector, RRF, facets)
│   ├── agent.py              LangGraph ReAct agent and MQL trace reconstruction
│   ├── reviews.py            Reviews RAG summarization
│   └── main.py               REST routes, CORS, request models
├── populate_marketplace.py   Generates the synthetic catalog and reviews
├── start.sh                  Launches backend and frontend together
└── README.md
```

The repository also contains a separate Streamlit transaction-profiler demo
(`app.py`, `populate_profiler.py`); it is independent of the marketplace POC.

## Stack

![MongoDB Atlas](https://img.shields.io/badge/MongoDB%20Atlas-8.0-00ED64?style=flat&logo=mongodb&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688?style=flat&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?style=flat&logo=react&logoColor=black)
![LangGraph](https://img.shields.io/badge/LangGraph-ReAct-7C6DD8?style=flat)
![Claude](https://img.shields.io/badge/Claude-Sonnet%204.6-FF6B4A?style=flat)
