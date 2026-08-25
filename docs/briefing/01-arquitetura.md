# Atlas Search × Vector Search — arquitetura e princípios

> Primeira das três partes do briefing desta PoV. Aqui está a tese, a arquitetura e os dois padrões que sustentam tudo. Coleções, índices e pipelines em `02-mongodb.md`; tela e roteiro em `03-interface-fluxos.md`.

---

## O que eu quero construir

Um PoC de **Atlas Search e Vector Search sobre um catálogo sintético de marketplace**, cobrindo: busca full-text, busca semântica, ranqueamento híbrido (`$rankFusion` nativo **e** RRF do lado da aplicação), analytics, RAG sobre avaliações e um agente ReAct em LangGraph. Sete abas no frontend, uma por capacidade.

A tese: **você não precisa de um motor de busca separado do banco, nem de um vector DB separado do motor de busca.** Os três são o mesmo cluster, e as sete abas provam isso capacidade por capacidade.

## Arquitetura

```
frontend/src/tabs/*.jsx ──axios (src/api.js)──► backend/main.py (rotas + Pydantic)
                                                   ├── atlas.py          todos os pipelines MongoDB
                                                   ├── agent.py          agente ReAct LangGraph
                                                   ├── reviews.py        sumarização RAG
                                                   └── observability.py  log estruturado + /api/metrics
```

**Todos os pipelines MongoDB moram em `atlas.py`.** Não espalha agregação por rota — quando eu precisar mostrar uma query pro cliente, quero abrir um arquivo só.

O agente LangGraph e o checkpointer do MongoDB são inicializados **preguiçosamente, na primeira requisição de agente**. Mantém os imports de módulo livres de efeito colateral: teste unitário, linter e endpoint não-agêntico **não podem exigir conexão com o Atlas**.

`AI_MAX_CONCURRENCY` é um semáforo compartilhado entre `/agent` e `/reviews-rag`; saturado, responde **429** em vez de enfileirar. Numa demo, requisição de LLM presa é pior que requisição recusada — pelo menos a recusa eu explico.

Portas: backend `:8200`, frontend `:5273`.

## Padrão central 1 — degradação graciosa

O backend **inspeciona os índices vivos** via `$listSearchIndexes`, com cache de TTL 60s, e se adapta no momento da requisição em vez de assumir estado de índice.

Duas adaptações concretas:

- **`search_filter_caps()`** — checa se `categoria`, `preco` e `em_estoque` têm os tipos certos no índice (`token`/`number`/`boolean`). Se têm, os filtros rodam **dentro do `$search`** (`compound.filter`). Se não têm, cai pra `$match` posterior e **sinaliza isso na resposta** — campo por campo, não tudo ou nada.
- **`hybrid_native()`** — cai pra RRF na aplicação, **com o motivo declarado**, quando os requisitos do `$rankFusion` não estão atendidos: ou o índice lexical não existe em `produtos_vector` (e a mensagem diz exatamente isso e onde criar), ou o servidor não conhece o estágio (Atlas 8.1+), e aí a mensagem carrega o erro do próprio servidor.

**Ao adicionar qualquer feature, retorna qual caminho executou — não só os resultados.** Um PoC que esconde que caiu no fallback está mentindo por omissão, e mentira desse tipo é descoberta na pergunta seguinte do cliente.

A diferença entre filtro dentro do `$search` e `$match` posterior vale explicar em cena, porque é técnica de verdade: **com filtro dentro do `$search`, a contagem de matches (`$$SEARCH_META.count.total`) reflete o filtro.** Com `$match` posterior, você filtra o que já veio ranqueado — a contagem mente e a paginação piora.

O `safe_aggregate` devolve `(resultados, erro)` em vez de estourar, com `maxTimeMS` de 10s, e o erro é sanitizado antes de chegar na UI. Erro cru de driver na tela do cliente é vazamento de detalhe de infraestrutura e, pior, é feio.

## Padrão central 2 — transparência de MQL

**Todo endpoint retorna o pipeline que executou, junto com os resultados. A UI renderiza.**

E o detalhe que faz isso valer alguma coisa: no agente, as ferramentas e o construtor de pipeline compartilham as **mesmas funções `_pipe_*`**, então o trace mostrado na UI é **byte a byte** o que rodou. Não é uma reconstrução aproximada pra exibição.

Regra ao mexer: mantém as funções de construção de pipeline **puras e compartilhadas entre execução e exibição**. No instante em que existirem duas versões — uma que roda e uma que aparece — o trace vira ficção.

Vai além do pipeline, aliás. A busca lexical pede `scoreDetails: true` e `highlight`, e projeta os dois pra tela. Assim a pergunta "por que esse produto ficou em primeiro?" tem resposta do próprio servidor, não uma explicação minha.

## O agente ReAct

LangGraph com `create_react_agent`, quatro ferramentas (`busca_semantica`, `buscar_produto`, `comparar_categoria`, `produtos_por_faixa_preco`), e `checkpoints` no próprio Atlas chaveado por `thread_id` — continuidade de conversa persistida no banco, sem estado em memória de processo. Isso é demonstrável: faço uma pergunta de continuidade e ela funciona.

As ferramentas constroem pipelines MQL reais, usando as mesmas funções `_pipe_*` que a exibição usa (`build_tool_pipeline` lê do mesmo dicionário). Nada de ferramenta que devolve resposta pronta.

E as ferramentas **degradam igual às abas**: `_index_ready()` checa se o índice existe e está `queryable` antes de rodar, e devolve uma mensagem legível ao modelo em vez de deixar um erro cru do PyMongo chegar no LLM. Erro de driver dentro do contexto do modelo produz uma resposta alucinada sobre infraestrutura, que é o pior tipo de resposta.

Os docstrings das tools e o system prompt ficam **em português**, porque são eles que dirigem a escolha de ferramenta e o idioma da resposta. O histórico é aparado (`_trim_history`) e o consumo de tokens é contabilizado (`_track_usage`).

## Como rodar

```bash
bash start.sh          # backend :8200 + frontend :5273
                       # recusa porta ocupada, espera /health
                       # logs em /tmp/poc-backend.log e /tmp/poc-frontend.log

BACKEND_PORT=8201 FRONTEND_PORT=5274 bash start.sh
```

Isolados:

```bash
cd backend && uvicorn main:app --reload --port 8200   # docs em /docs
cd frontend && npm run dev                            # VITE_API_URL aponta pro backend
cd frontend && npm run lint && npm run build
```

Setup de índices no Atlas, uma vez e **idempotente**: `python3 setup_search_indexes.py` (e `--status`). Geração de dados: `python3 populate_marketplace.py`.

Testes: `cd backend && python -m unittest discover -s tests -v` — **lógica pura, sem Atlas nem Anthropic ao vivo**. Cobrem os construtores de pipeline do agente (o contrato de "o que roda é o que aparece"), os modelos de request e a observabilidade. Se um teste começar a exigir cluster, ele saiu do lugar dele.

Docker em container único, nginx + uvicorn, rodando non-root e com CSP no nginx.

`.env` na raiz: `MONGODB_URI`, `DB_NAME` (default `POC`), `ANTHROPIC_API_KEY` — essa última só necessária pro agente e pro RAG. Pool e timeouts do Mongo, e timeout/retries da Anthropic, também vêm de env.

Diferente das minhas outras PoVs, aqui o frontend fala **direto** com a URL do backend via `VITE_API_URL`, sem proxy do Vite. Mudou a porta do backend, muda a variável — não o código. O CORS do backend é uma lista explícita (`CORS_ORIGINS`), não `*`.

## Como quero que você trabalhe

- Textos de UI em português (público brasileiro); código, comentários e documentação em inglês. Nome de coleção e de campo em português (`produtos`, `avaliacoes`, `preco`, `categoria`) — é o vocabulário do cliente.
- Todo endpoint devolve o pipeline. Sem exceção.
- Todo fallback é declarado na resposta e visível na tela. Sem exceção.
- Nada de import com efeito colateral. O linter e os testes rodam sem cluster.
- Se você precisar duplicar uma função de construção de pipeline pra exibição, para — é sinal de que a arquitetura escorregou.
- Erro de driver é sanitizado antes de chegar na UI.

## Ordem de trabalho

1. Geração do catálogo sintético e das avaliações.
2. `setup_search_indexes.py` idempotente, e o `--status` funcionando.
3. `atlas.py` com os pipelines de busca lexical, com o `$listSearchIndexes` e a introspecção de capacidades já dentro.
4. Busca vetorial sobre o subset, com autoEmbed.
5. Híbrida: primeiro o RRF da aplicação (que sempre funciona), **depois** o `$rankFusion` nativo com detecção de requisito e fallback.
6. Analytics com `$facet`.
7. RAG de avaliações, com o cache do subconjunto avaliado.
8. Agente LangGraph, com as funções `_pipe_*` compartilhadas desde o primeiro commit.
9. Observabilidade.
10. Frontend, aba por aba, com o `MqlBlock` desde a primeira.

O RRF da aplicação antes do nativo é deliberado: assim o fallback é o caminho testado e maduro, não um plano B escrito às pressas.

## Fronteiras do PoC

- Catálogo sintético, não dado de cliente.
- Vetorial e híbrida rodam sobre o subset de 500K, não sobre os 20M — **dito na tela**.
- O RAG responde sobre o subconjunto de produtos que tem avaliação.
- Sem autenticação nos endpoints.
- Métricas em processo, resetam no restart.
- Os testes cobrem lógica pura; a verificação de comportamento de busca depende do Atlas ao vivo.
