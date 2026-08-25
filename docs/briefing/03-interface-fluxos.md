# Atlas Search × Vector Search — interface, fluxos e roteiro

> Terceira parte do briefing. As sete abas, o componente que sustenta a demo inteira, e o roteiro que eu preciso conseguir executar no fim.

---
## Estado atual — modo palco

As sete jornadas continuam disponíveis em tabs horizontais compactas. Sidebar,
KPIs globais e texto de enquadramento foram removidos: a tela abre no cenário,
na consulta e no resultado. Status offline continua visível porque altera a
leitura da evidência.

## Contrato visual do portfólio (v2)

Esta UI participa da assinatura MongoDB Dark das PoVs. O arquivo
`src/pov-signature.css` é uma cópia sincronizada entre os onze frontends e deve
ser importado **depois** do stylesheet local. O contêiner raiz carrega
`data-pov-shell`, existe um `.pov-skip-link` para `#conteudo-principal` e o
`index.html` declara pt-BR, dark color scheme, theme color e o favicon comum.

A camada compartilhada é dona da document rail, foco, touch targets e redução de
movimento. Este arquivo continua dono do fluxo e das exceções de domínio: não
achate uma tela operacional num template de landing page e não remova a tese
visual específica desta PoV. Qualquer mudança na assinatura precisa ser
replicada nas onze cópias e validada em 1440, 768 e 360 px, além do build de
produção e do estado offline.


## A tese é visual

O PoC tem uma tese só, e ela é visual: **mostrar a query.** Os dois padrões centrais do backend não valem nada se a tela esconder qual caminho executou.

## Stack

React 18 + Vite + LeafyGreen, `axios` pro backend, `react-markdown` pra resposta do agente. Um componente por aba, cliente compartilhado em `src/api.js`, tokens de cor em `src/theme.js`.

Duas restrições que não são preferência minha, são fato:

- **React 18 pinado.** LeafyGreen não suporta React 19; subir a versão quebra o build.
- **`vite-plugin-node-polyfills` é obrigatório.** Uma dependência transitiva do LeafyGreen precisa de `Buffer`/`process`/`global`. Remover **não dá erro de build — dá página em branco**, que é bem pior de diagnosticar.

Sem router. O `App.jsx` guarda um índice e um array `TABS` decide o componente ativo. São sete abas numa demo linear; roteamento aqui seria peso morto.

## As sete abas

| Aba | Componente | Endpoint | O que a tela precisa provar |
|---|---|---|---|
| Busca full-text | `AtlasSearch.jsx` | `POST /search`, `/search/facets` | relevância lexical em 20M docs, filtro **dentro** do `$search`, facetas, `scoreDetails` e highlight |
| Search vs. Vector | `SearchVsVector.jsx` | `POST /compare` | a mesma intenção escrita de outro jeito: a lexical erra (às vezes zero resultado), a vetorial acerta |
| Híbrida | `HybridRRF.jsx` | `POST /hybrid`, `/hybrid-native` | `$rankFusion` nativo com o rank de cada motor por documento, e o fallback de RRF quando os requisitos não estão lá |
| Similares | `Similares.jsx` | `POST /similar` | vizinho semântico a partir de um produto, não de um texto, com pré-filtro dentro do `$vectorSearch` |
| Analytics | `Analytics.jsx` | `GET /analytics` | agregação com `$facet` no servidor, sem trazer dado pra aplicação |
| RAG de avaliações | `ReviewsRag.jsx` | `POST /reviews-rag` | resposta fundamentada nas avaliações que foram de fato recuperadas |
| Agente | `AiAgent.jsx` | `POST /agent` | ReAct com trace fiel: o pipeline exibido é o que rodou |

`GET /stats` continua disponível para preflight e diagnóstico, mas não ocupa uma
sidebar persistente. Durante a apresentação, escala e prontidão aparecem apenas
quando forem relevantes ao cenário ativo.

Na aba híbrida, mostra por documento **em qual dos dois motores ele apareceu e em que posição**, mais a contagem de "só lexical / só vetorial / nos dois". É isso que torna a fusão visível em vez de mágica — e a linha "só vetorial" é o argumento inteiro numa imagem.

## `MqlBlock` — o componente que sustenta a demo

Renderiza o campo `pipeline` que **todo endpoint devolve junto com os resultados**, sempre com a coleção nomeada (`POC.produtos`, `POC.produtos_vector`, `POC.produtos → POC.avaliacoes`).

Aparece em praticamente toda aba. Quem está assistindo copia e roda no Compass.

**Regra ao adicionar aba nova: o endpoint devolve o pipeline, e a aba renderiza o `MqlBlock`. Sem exceção.**

## Badges de fallback

O backend informa qual caminho executou. A UI **tem** que mostrar:

- se o filtro rodou dentro do `$search` ou virou `$match` posterior;
- se o híbrido usou `$rankFusion` nativo ou o RRF da aplicação, e por quê;
- se os sinônimos caíram no fallback (`synonyms_fallback`).

Badge visível custa nada e compra credibilidade. Esconder custa a reunião inteira.

## Timeout e estado offline

60s no cliente axios. Não é chute: `$vectorSearch` sobre o subset com autoEmbed não responde em 5 segundos, e a busca lexical sobre 20M também não, dependendo da query.

E trata o estado `offline` explicitamente — quando o backend está fora, a tela diz isso em vez de ficar carregando pra sempre. Quando o semáforo de IA satura, o backend responde **429**, e a aba mostra "ocupado, tenta de novo" em vez de girar.

## O roteiro que eu preciso conseguir executar no fim

1. **Full-text sobre 20M documentos.** Mostrar a contagem de matches com filtro dentro do `$search`, o `scoreDetails` explicando o ranking, e o pipeline renderizado ao lado.
2. **Ligar e desligar o sinal de negócio** no score e ver o ranking mudar. Relevância é regra, e a regra está na query.
3. **A mesma intenção, escrita de outro jeito.** A lexical erra — às vezes com zero resultado —, a vetorial acerta. Mesmo cluster.
4. **Híbrida** com `$rankFusion` nativo, mostrando o rank de cada motor por documento e quantos vieram só de um lado.
5. **Forçar o fallback** — RRF na aplicação, com o motivo declarado. O PoC nunca finge.
6. **RAG de avaliações**, fundamentado nas avaliações realmente recuperadas.
7. **Agente.** Uma pergunta de negócio, o trace com os pipelines reais, e depois uma pergunta de continuidade no mesmo `thread_id` — o checkpoint no Atlas segurou o contexto.
8. **`/api/metrics`** — contadores e latência por rota.

O passo 5 é o que mais surpreende positivamente. Mostrar o próprio produto degradando com honestidade compra mais confiança do que qualquer número.

## Antes de apresentar

- `setup_search_indexes.py --status` com tudo `READY` — índice de Search demora, e o vetorial com autoEmbed demora mais.
- `/api/stats` confirmando números reais do cluster, não zeros.
- Uma busca de aquecimento em cada aba de IA, pra que o primeiro clique da demo não pague cold start.
