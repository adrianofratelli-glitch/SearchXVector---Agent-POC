# Frontend — Search × Vector (React + LeafyGreen)

Interface da POC construída com **React 18 + Vite** e os componentes oficiais da MongoDB
(**LeafyGreen**), consumindo o backend FastAPI via **axios**.

## Stack

| Camada | Tecnologia |
|---|---|
| UI framework | React 18 + Vite |
| Componentes | `@leafygreen-ui/*` (design system oficial MongoDB) |
| Fontes | Euclid Circular A + MongoDB Value Serif (CDN MongoDB) |
| HTTP | axios |
| Polyfills | `vite-plugin-node-polyfills` (Buffer/process p/ deps do LeafyGreen) |

## Pré-requisitos

- Node 18+ (testado em Node 18–26)
- Backend rodando (ver `../backend/README.md`)

## Setup

```bash
npm install
cp .env.example .env        # ajuste VITE_API_URL se o backend não estiver em localhost:8000
npm run dev                 # http://localhost:5173
```

## Variáveis de ambiente

| Variável | Default | Descrição |
|---|---|---|
| `VITE_API_URL` | `http://localhost:8000` | URL base do backend FastAPI |

## Estrutura

```
src/
├── api.js                 # cliente axios + endpoints
├── theme.js               # tokens de cor MongoDB Atlas (LeafyGreen palette)
├── App.jsx                # LeafyGreenProvider + layout + tabs
├── components/
│   ├── Leaf.jsx           # logo folha MongoDB
│   ├── Sidebar.jsx        # navegação + collections + cluster status
│   ├── KpiCard.jsx        # card KPI com top-border colorida
│   └── ProductTable.jsx   # tabela de resultados + bloco MQL
└── tabs/
    ├── AtlasSearch.jsx    # busca textual (autocomplete, fuzzy, highlight)
    ├── SearchVsVector.jsx # comparação lado a lado + RRF
    ├── HybridRRF.jsx      # RRF tunável (sliders) + chart de scores
    └── AiAgent.jsx        # chat ReAct com trace (tool → MQL → resultado)
```

## Notas técnicas

- **React 18** (não 19): os componentes LeafyGreen ainda não suportam React 19.
- **node polyfills**: uma dependência do LeafyGreen usa globais Node (`Buffer`).
  O `vite-plugin-node-polyfills` resolve — sem ele a tela renderiza em branco.

## Build de produção

```bash
npm run build      # gera dist/
npm run preview    # serve o build localmente
```
