# Frontend — Search & Vector (React + LeafyGreen)

The POC interface, built with React 18 and Vite using MongoDB's official
component library (LeafyGreen), consuming the FastAPI backend over axios.

## Stack

| Layer        | Technology                                                       |
|--------------|------------------------------------------------------------------|
| UI framework | React 18 + Vite                                                  |
| Components   | `@leafygreen-ui/*` (MongoDB design system)                       |
| Typography   | Outfit + JetBrains Mono (Google Fonts)                           |
| HTTP         | axios                                                            |
| Polyfills    | `vite-plugin-node-polyfills` (Buffer/process for LeafyGreen deps)|

## Prerequisites

- Node 18+ (tested on Node 18–26)
- Backend running (see [`../backend/README.md`](../backend/README.md))

## Run with the backend

From the repository root:

```bash
bash start.sh        # Starts FastAPI :8200 and Vite :5273, then verifies both
```

## Run the frontend only

```bash
npm install
cp .env.example .env        # Set VITE_API_URL if the backend is not on localhost:8200
npm run dev                 # http://localhost:5273
```

## Environment variables

| Variable       | Default                   | Description                  |
|----------------|---------------------------|------------------------------|
| `VITE_API_URL` | `http://localhost:8200`   | FastAPI backend base URL     |

## Structure

```
src/
├── api.js                 axios client and endpoints
├── theme.js               MongoDB Atlas color tokens and formatters
├── App.jsx                LeafyGreenProvider, layout, and tabs
├── components/
│   ├── Leaf.jsx           MongoDB leaf logo
│   ├── Sidebar.jsx        Navigation, collections, cluster status
│   ├── KpiCard.jsx        Stat-bar segment
│   └── ProductTable.jsx   Results table and MQL block
└── tabs/
    ├── AtlasSearch.jsx    Full-text search (autocomplete, fuzzy, highlight)
    ├── SearchVsVector.jsx Lexical vs semantic comparison
    ├── HybridRRF.jsx      Tunable RRF with a score chart
    ├── Similares.jsx      Vector "more like this" with pre-filtering
    ├── Analytics.jsx      $facet aggregations
    ├── ReviewsRag.jsx     Review retrieval and summarization
    └── AiAgent.jsx        ReAct chat with a tool → MQL → result trace
```

## Technical notes

- React 18 (not 19): the LeafyGreen components do not yet support React 19.
- Node polyfills: a LeafyGreen dependency relies on Node globals (`Buffer`).
  `vite-plugin-node-polyfills` provides them; without it the page renders blank.
- The UI copy is intentionally in Portuguese, since the demo targets a Brazilian
  audience.

## Production build

```bash
npm run build      # Outputs to dist/
npm run preview    # Serves the build locally
```
