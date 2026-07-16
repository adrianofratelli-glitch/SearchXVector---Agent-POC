"""Unit tests for agent.py's pure pipeline builders (no network)."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("MONGODB_URI", "mongodb://localhost/test")
os.environ.setdefault("ANTHROPIC_API_KEY", "test")

from agent import (
    _pipe_busca_semantica, _pipe_buscar_produto, _pipe_comparar_categoria,
    _pipe_produtos_por_faixa_preco, build_tool_pipeline, PIPELINE_BUILDERS,
)


class TestPipeBuscaSemantica(unittest.TestCase):
    def test_uses_vector_search_stage(self):
        pipe = _pipe_busca_semantica("academia em casa")
        self.assertIn("$vectorSearch", pipe[0])
        self.assertEqual(pipe[0]["$vectorSearch"]["query"], "academia em casa")
        self.assertEqual(pipe[0]["$vectorSearch"]["limit"], 10)


class TestPipeBuscarProduto(unittest.TestCase):
    def test_uses_autocomplete_with_fuzzy(self):
        pipe = _pipe_buscar_produto("tenis")
        stage = pipe[0]["$search"]["autocomplete"]
        self.assertEqual(stage["query"], "tenis")
        self.assertEqual(stage["fuzzy"], {"maxEdits": 1})


class TestPipeCompararCategoria(unittest.TestCase):
    def test_filters_by_category_and_in_stock(self):
        pipe = _pipe_comparar_categoria("Eletrônicos", limite=5)
        self.assertEqual(pipe[0]["$match"], {"categoria": "Eletrônicos", "em_estoque": True})
        self.assertEqual(pipe[2]["$limit"], 5)

    def test_default_limit_is_ten(self):
        pipe = _pipe_comparar_categoria("Moda")
        self.assertEqual(pipe[2]["$limit"], 10)


class TestPipeProdutosPorFaixaPreco(unittest.TestCase):
    def test_filters_by_price_range(self):
        pipe = _pipe_produtos_por_faixa_preco("Moda", 50, 200)
        match = pipe[0]["$match"]
        self.assertEqual(match["preco"], {"$gte": 50, "$lte": 200})
        self.assertEqual(match["categoria"], "Moda")


class TestBuildToolPipeline(unittest.TestCase):
    def test_dispatches_to_registered_builder(self):
        pipe = build_tool_pipeline("busca_semantica", {"consulta": "presente"})
        self.assertIn("$vectorSearch", pipe[0])

    def test_unknown_tool_returns_empty_list(self):
        self.assertEqual(build_tool_pipeline("tool_that_does_not_exist", {}), [])

    def test_all_pipeline_builders_registered(self):
        expected = {"busca_semantica", "buscar_produto", "comparar_categoria", "produtos_por_faixa_preco"}
        self.assertEqual(set(PIPELINE_BUILDERS.keys()), expected)


if __name__ == "__main__":
    unittest.main()
