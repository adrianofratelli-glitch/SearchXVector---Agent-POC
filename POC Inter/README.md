# 🏦 Banco Inter × MongoDB Atlas — AI Agent POC

> Demo técnica de AI Agent sobre dados transacionais reais usando **LangGraph + Claude Haiku + Atlas Vector Search (autoEmbed voyage-4) + MongoDB**.

---

## 🎯 Objetivo

Demonstrar como o **MongoDB Atlas** serve como backend completo para aplicações de AI Agents — combinando busca semântica, full-text search, aggregation e memória de longo prazo em uma única plataforma.

---

## 🏗️ Arquitetura

![Architecture](architecture-banco-inter.html)

| Camada | Tecnologia |
|---|---|
| UI | Streamlit (EC2 :8501) |
| AI Agent | LangGraph — ReAct pattern |
| LLM | Claude Haiku 4.5 (Anthropic) |
| Embedding | VoyageAI voyage-4 via **autoEmbed** (sem SDK externo) |
| Banco de dados | MongoDB Atlas 8.0 |
| Memória | MongoDBSaver — checkpoints por `thread_id` |
| Infra | AWS EC2 m5.2xlarge — systemd auto-start |

---

## 🚀 Features demonstradas

### 🔍 Tab 1 — Atlas Search
- Full-text search com **autocomplete** e **fuzzy matching** (maxEdits: 1)
- **Facets** por segmento e categoria MCC
- **Highlight** dos termos encontrados
- Ordenação por relevância, maior e menor valor
- Collections: `transacoes` (71M docs) e `fatura`

### ⚡ Tab 2 — Search vs Vector
- Comparação lado a lado: **busca por palavra-chave** vs **busca semântica**
- Demonstra o gap: "alimentação" → Atlas Search retorna zero; Vector Search retorna SUPERMERCADO, IFOOD, ATACADISTA
- Evidencia o valor do **autoEmbed** (query string → embedding → ANN search, tudo no Atlas)

### 🤖 Tab 3 — AI Agent
- LangGraph ReAct Agent com 4 ferramentas MongoDB:
  - `busca_semantica` — `$vectorSearch` em `transacoes_sample`
  - `buscar_por_estabelecimento` — `$search` autocomplete + fuzzy
  - `analisar_conta` — `$match` + `$group` + `$sort` por account
  - `top_gastos_segmento` — `$match` segmento + `$sort` por valor
- **Memória de longo prazo** via `MongoDBSaver` — histórico gravado em `banco_inter.checkpoints`
- Cada sessão identificada por `thread_id` — persiste entre restarts da EC2

---

## 🗄️ Collections no Atlas

```
banco_inter
├── transacoes          → 71M docs — idx: segmento, account_number, amos_mt_desc
├── transacoes_sample   → Vector Search index HNSW — voyage-4 1024d (autoEmbed)
├── fatura              → Atlas Search index: autocomplete + fuzzy + facets
└── checkpoints         → Memória de longo prazo do LangGraph
```

---

## ⚙️ Setup

### Pré-requisitos
- AWS EC2 m5.2xlarge (ou superior)
- MongoDB Atlas cluster com MongoDB 8.0+
- Conta Anthropic (Claude Haiku)
- Python 3.11+

### Instalação

```bash
git clone https://github.com/adrianofratelli-glitch/SearchXVector---Agent-POC.git
cd SearchXVector---Agent-POC

pip install -r requirements.txt
```

### Variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
MONGODB_URI=mongodb+srv://<user>:<password>@<cluster>.mongodb.net/
DB_NAME=banco_inter
ANTHROPIC_API_KEY=sk-ant-...
```

### Executar

```bash
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

Ou via systemd (auto-start):

```bash
sudo systemctl enable streamlit-inter
sudo systemctl start streamlit-inter
```

---

## 🔑 Por que MongoDB para AI Agents?

| Necessidade | Solução MongoDB Atlas |
|---|---|
| Busca semântica | Vector Search + autoEmbed (sem pipeline de embedding externo) |
| Busca textual | Atlas Search — autocomplete, fuzzy, facets, highlight |
| Análise transacional | Aggregation Framework — $match, $group, $sort, $lookup |
| Memória do agente | MongoDBSaver — checkpoints nativos do LangGraph |
| Escalabilidade | 71M+ documentos com latência < 10ms por query |

> **autoEmbed** elimina a necessidade de um serviço de embedding separado — a query string é enviada diretamente ao `$vectorSearch` e o Atlas gera o vetor internamente usando VoyageAI voyage-4.

---

## 📁 Estrutura do projeto

```
.
├── app.py                        # Aplicação principal Streamlit + LangGraph
├── architecture-banco-inter.html # Diagrama de arquitetura
├── .env                          # Variáveis de ambiente (não commitado)
└── README.md
```

---

## 🛠️ Stack completa

![MongoDB Atlas](https://img.shields.io/badge/MongoDB%20Atlas-8.0-00ED64?style=flat&logo=mongodb&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-ReAct-7C6DD8?style=flat)
![Claude](https://img.shields.io/badge/Claude-Haiku%204.5-FF6B4A?style=flat)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-EC2%20m5.2xlarge-232F3E?style=flat&logo=amazon-aws)

---

*POC desenvolvida para demonstração técnica — Solutions Architect MongoDB Brasil — 2026*
