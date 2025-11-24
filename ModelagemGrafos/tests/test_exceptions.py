"""
Testes para o modulo de excecoes.
"""

import pytest
from src.graph.exceptions import (
    GraphException,
    InvalidVertexException,
    InvalidEdgeException
)


class TestExceptions:
    """Testes para as excecoes customizadas."""

    def test_graph_exception(self):
        """Testa excecao base."""
        with pytest.raises(GraphException):
            raise GraphException("Erro generico")

    def test_invalid_vertex_exception_simple(self):
        """Testa excecao de vertice invalido com mensagem simples."""
        with pytest.raises(InvalidVertexException) as exc_info:
            raise InvalidVertexException("Vertice invalido")

        assert "Vertice invalido" in str(exc_info.value)

    def test_invalid_vertex_exception_with_params(self):
        """Testa excecao de vertice invalido com parametros."""
        with pytest.raises(InvalidVertexException) as exc_info:
            raise InvalidVertexException(vertex=10, max_vertex=5)

        error_msg = str(exc_info.value)
        assert "10" in error_msg
        assert "5" in error_msg

    def test_invalid_edge_exception(self):
        """Testa excecao de aresta invalida."""
        with pytest.raises(InvalidEdgeException) as exc_info:
            raise InvalidEdgeException("Aresta invalida")

        assert "Aresta invalida" in str(exc_info.value)

    def test_invalid_edge_loop_not_allowed(self):
        """Testa metodo factory para laco nao permitido."""
        exception = InvalidEdgeException.loop_not_allowed(5)

        assert "5" in str(exception)
        assert "Laco" in str(exception) or "laco" in str(exception).lower()

    def test_invalid_edge_not_found(self):
        """Testa metodo factory para aresta nao encontrada."""
        exception = InvalidEdgeException.edge_not_found(3, 7)

        error_msg = str(exception)
        assert "3" in error_msg
        assert "7" in error_msg
        assert "nao existe" in error_msg.lower()

    def test_exception_inheritance(self):
        """Testa hierarquia de heranca das excecoes."""
        assert issubclass(InvalidVertexException, GraphException)
        assert issubclass(InvalidEdgeException, GraphException)
        assert issubclass(GraphException, Exception)
