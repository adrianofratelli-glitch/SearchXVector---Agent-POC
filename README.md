# POC de Search & Agente de IA — MongoDB Atlas

A maioria das stacks de e-commerce cola um motor de busca, um banco vetorial, um warehouse de analytics e um armazenamento para a memória do agente. Esta POC roda os quatro só no MongoDB Atlas, sobre um catálogo sintético de 20 milhões de produtos.

Sete abas, uma capacidade do Atlas em cada. Toda tela imprime o MQL que de fato rodou — nada é mockado. Aponte para qualquer dataset via `MONGODB_URI` / `DB_NAME`.

```
React + LeafyGreen  ──axios──►  FastAPI  ──►  MongoDB Atlas
     (:5273)                     (:8200)
```

## A demo, aba por aba

**1. Atlas Search** — full-text sobre o catálogo: autocomplete, fuzzy (`"adidass"` → Adidas), facetas clicáveis via `$searchMeta`, highlight, contagem de matches, `scoreDetails`. Os filtros rodam dentro do `$search` quando o índice permite, então as contagens os refletem; caso contrário a aplicação cai para o outro caminho e avisa.

![Aba Atlas Search: facetas, highlights e contagem total de matches](docs/screenshots/atlas-search.png)

**2. Search vs Vector** — a mesma consulta nos dois motores, lado a lado. O lexical por frase exata retorna **zero** para `"academia em casa"`; a busca vetorial entende a intenção. Cada motor reporta a própria latência.

![Busca lexical retornando zero ao lado da busca vetorial retornando produtos relevantes](docs/screenshots/search-vs-vector.png)

**3. RRF híbrido** — `$rankFusion` nativo (MongoDB 8.1+, fundido no servidor em uma única agregação) ou RRF do lado da aplicação com `k` ajustável, mantido como visão didática. Cai para o fallback com o motivo quando os requisitos do `$rankFusion` não são atendidos.

![Aba híbrida rodando $rankFusion nativo com os ranks por motor](docs/screenshots/hybrid-rrf.png)

**4. Similares** — "mais como este" vetorial a partir da descrição de um produto, com filtros de categoria e estoque rodando *dentro* do `$vectorSearch`, não depois dele.

![Resultados de produtos similares com pré-filtro aplicado dentro do $vectorSearch](docs/screenshots/similares.png)

**5. Analytics** — um pipeline `$facet` rodando várias agregações em paralelo no servidor. O padrão é um `$sample` de 12 mil; alterne para rodar sobre a coleção inteira e comparar os tempos.

![Aba de analytics: agregações $facet paralelas sobre o catálogo](docs/screenshots/analytics.png)

**6. RAG de reviews** — o `$search` encontra o produto mais relevante que tenha reviews, o MongoDB devolve as reviews e o Claude resume estritamente ancorado nesses dados.

**7. Agente de IA** — um agente ReAct em LangGraph com quatro ferramentas MongoDB, memória de longo prazo via `MongoDBSaver` e um trace construído pelas mesmas funções que as ferramentas executam — byte a byte o que rodou.

![Aba do agente de IA com as chamadas de ferramenta e o trace MQL](docs/screenshots/ai-agent.png)

## Coleções

```
POC
├── produtos          20M produtos      — Atlas Search: produtos_search
├── produtos_vector   subconjunto 500K  — Vector Search: produtos_vector (voyage-4, autoEmbed)
│                                       — Atlas Search: produtos_vector_search
├── avaliacoes        reviews           — RAG de reviews + agente
└── checkpoints       memória do LangGraph
```

O subconjunto vetorial de 500 mil é uma decisão de custo/tempo de build, não um limite — é um `$sample` representativo. O índice lexical extra em `produtos_vector` existe porque o `$rankFusion` nativo precisa dos dois sub-pipelines na mesma coleção. A aplicação detecta os índices disponíveis via `$listSearchIndexes` e degrada de forma graciosa.

## Setup

Requer Atlas 8.0+ (8.1+ para o `$rankFusion` nativo), Python 3.11+, Node 18+ e uma chave da Anthropic.

`.env` na raiz do repositório:

```env
MONGODB_URI=mongodb+srv://<user>:<password>@<cluster>.mongodb.net/
DB_NAME=POC
ANTHROPIC_API_KEY=sk-ant-...
```

```bash
python3 setup_search_indexes.py    # uma vez, idempotente; --status para acompanhar o progresso
bash start.sh                      # backend + frontend → http://localhost:5273
```

Portas customizadas: `BACKEND_PORT=8201 FRONTEND_PORT=5274 bash start.sh`. Execução manual: `uvicorn main:app --port 8200` em `backend/`, `npm run dev` em `frontend/`.

## Sinônimos (opcional)

O toggle de sinônimos precisa de um mapeamento chamado `sinonimos_produtos` no `produtos_search`: UI do Atlas → Atlas Search → Synonyms → coleção de origem `sinonimos`, analisador `lucene.portuguese`. Depois insira documentos assim:

```json
[
  { "mappingType": "equivalent", "synonyms": ["notebook", "laptop", "computador portátil"] },
  { "mappingType": "equivalent", "synonyms": ["celular", "smartphone", "telefone"] },
  { "mappingType": "explicit", "input": ["presente"], "synonyms": ["kit", "combo", "caixa"] }
]
```

O índice é reconstruído em cerca de dois minutos; o toggle avisa enquanto a construção está em andamento.

## Stack

React 18 + Vite + LeafyGreen · FastAPI · LangGraph (ReAct) · Claude Sonnet 4.6 · Voyage `voyage-4` via autoEmbed do Atlas · MongoDB Atlas 8.0+.

## Fronteira de produção

As chamadas ao MongoDB e ao LLM têm limites de pool, socket, timeout de modelo e retry; as rotas de IA compartilham um portão de concorrência limitada e retornam 429 sob saturação. Erros de agregação são sanitizados antes de chegar aos clientes. A imagem roda como UID 10001, mas a API não tem autenticação de usuário: coloque-a atrás de um IdP/API gateway, TLS e cotas por tenant antes de qualquer exposição externa.

Os textos da UI estão em português de propósito (público brasileiro). Detalhes dos componentes: [`frontend/README.md`](frontend/README.md) · [`backend/README.md`](backend/README.md).
