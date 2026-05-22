# POC Banco Inter × MongoDB Atlas

Demo técnica de **Atlas Search**, **Vector Search** e **AI Agent** sobre dados transacionais reais do Banco Inter.

---

## Arquitetura

```
┌─────────────────────────────────────────────┐
│           Streamlit (EC2 :8501)             │
│  Tab 1: Atlas Search  |  Tab 2: Search vs   │
│  Tab 3: AI Agent (LangGraph + Ollama)        │
└──────────────┬──────────────────────────────┘
               │
┌──────────────▼──────────────────────────────┐
│           MongoDB Atlas M10/M30             │
│  banco_inter.fatura       (~44M docs)        │
│  banco_inter.transacoes   (~27M docs)        │
│  banco_inter.transacoes_sample (50K docs)    │
│  banco_inter.checkpoints  (memória agente)   │
│                                             │
│  Índices:                                   │
│  • Search "Fatura"       (fatura)            │
│  • Search "transacoes"   (transacoes)        │
│  • Vector "transacoes_vector" (autoEmbed     │
│    voyage-4 em transacoes_sample)            │
└─────────────────────────────────────────────┘
```

---

## Pré-requisitos

| Recurso | Detalhe |
|---|---|
| EC2 | Amazon Linux 2023 — qualquer instância (`t3.medium` é suficiente) |
| IAM Role | `ec2-inter` com `AmazonSSMManagedInstanceCore` + `AmazonS3ReadOnlyAccess` |
| MongoDB Atlas | Cluster M10+ com collections importadas |
| S3 | Bucket com os JSONLs dos dados |

---

## Setup (nova EC2)

```bash
# 1. Clone o repositório
git clone https://github.com/<seu-usuario>/poc-inter-mongodb.git
cd poc-inter-mongodb

# 2. Configure as credenciais
cp .env.example .env
nano .env   # preencha MONGODB_URI com sua connection string

# 3. Execute o setup completo
bash setup.sh
```

---

## Iniciar a POC

```bash
bash start.sh
```

Acesse em: `http://<IP-PÚBLICO-DA-EC2>:8501`

> **Lembrete:** toda vez que religar a VM, o IP público muda.
> Atualize no **Atlas Network Access** e no **Security Group** (porta 8501).

---

## Funcionalidades

### 🔍 Tab 1 — Atlas Search
- Full-text search com **autocomplete** e **fuzzy matching**
- **Highlight** do termo buscado nos resultados
- **Facets** por segmento (s1/s2/s3/s4)
- Ordenação por Relevância, Maior Valor ou Menor Valor
- Suporte às collections `fatura` e `transacoes`

### ⚡ Tab 2 — Search vs Vector Search
- Comparação lado a lado entre busca por palavra-chave e busca semântica
- Demonstra a diferença: `"alimentação"` → Atlas Search não acha nada, Vector Search acha IFOOD

### 🤖 Tab 3 — AI Agent
- LangGraph + **Claude claude-sonnet-4-6** via API Anthropic
- Tools: busca semântica, análise de conta, top gastos por segmento
- **Memória persistida** no MongoDB (`banco_inter.checkpoints`)
- Embeddings gerados pelo modelo **voyage-4** hospedado no Atlas (autoEmbed)

---

## Índices necessários no Atlas

### Atlas Search — `fatura` (nome: `Fatura`)
```json
{
  "mappings": {
    "dynamic": false,
    "fields": {
      "amss_mt_desc":          [{"type": "string", "analyzer": "lucene.standard"}, {"type": "autocomplete"}],
      "amss_mt_rpt_desc":      {"type": "string"},
      "amss_mt_category_code": {"type": "stringFacet"},
      "segmento":              {"type": "stringFacet"},
      "amss_mt_amount":        {"type": "number"}
    }
  }
}
```

### Atlas Search — `transacoes` (nome: `transacoes`)
```json
{
  "mappings": {
    "dynamic": false,
    "fields": {
      "amos_mt_desc":          [{"type": "string", "analyzer": "lucene.standard"}, {"type": "autocomplete"}],
      "amos_mt_category_code": {"type": "stringFacet"},
      "segmento":              {"type": "stringFacet"},
      "amos_mt_amount":        {"type": "number"}
    }
  }
}
```

### Vector Search — `transacoes_sample` (nome: `transacoes_vector`)
```json
{
  "fields": [
    {"type": "autoEmbed", "modality": "text", "path": "amos_mt_desc", "model": "voyage-4"},
    {"type": "filter", "path": "segmento"}
  ]
}
```

### Criar `transacoes_sample` (50K docs)
```js
use banco_inter
db.transacoes.aggregate([
  { "$sample": { "size": 50000 } },
  { "$out": "transacoes_sample" }
])
```

---

## Popular o Performance Advisor / Profiler

```bash
source venv/bin/activate   # ou pip install pymongo
python populate_profiler.py
```

Antes de rodar, ative o **Profiler** no Atlas UI com threshold `0ms`.

---

## Variáveis de ambiente

| Variável | Descrição |
|---|---|
| `MONGODB_URI` | Connection string Atlas (`mongodb+srv://...`) |
| `DB_NAME` | Nome do banco (padrão: `banco_inter`) |
| `ANTHROPIC_API_KEY` | Chave da API Anthropic (`sk-ant-...`) |

---

## Estrutura do repositório

```
poc-inter-mongodb/
├── app.py                  # Aplicação Streamlit principal
├── populate_profiler.py    # Script para popular Performance Advisor
├── requirements.txt        # Dependências Python
├── setup.sh                # Bootstrap para nova EC2
├── start.sh                # Iniciar a POC
├── .env.example            # Template de variáveis de ambiente
├── .gitignore
└── README.md
```
