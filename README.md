# 🛒 Search & AI Agent POC — MongoDB Atlas

> Demo técnica para demonstrar **Atlas Search · Vector Search · Hybrid RRF · AI Agent** usando um catálogo de marketplace com **20M+ documentos** sintéticos.
> Configurável para qualquer cliente via variáveis de ambiente (`DB_NAME`, `MONGODB_URI`).

---

## 🎯 Objetivo

Demonstrar como o **MongoDB Atlas** serve como backend completo para aplicações de busca e AI — combinando busca textual, busca semântica, hybrid search e AI Agent com memória em uma única plataforma.

---

## 🏗️ Arquitetura

| Camada | Tecnologia |
|---|---|
| UI | Streamlit |
| AI Agent | LangGraph — ReAct pattern |
| LLM | Claude Haiku 4.5 (Anthropic) |
| Embedding | VoyageAI voyage-4 via **autoEmbed** |
| Banco de dados | MongoDB Atlas 8.0 |
| Memória | MongoDBSaver — checkpoints por `thread_id` |

---

## 🚀 Features demonstradas

### 🔍 Tab 1 — Atlas Search
- **Autocomplete** no nome do produto (edgeGram, minGrams: 2)
- **Fuzzy matching** — `"adidass"` → Adidas, `"samsumg"` → Samsung
- **Facets** por categoria, faixa de preço, estoque (`$searchMeta`)
- **Highlight nativo** — Atlas Search marca os trechos exatos encontrados em `nome` e `descricao`
- **Total de matches** — `$$SEARCH_META.count.total` exibe o universo real de resultados, não só os 50 retornados
- **Compound query** — boost no `nome`, full-text na `descricao`
- **Sinônimos** — toggle ativa o mapeamento `sinonimos_produtos` no índice

### ⚡ Tab 2 — Search vs Vector vs RRF
- Comparação **lado a lado em 3 colunas**: Atlas Search · Vector Search · Hybrid RRF
- O gap WOW: `"academia em casa"` → Atlas Search retorna zero; Vector Search retorna halteres, whey, kettlebell; RRF combina o melhor dos dois
- Demonstra o valor do **autoEmbed** — query string direto no `$vectorSearch`

### 🔀 Tab 3 — Hybrid RRF (aprofundado)
- Combina Atlas Search + Vector Search via **Reciprocal Rank Fusion**
- `score_rrf = Σ 1 / (k + rank_i)` com k ajustável via slider
- Mostra origem de cada resultado: só Search, só Vector, ou nos dois 🏆
- **Chart de scores** — barras comparando as 3 engines para os top 10 resultados
- Sliders para controlar k, quantidade de resultados por engine

### 🤖 Tab 4 — AI Agent
- LangGraph ReAct Agent com 4 ferramentas MongoDB:
  - `busca_semantica` — `$vectorSearch` autoEmbed
  - `buscar_produto` — `$search` autocomplete + fuzzy
  - `comparar_categoria` — `$match` + `$sort` por avaliação
  - `produtos_por_faixa_preco` — `$match` com range de preço
- **Memória de longo prazo** via `MongoDBSaver`
- Cada sessão identificada por `thread_id`

---

## 🗄️ Collections

```
POC (database)
├── produtos          → 20M docs — Atlas Search index: produtos_search
├── produtos_vector   → 500K docs — Vector Search index: produtos_vector (autoEmbed voyage-4)
├── avaliacoes        → 5M docs — reviews dos produtos
└── checkpoints       → Memória do LangGraph Agent
```

---

## 🔥 Queries de demo prontas

### Gap textual vs semântico (momento WOW)
| Query | Atlas Search | Vector Search |
|---|---|---|
| `"academia em casa"` | ❌ 0 resultados | ✅ halteres, whey, kettlebell |
| `"presente dia dos pais"` | ❌ 0 resultados | ✅ perfumes, relógios, livros |
| `"proteção solar rosto"` | ❌ 0 resultados | ✅ protetor solar, hidratante FPS |

### Fuzzy (tolerância a erros)
- `"adidass"` → Adidas
- `"samsumg"` → Samsung
- `"notebokk"` → notebook

### AI Agent
- *"Me recomende um notebook para programação até R$ 3.000"*
- *"Compare os melhores smartphones Samsung vs Apple"*
- *"Preciso de um presente para alguém que gosta de academia"*

---

## ⚙️ Setup

### Pré-requisitos
- MongoDB Atlas cluster 8.0+
- Conta Anthropic (Claude Haiku)
- Python 3.11+

### Instalação

```bash
pip install -r requirements.txt
```

### Variáveis de ambiente

Crie um arquivo `.env`:

```env
MONGODB_URI=mongodb+srv://<user>:<password>@<cluster>.mongodb.net/
DB_NAME=POC
ANTHROPIC_API_KEY=sk-ant-...
```

### Executar localmente

```bash
streamlit run app_marketplace.py
```

### Executar em EC2

```bash
bash setup.sh   # primeira vez
bash start.sh   # sempre que religar
```

---

## 🔤 Configurando Sinônimos no Atlas UI

O toggle **Sinônimos** na Tab 1 usa um mapeamento chamado `sinonimos_produtos` configurado no índice `produtos_search`.

**Passo a passo:**
1. Atlas UI → seu cluster → **Atlas Search** → índice `produtos_search` → **Synonyms** → **Add synonym mapping**
2. Nome: `sinonimos_produtos` · Source collection: `sinonimos` · Analyzer: `lucene.portuguese`
3. Insira os documentos abaixo na collection `sinonimos` (via Atlas UI ou Compass):

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

> **Nota:** após salvar o mapeamento, o índice reconstrói (~2 min). O toggle mostrará uma mensagem de aviso se o índice ainda estiver em `Building`.

---

## 🗂️ Estrutura do projeto

```
.
├── app_marketplace.py     # App principal — Streamlit + LangGraph
├── populate_marketplace.py # Popula 20M docs sintéticos
├── requirements.txt
├── setup.sh               # Bootstrap EC2
├── start.sh               # Start/restart app
└── README.md
```

---

## 🛠️ Stack

![MongoDB Atlas](https://img.shields.io/badge/MongoDB%20Atlas-8.0-00ED64?style=flat&logo=mongodb&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-ReAct-7C6DD8?style=flat)
![Claude](https://img.shields.io/badge/Claude-Haiku%204.5-FF6B4A?style=flat)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-FF4B4B?style=flat&logo=streamlit&logoColor=white)

---

*POC desenvolvida para demonstração técnica — MongoDB Atlas — 2026*
