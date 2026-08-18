# Atlas Search × Vector Search — prompt de construção

> Esse é o briefing que eu entrego **antes de existir uma linha de código**. Não é documentação do que existe: é o que eu daria pra alguém (ou pro Claude) subir a PoV inteira do zero.

Um PoC de Atlas Search e Vector Search sobre um catálogo sintético de marketplace: full-text, semântica, híbrida (`$rankFusion` nativo **e** RRF na aplicação), analytics, RAG de avaliações e um agente ReAct em LangGraph. Sete abas, uma por capacidade. Backend FastAPI em `:8200`, frontend Vite/React/LeafyGreen em `:5273`, database `POC`.

A tese: **você não precisa de um motor de busca separado do banco, nem de um vector DB separado do motor de busca.**

| Arquivo | O que responde |
|---|---|
| [`docs/prompts/01-arquitetura.md`](docs/prompts/01-arquitetura.md) | tese, arquitetura de módulos, degradação graciosa, transparência de MQL, o agente ReAct, como rodar, fronteiras |
| [`docs/prompts/02-mongodb.md`](docs/prompts/02-mongodb.md) | as duas coleções e o porquê, definições de índice, score de negócio, todos os pipelines (`$search`, `$vectorSearch`, `$rankFusion`, `$facet`) |
| [`docs/prompts/03-interface-fluxos.md`](docs/prompts/03-interface-fluxos.md) | as sete abas, `MqlBlock`, badges de fallback, roteiro de demo |

Se for ler só um: o **01**, pelos dois padrões centrais. Sem eles a demo vira "um buscador bonito".
