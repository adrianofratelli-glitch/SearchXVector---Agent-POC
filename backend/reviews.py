"""
reviews.py — RAG over real product reviews.
Finds the product, pulls its reviews from MongoDB, and the LLM summarizes them.
The prompt is kept in Portuguese on purpose, since the summary is shown in the UI.
"""

import logging
from langchain_anthropic import ChatAnthropic
from atlas import get_product_and_reviews

logger = logging.getLogger("searchxvector.reviews")

_llm = ChatAnthropic(model="claude-sonnet-4-6", temperature=0)

PROMPT = """Você é um analista de avaliações de e-commerce. Com base APENAS nas avaliações
reais abaixo, escreva um resumo conciso em português sobre o produto "{produto}".

Estruture assim:
- **Sentimento geral**: (positivo/misto/negativo) + 1 frase
- **Pontos positivos**: 2-3 bullets
- **Pontos de atenção**: 1-2 bullets (se houver)

Não invente informação que não esteja nas avaliações. Seja objetivo.

AVALIAÇÕES:
{reviews}
"""


def summarize_reviews(query: str) -> dict:
    data = get_product_and_reviews(query, n_reviews=10)
    if data.get("error") or not data.get("produto"):
        return {"error": data.get("error", "Produto não encontrado"), "produto": None}

    produto = data["produto"]
    reviews = data["reviews"]
    via = data.get("via")
    pipeline = data.get("pipeline")
    if not reviews:
        return {"produto": produto, "reviews": [], "summary": "Este produto ainda não tem avaliações.",
                "nota_media": produto.get("avaliacao_media", 0), "via": via, "pipeline": pipeline}

    reviews_txt = "\n".join(
        f'[{r["nota"]}★] "{r.get("titulo","")}" — {r.get("texto","")} (útil: {r.get("util_count",0)})'
        for r in reviews
    )
    msg = PROMPT.format(produto=produto["nome"], reviews=reviews_txt)
    try:
        resp = _llm.invoke(msg)
    except Exception:
        logger.exception("review summarization LLM call failed produto=%s", produto.get("nome"))
        return {"produto": produto, "reviews": reviews,
                "summary": "Não foi possível gerar o resumo agora. Tente novamente em instantes.",
                "nota_media": produto.get("avaliacao_media", 0), "via": via, "pipeline": pipeline}
    summary = resp.content if isinstance(resp.content, str) else \
        " ".join(b.get("text", "") for b in resp.content if isinstance(b, dict))

    notas = [r["nota"] for r in reviews]
    return {
        "produto": produto,
        "summary": summary,
        "reviews": reviews,
        "nota_media": round(sum(notas) / len(notas), 1),
        "total_analisado": len(reviews),
        "via": via,
        "pipeline": pipeline,
    }
