# Atlas Search × Vector Search — MongoDB: coleções, índices e pipelines

> Segunda parte do briefing. Tudo que encosta no Atlas: por que são duas coleções, as definições de índice, e cada pipeline que a demo executa.

---

## Coleções — database `POC`

| Coleção | Tamanho | Índices |
|---|---|---|
| `produtos` | 20 milhões | `produtos_search` (lexical) |
| `produtos_vector` | 500 mil (subset via `$sample`) | `produtos_vector` (vetorial, autoEmbed voyage-4) **+** `produtos_vector_search` (lexical) |
| `avaliacoes` | — | usada pelo RAG e pelo agente |
| `checkpoints` | — | memória do LangGraph (`MongoDBSaver`), chaveada por `thread_id` |

## Duas coleções, por necessidade do `$rankFusion`

Essa é a decisão de modelagem que mais gera pergunta em demo, então deixa explicada na tela e no README.

Por que um índice lexical numa coleção que existe pra busca vetorial? Porque **o `$rankFusion` nativo exige que os dois sub-pipelines rodem na mesma coleção.** Sem o lexical em `produtos_vector`, não existe híbrido nativo — só RRF na aplicação.

O subset de 500K existe porque vetorizar 20M de documentos num PoC não agrega ao argumento e custa caro. A demo de busca lexical roda contra os 20M inteiros; a de vetorial e híbrida, contra o subset. **Isso é dito na tela**, não escondido — se alguém descobrir sozinho, o resto da demo perde crédito.

## Índices — `setup_search_indexes.py`, idempotente

O script **mescla** os tipos desejados na definição viva em vez de sobrescrever: sinônimos, analisadores e qualquer coisa que já esteja no índice são preservados. Roda quantas vezes quiser; `--status` mostra o que está `READY`.

### `produtos_vector` (vectorSearch, coleção `produtos_vector`)

```python
{"fields": [
    {"type": "autoEmbed", "modality": "text", "model": "voyage-4", "path": "descricao"},
    {"type": "filter", "path": "categoria"},
    {"type": "filter", "path": "preco"},
    {"type": "filter", "path": "em_estoque"},
]}
```

autoEmbed: o Atlas gera o embedding no ingest e na query — sem pipeline de embedding do meu lado. Os três `filter` existem pra que o pré-filtro rode **dentro** do `$vectorSearch`.

### `produtos_search` (lexical, coleção `produtos`)

```python
{"mappings": {"fields": {
    "nome": [
        {"type": "autocomplete", "analyzer": "lucene.standard", ...},
        {"type": "string", "analyzer": "lucene.standard"},
    ],
    "descricao":       {"type": "string", "analyzer": "lucene.portuguese"},
    "marca":           {"type": "string"},
    "produto_id":      {"type": "token"},
    "categoria":       [{"type": "stringFacet"}, {"type": "token"}],
    "subcategoria":    {"type": "stringFacet"},
    "genero":          {"type": "stringFacet"},
    "em_estoque":      {"type": "boolean"},
    "preco":           [{"type": "numberFacet"}, {"type": "number"}],
    "avaliacao_media": {"type": "number"},
}},
 "synonyms": [{"name": "sinonimos_produtos", "analyzer": "lucene.standard", ...}]}
```

`lucene.portuguese` na descrição (stemming em pt-BR), `token` e `number` nos campos filtráveis (é isso que permite `compound.filter`), `stringFacet`/`numberFacet` nos facetáveis, e `avaliacao_media` como `number` porque o score de negócio lê esse caminho.

### `produtos_vector_search` (lexical, coleção `produtos_vector`)

Mesmo desenho, versão enxuta — existe **só** para viabilizar o `$rankFusion` nativo.

## Relevância com sinal de negócio

O score da busca lexical não é só relevância de texto: ele **multiplica a relevância pela nota média do produto**, com default 3.0 quando ausente:

```python
{"function": {"multiply": [
    {"score": "relevance"},
    {"path": {"value": "avaliacao_media", "undefined": 3.0}},
]}}
```

Isso é de propósito, e é um argumento por si só: tuning de relevância de e-commerce é regra de negócio, e ela vive na query — não num serviço de reranking separado depois. `boost_business` é alternável, porque mostrar o ranking com e sem o sinal lado a lado é uma das coisas que mais chama atenção de quem trabalha com busca. Desligado, o `nome` cai pra um `boost` fixo de 2.

O operador base é um `compound.should` com `autocomplete` fuzzy (1 edit) em `nome` e `text` fuzzy em `descricao`, `minimumShouldMatch: 1`.

O caminho de sinônimos usa um operador `text` com a coleção `sinonimos_produtos`, e por isso precisa ser **embrulhado num `compound.must`** antes de receber os filtros — operador não-compound não aceita `compound.filter` direto. É o tipo de detalhe que quebra silenciosamente e leva meia hora pra achar. Quando o analisador de sinônimos não está pronto, a resposta traz `synonyms_fallback: true`.

## Pipeline de busca lexical

```python
[{"$search": {
    "index": "produtos_search",
    **search_op,
    "count": {"type": "total"},
    "highlight": {"path": ["nome", "descricao"], "maxCharsToExamine": 500, "maxNumPassages": 1},
    "scoreDetails": True,          # por que esse produto ranqueou aí
 }},
 # {"$match": mql_filter}  ← só quando o índice NÃO suporta o filtro
 {"$limit": 50},
 {"$addFields": {"_total_matches": "$$SEARCH_META.count.total"}},
 {"$project": {"_id": 0, ..., "score": {"$meta": "searchScore"},
               "highlights": {"$meta": "searchHighlights"},
               "scoreDetails": {"$meta": "searchScoreDetails"}, "_total_matches": 1}}]
```

`build_filters()` decide, campo a campo, o que vai pro `compound.filter` (`range` em `preco`, `equals` em `em_estoque`, `in` em `categoria`) e o que sobra pro `$match` — segundo as capacidades lidas do índice vivo.

## Facetas — `$searchMeta`

`search_facets()` roda um `$searchMeta` com `facet` sobre `categoria` (stringFacet) e faixas de `preco` (numberFacet), devolvendo os buckets direto do servidor. Faceta calculada na aplicação sobre uma página de resultados é faceta errada.

## Vetorial

```python
{"$vectorSearch": {"index": "produtos_vector", "path": "descricao",
                   "query": query, "numCandidates": 150, "limit": 10}}
```

`query` como texto puro — o autoEmbed embeda no servidor. `numCandidates` é ~10× o `limit` (regra prática: candidatos demais é latência, de menos é recall ruim).

Em **Similares** (`find_similar`), o vizinho parte de um produto, não de um texto, e o pré-filtro (categoria / em estoque) vai **dentro** do `$vectorSearch`, no campo `filter` — semântica e filtro no mesmo estágio. Projeta `{"$meta": "vectorSearchScore"}`.

## Híbrida — os dois caminhos

### RRF na aplicação (`hybrid_rrf`)

Roda os dois pipelines separados (`$search` em `produtos`, `$vectorSearch` em `produtos_vector`), e funde por `1/(k + rank)` com `k = 60`. Sempre funciona. É o caminho maduro, e por isso é o fallback.

### `$rankFusion` nativo (`hybrid_native`)

```python
[{"$rankFusion": {
    "input": {"pipelines": {
        "textual":   [{"$search": {"index": <lexical de produtos_vector>, "compound": {"should": [
                          {"autocomplete": {"query": q, "path": "nome", "fuzzy": {"maxEdits": 1}}},
                          {"text": {"query": q, "path": "descricao", "fuzzy": {"maxEdits": 1}}}]}}},
                      {"$limit": limit}],
        "semantico": [{"$vectorSearch": {"index": "produtos_vector", "path": "descricao",
                                         "query": q, "numCandidates": limit * 10, "limit": limit}}],
    }},
    "combination": {"weights": {"textual": 1, "semantico": 1}},
    "scoreDetails": True,
 }},
 {"$limit": limit},
 {"$project": {"_id": 0, ..., "score": {"$meta": "score"},
               "scoreDetails": {"$meta": "scoreDetails"}}}]
```

Requisitos: MongoDB **8.1+** e os dois índices na **mesma** coleção. `_parse_rank_fusion_details()` extrai, defensivamente, o rank de cada sub-pipeline por documento — é isso que alimenta a contagem "só lexical / só vetorial / nos dois" da tela.

Faltou requisito → cai no RRF da aplicação **com o motivo escrito na resposta**, incluindo o erro do servidor quando é o caso.

## Analytics — um `$facet` só

```python
{"$facet": {
    "por_categoria": [{"$group": {"_id": "$categoria", "total": {"$sum": 1},
                                  "preco_medio": {"$avg": "$preco"},
                                  "avaliacao_media": {"$avg": "$avaliacao_media"}}},
                      {"$sort": {"total": -1}}],
    "top_marcas":    [{"$group": {"_id": "$marca", "total": {"$sum": 1}}},
                      {"$sort": {"total": -1}}, {"$limit": 8}],
    "faixa_preco":   [{"$bucket": {"groupBy": "$preco",
                                   "boundaries": [0, 100, 500, 1000, 3000, 5000, 10000, 999999],
                                   "default": "outros", "output": {"total": {"$sum": 1}}}}],
    "por_mes":       [{"$match": {"created_at": {"$type": "date"}}},
                      {"$group": {"_id": {"$dateToString": {"format": "%Y-%m", "date": "$created_at"}},
                                  "total": {"$sum": 1}}}, {"$sort": {"_id": 1}}, {"$limit": 12}],
    "geral":         [{"$group": {"_id": None, "total": {"$sum": 1}, "preco_medio": {"$avg": "$preco"},
                                  "desconto_medio": {"$avg": "$desconto_pct"},
                                  "em_estoque": {"$sum": {"$cond": ["$em_estoque", 1, 0]}}}}],
}}
```

Cinco agregações em paralelo, no servidor, numa passada. `full=False` (default de demo) roda sobre um `$sample` de 12 mil docs pra responder instantâneo; `full=True` roda o **mesmo pipeline** sobre os 20M — e essa comparação é a demonstração.

## RAG de avaliações — o detalhe honesto

Só uma parte pequena do catálogo tem avaliação. Se você buscar o produto por texto e depois procurar as avaliações dele, a demo cai numa tela de "0 avaliações" com frequência incômoda.

Então `_get_reviewed()` cacheia (TTL 600s) o subconjunto de produtos **que têm avaliação** e resolve a busca dentro dele. A demo nunca cai no estado vazio, e um recarregamento de dados não exige reiniciar o backend. É uma escolha de apresentação, e ela é honesta desde que dita: o RAG responde sobre produtos avaliados, que é exatamente o caso de uso real.

## Pipelines do agente (`_pipe_*`)

| Função | Coleção | O que faz |
|---|---|---|
| `_pipe_busca_semantica` | `produtos_vector` | `$vectorSearch` sobre `descricao` |
| `_pipe_buscar_produto` | `produtos` | `$search` por nome |
| `_pipe_comparar_categoria` | `produtos` | agregação de comparação por categoria |
| `_pipe_produtos_por_faixa_preco` | `produtos` | filtro de faixa + agregação |

`build_tool_pipeline(tool_name, args)` lê do **mesmo** dicionário que as tools usam. Um só lugar constrói pipeline; execução e exibição consomem dali.

## Introspecção de índices

`get_search_indexes(collection)` → `$listSearchIndexes` com cache de 60s. Em cima dela:

- `get_index_status()` — preflight e diagnóstico de índice (nome, tipo, status).
- `_field_types(index_doc, path)` — quais tipos um campo tem no índice vivo.
- `search_filter_caps()` — as capacidades de filtro, campo a campo.
- `vector_collection_search_index()` — o nome do índice lexical **queryable** em `produtos_vector`, ou `None` (o gatilho do fallback do `$rankFusion`).
