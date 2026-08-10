# Search & AI Agent POC — MongoDB Atlas

Most e-commerce stacks glue together a search engine, a vector database, an analytics warehouse and a store for agent memory. This POC runs all four on MongoDB Atlas alone, over a synthetic 20M-product catalog.

Seven tabs, one Atlas capability each. Every screen prints the MQL that actually ran — nothing is mocked. Point it at any dataset via `MONGODB_URI` / `DB_NAME`.

```
React + LeafyGreen  ──axios──►  FastAPI  ──►  MongoDB Atlas
     (:5273)                     (:8200)
```

## The demo, tab by tab

**1. Atlas Search** — full-text over the catalog: autocomplete, fuzzy (`"adidass"` → Adidas), clickable facets via `$searchMeta`, highlighting, match counts, `scoreDetails`. Filters run inside `$search` when the index allows it, so counts reflect them; otherwise the app falls back and says so.

![Atlas Search tab: facets, highlights and total match count](docs/screenshots/atlas-search.png)

**2. Search vs Vector** — the same query on both engines, side by side. Exact-phrase lexical returns **zero** for `"academia em casa"`; vector search understands the intent. Each engine reports its own latency.

![Lexical search returning zero next to vector search returning relevant products](docs/screenshots/search-vs-vector.png)

**3. Hybrid RRF** — native `$rankFusion` (MongoDB 8.1+, fused server-side in one aggregation) or application-side RRF with adjustable `k`, kept as the educational view. Falls back with a reason when `$rankFusion` requirements aren't met.

![Hybrid tab running native $rankFusion with per-engine ranks](docs/screenshots/hybrid-rrf.png)

**4. Similares** — vector "more like this" from a product description, with category and stock filters running *inside* `$vectorSearch`, not after it.

![Similar-products results with pre-filtering applied inside $vectorSearch](docs/screenshots/similares.png)

**5. Analytics** — one `$facet` pipeline running several aggregations in parallel on the server. Defaults to a 12k `$sample`; toggle to run over the full collection and compare timings.

![Analytics tab: parallel $facet aggregations over the catalog](docs/screenshots/analytics.png)

**6. Reviews RAG** — `$search` finds the most relevant product with reviews, MongoDB returns them, Claude summarizes grounded strictly in that data.

**7. AI Agent** — a LangGraph ReAct agent with four MongoDB tools, long-term memory via `MongoDBSaver`, and a trace built by the same functions the tools execute — byte-for-byte what ran.

![AI Agent tab with tool calls and the MQL trace](docs/screenshots/ai-agent.png)

## Collections

```
POC
├── produtos          20M products      — Atlas Search: produtos_search
├── produtos_vector   500K subset       — Vector Search: produtos_vector (voyage-4, autoEmbed)
│                                       — Atlas Search: produtos_vector_search
├── avaliacoes        reviews           — Reviews RAG + agent
└── checkpoints       LangGraph memory
```

The 500K vector subset is a cost/build-time decision, not a limit — it's a representative `$sample`. The extra lexical index on `produtos_vector` exists because native `$rankFusion` needs both sub-pipelines on the same collection. The app detects available indexes via `$listSearchIndexes` and degrades gracefully.

## Setup

Requires Atlas 8.0+ (8.1+ for native `$rankFusion`), Python 3.11+, Node 18+, and an Anthropic key.

`.env` at the repo root:

```env
MONGODB_URI=mongodb+srv://<user>:<password>@<cluster>.mongodb.net/
DB_NAME=POC
ANTHROPIC_API_KEY=sk-ant-...
```

```bash
python3 setup_search_indexes.py    # one-time, idempotent; --status to check progress
bash start.sh                      # backend + frontend → http://localhost:5273
```

Custom ports: `BACKEND_PORT=8201 FRONTEND_PORT=5274 bash start.sh`. Manual run: `uvicorn main:app --port 8200` in `backend/`, `npm run dev` in `frontend/`.

## Synonyms (optional)

The synonyms toggle needs a mapping named `sinonimos_produtos` on `produtos_search`: Atlas UI → Atlas Search → Synonyms → source collection `sinonimos`, analyzer `lucene.portuguese`. Then insert documents like:

```json
[
  { "mappingType": "equivalent", "synonyms": ["notebook", "laptop", "computador portátil"] },
  { "mappingType": "equivalent", "synonyms": ["celular", "smartphone", "telefone"] },
  { "mappingType": "explicit", "input": ["presente"], "synonyms": ["kit", "combo", "caixa"] }
]
```

The index rebuilds in about two minutes; the toggle warns while it's building.

## Stack

React 18 + Vite + LeafyGreen · FastAPI · LangGraph (ReAct) · Claude Sonnet 4.6 · Voyage `voyage-4` via Atlas autoEmbed · MongoDB Atlas 8.0+.

UI copy is in Portuguese on purpose (Brazilian audience). Component details: [`frontend/README.md`](frontend/README.md) · [`backend/README.md`](backend/README.md).
