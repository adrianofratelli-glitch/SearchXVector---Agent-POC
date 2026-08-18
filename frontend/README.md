# Frontend — Search & Vector (React + LeafyGreen)

A interface da POC, construída com React 18 e Vite usando a biblioteca oficial de
componentes da MongoDB (LeafyGreen), consumindo o backend FastAPI via axios.

## Stack

| Camada       | Tecnologia                                                        |
|--------------|-------------------------------------------------------------------|
| Framework de UI | React 18 + Vite                                                |
| Componentes  | `@leafygreen-ui/*` (design system da MongoDB)                     |
| Tipografia   | Outfit + JetBrains Mono (Google Fonts)                            |
| HTTP         | axios                                                             |
| Polyfills    | `vite-plugin-node-polyfills` (Buffer/process para deps do LeafyGreen) |

## Pré-requisitos

- Node 18+ (testado no Node 18–26)
- Backend rodando (veja [`../backend/README.md`](../backend/README.md))

## Rodar junto com o backend

A partir da raiz do repositório:

```bash
bash start.sh        # Sobe o FastAPI :8200 e o Vite :5273, e então verifica os dois
```

## Rodar só o frontend

```bash
npm install
cp .env.example .env        # Ajuste VITE_API_URL se o backend não estiver em localhost:8200
npm run dev                 # http://localhost:5273
```

## Variáveis de ambiente

| Variável       | Padrão                    | Descrição                    |
|----------------|---------------------------|------------------------------|
| `VITE_API_URL` | `http://localhost:8200`   | URL base do backend FastAPI  |

## Estrutura

```
src/
├── api.js                 cliente axios e endpoints
├── theme.js               tokens de cor do MongoDB Atlas e formatadores
├── App.jsx                LeafyGreenProvider, layout e abas
├── components/
│   ├── Leaf.jsx           logo da folha MongoDB
│   ├── Sidebar.jsx        navegação, coleções, status do cluster
│   ├── KpiCard.jsx        segmento da barra de estatísticas
│   └── ProductTable.jsx   tabela de resultados e bloco MQL
└── tabs/
    ├── AtlasSearch.jsx    busca full-text (autocomplete, fuzzy, highlight)
    ├── SearchVsVector.jsx comparação léxica vs semântica
    ├── HybridRRF.jsx      RRF ajustável com gráfico de score
    ├── Similares.jsx      "mais como este" vetorial com pré-filtro
    ├── Analytics.jsx      agregações com $facet
    ├── ReviewsRag.jsx     recuperação e sumarização de reviews
    └── AiAgent.jsx        chat ReAct com trace ferramenta → MQL → resultado
```

## Notas técnicas

- React 18 (não 19): os componentes LeafyGreen ainda não suportam React 19.
- Polyfills do Node: uma dependência do LeafyGreen depende de globais do Node (`Buffer`).
  O `vite-plugin-node-polyfills` fornece esses globais; sem ele a página renderiza em branco.
- Os textos da UI estão intencionalmente em português, já que a demo é voltada a um
  público brasileiro.

## Build de produção

```bash
npm run build      # Gera em dist/
npm run preview    # Serve o build localmente
```
