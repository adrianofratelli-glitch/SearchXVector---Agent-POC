# 🛒 Marketplace × MongoDB Atlas — Search & AI Agent POC

> Demo técnica para demonstrar **Atlas Search · Vector Search · Hybrid RRF · AI Agent** usando um catálogo de marketplace com **20M+ documentos** sintéticos.

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
- **Facets** por categoria, faixa de preço, estoque
- **Highlight** dos termos encontrados
- **Compound query** — boost no `nome`, full-text na `descricao`

### ⚡ Tab 2 — Search vs Vector
- Comparação lado a lado: **palavra-chave** vs **significado semântico**
- O gap WOW: `"academia em casa"` → Atlas Search retorna zero; Vector Search retorna halteres, whey, kettlebell
- Demonstra o valor do **autoEmbed** — query string direto no `$vectorSearch`

### 🔀 Tab 3 — Hybrid RRF
- Combina Atlas Search + Vector Search via **Reciprocal Rank Fusion**
- `score_rrf = Σ 1 / (k + rank_i)` com k ajustável
- Mostra origem de cada resultado: só Search, só Vector, ou nos dois 🏆
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

*POC desenvolvida para demonstração técnica — Solutions Architect MongoDB Brasil — 2026*
