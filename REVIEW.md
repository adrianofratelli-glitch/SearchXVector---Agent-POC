# Revisão de engenharia e design — search-e-vector-marketplace

## Resultado

browserslist atualizado para 4.28.9 e nanoid para 3.3.18, com metadados transitivos compatíveis.

Branch `review/codex-improvements`, criada de `main` em `7ffa1140a48e12c05cc85db197beaafe6ced3448`. Sem merge, push, troca de biblioteca core, alteração de schema ou dataset.

## Commits de correção

- `892e493 fix: update vulnerable browserslist and nanoid dependencies`

## Commits visible-change

Nenhum.

## Validação

- 17 testes unitários passaram.
- Build de produção passou; análise Ruff E9/F63/F7/F82 com target Python 3.12 passou.
- Browser com APIs bloqueadas: 1440×1000, 768×1024 e 360×800; sem pageerror e sem overflow horizontal no shell inicial; link de salto transfere foco ao conteúdo.
- As 14 cópias de pov-signature.css permanecem idênticas; lang pt-BR confirmado. Nenhuma alteração na camada compartilhada de CSS.
- Auditor de portas passou: registro e configurações alinhados.
- npm audit do lockfile após correções: 0 altos, 0 críticos, 0 moderados e 0 baixos.

## Sugestões não aplicadas e limites

- Sete destinos primários em `frontend/src/App.jsx` excedem os cinco previstos pelo design system. Agrupamento de capacidades mudaria o roteiro já estabelecido; registrado para avaliação de produto.
- Preservados pooling, maxTimeMS e fallback explícito de busca híbrida. Não alterados índices, corpus ou pipeline de ranking.

A verificação visual cobre o shell offline e abas acessíveis sem backend, não todos os estados de dados. Não certifica contraste de cada componente, comportamento touch completo ou toda a navegação com Atlas. Fluxos reais de escrita/carga não foram executados para preservar datasets. Nenhuma comparação de performance foi inventada. Evidências locais: `/tmp/codex-portfolio-review/`.

## Dependências Python

Auditoria do ambiente instalado, não de uma resolução limpa do manifesto; ferramentas de desenvolvimento podem aparecer junto com runtime. Os IDs abaixo não equivalem a exploração confirmada na PoV. Reconciliar versões instaladas/manifests e testar compatibilidade; atualizações core/major ficaram fora desta rodada. Pacotes de ferramenta e componentes extras do venv também não foram alterados fora da branch.

| Pacote instalado | Versão | Advisory | Versões corrigidas informadas |
|---|---|---|---|
| pip | 26.1 | PYSEC-2026-196, PYSEC-2026-3721 | 26.1.2, 26.2 |

## Segredos e compartilhamento

Varredura por padrões de chaves privadas, chaves Anthropic/AWS e URI MongoDB autenticada no histórico Git local alcançável: nenhuma credencial real confirmada; matches encontrados eram placeholders conhecidos. Limite: não é scanner de entropia, não cobre objetos inacessíveis, texto em screenshots nem logs externos.

Nenhum import/referência estática a `_shared/grove_client.py` foi encontrado nesta PoV. Configuração própria de gateway/ambiente não constitui dependência de código desse módulo. `_shared` permaneceu intocado; consumidores externos/dinâmicos não são garantidos por busca estática. Relatório separado: `../REVIEW_SHARED.md`.


## Fechamento final — 2026-09-05

Esta seção atualiza o estado dos achados históricos acima.

- Aplicado/reavaliado: visible-change: sete destinos organizados em quatro categorias primárias; quatro cenários de Busca no segundo nível. Preserva os sete componentes/índices.
- Validação: 17 testes; build; quatro categorias e quatro subitens exercitados, 1440/768/360 sem pageerror/overflow; npm/pip-audit sem achados.
- Propostas e limites restantes: Nenhuma pendência de código adicional segura identificada. Aprovação necessária para agrupamento de navegação (limite de cinco destinos primários do design system). Ranking, corpus, índices, pooling e maxTimeMS preservados.
- pip-audit atual: Nenhum advisory de Python encontrado no ambiente auditado.
- Ambiente: pip 26.2.1 nos ambientes que possuem pip; FinScope mantém uv sem pip. Essa atualização local não altera arquivos de dependências das PoVs.
- `_shared`: nenhum importador estático comprovado nesta PoV; apenas smoke consome o helper no inventário.
