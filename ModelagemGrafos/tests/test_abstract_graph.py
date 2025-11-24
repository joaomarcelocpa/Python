"""
Testes para a classe AbstractGraph.

Como AbstractGraph e uma classe abstrata, criamos uma implementacao
minima concreta apenas para testar os metodos concretos.
"""

import pytest
import numpy as np
from src.graph.abstract_graph import AbstractGraph
from src.graph.exceptions import InvalidVertexException, InvalidEdgeException


class MinimalGraph(AbstractGraph):
    """
    Implementacao minima de AbstractGraph para testes.

    Implementa apenas os metodos abstratos necessarios
    com comportamento basico.
    """

    def __init__(self, num_vertices: int):
        super().__init__(num_vertices)
        self._edges = set()
        self._edge_weights_dict = {}

    def has_edge(self, u: int, v: int) -> bool:
        self._validate_vertex(u)
        self._validate_vertex(v)
        return (u, v) in self._edges

    def add_edge(self, u: int, v: int) -> None:
        self._validate_edge(u, v)
        if (u, v) not in self._edges:
            self._edges.add((u, v))
            self._num_edges += 1
            self._edge_weights_dict[(u, v)] = 0.0

    def remove_edge(self, u: int, v: int) -> None:
        self._validate_vertex(u)
        self._validate_vertex(v)
        if (u, v) in self._edges:
            self._edges.remove((u, v))
            self._num_edges -= 1
            del self._edge_weights_dict[(u, v)]

    def get_vertex_in_degree(self, u: int) -> int:
        self._validate_vertex(u)
        return sum(1 for (_, v) in self._edges if v == u)

    def get_vertex_out_degree(self, u: int) -> int:
        self._validate_vertex(u)
        return sum(1 for (u_edge, _) in self._edges if u_edge == u)

    def set_edge_weight(self, u: int, v: int, weight: float) -> None:
        self._validate_vertex(u)
        self._validate_vertex(v)
        if (u, v) not in self._edges:
            raise InvalidEdgeException(f"Aresta ({u},{v}) nao existe")
        self._edge_weights_dict[(u, v)] = weight

    def get_edge_weight(self, u: int, v: int) -> float:
        self._validate_vertex(u)
        self._validate_vertex(v)
        if (u, v) not in self._edges:
            raise InvalidEdgeException(f"Aresta ({u},{v}) nao existe")
        return self._edge_weights_dict[(u, v)]

    def is_connected(self) -> bool:
        # Implementacao simplificada
        return self._num_vertices > 0 and self._num_edges > 0

    def get_successors(self, u: int) -> list:
        self._validate_vertex(u)
        return [v for (u_edge, v) in self._edges if u_edge == u]

    def get_predecessors(self, u: int) -> list:
        self._validate_vertex(u)
        return [u_edge for (u_edge, v) in self._edges if v == u]


class TestAbstractGraph:
    """Testes para metodos concretos de AbstractGraph."""

    def test_initialization(self):
        """Testa inicializacao basica."""
        g = MinimalGraph(5)
        assert g.get_vertex_count() == 5
        assert g.get_edge_count() == 0
        assert g.num_vertices == 5
        assert g.num_edges == 0

    def test_initialization_invalid(self):
        """Testa inicializacao com numero invalido de vertices."""
        with pytest.raises(ValueError):
            MinimalGraph(-1)

    def test_vertex_weights(self):
        """Testa operacoes com pesos de vertices."""
        g = MinimalGraph(3)

        # Peso inicial deve ser 0
        assert g.get_vertex_weight(0) == 0.0

        # Define peso
        g.set_vertex_weight(0, 5.5)
        assert g.get_vertex_weight(0) == 5.5

        # Define peso negativo
        g.set_vertex_weight(1, -3.2)
        assert g.get_vertex_weight(1) == -3.2

    def test_vertex_weights_invalid_vertex(self):
        """Testa pesos com vertice invalido."""
        g = MinimalGraph(3)

        with pytest.raises(InvalidVertexException):
            g.set_vertex_weight(10, 5.0)

        with pytest.raises(InvalidVertexException):
            g.get_vertex_weight(-1)

    def test_vertex_labels(self):
        """Testa operacoes com rotulos de vertices."""
        g = MinimalGraph(3)

        # Label inicial deve ser None
        assert g.get_vertex_label(0) is None

        # Define label
        g.set_vertex_label(0, "vertex_A")
        assert g.get_vertex_label(0) == "vertex_A"

        # Substitui label
        g.set_vertex_label(0, "new_label")
        assert g.get_vertex_label(0) == "new_label"

    def test_vertex_labels_invalid_vertex(self):
        """Testa labels com vertice invalido."""
        g = MinimalGraph(3)

        with pytest.raises(InvalidVertexException):
            g.set_vertex_label(5, "label")

        with pytest.raises(InvalidVertexException):
            g.get_vertex_label(-2)

    def test_is_successor(self):
        """Testa metodo is_successor."""
        g = MinimalGraph(3)
        g.add_edge(0, 1)

        assert g.is_successor(0, 1) is True
        assert g.is_successor(1, 0) is False

    def test_is_predecessor(self):
        """Testa metodo is_predecessor."""
        g = MinimalGraph(3)
        g.add_edge(0, 1)

        assert g.is_predecessor(0, 1) is True
        assert g.is_predecessor(1, 0) is False

    def test_is_divergent(self):
        """Testa deteccao de arestas divergentes."""
        g = MinimalGraph(4)
        g.add_edge(0, 1)
        g.add_edge(0, 2)

        # Mesma origem, destinos diferentes
        assert g.is_divergent(0, 1, 0, 2) is True

        # Origens diferentes
        g.add_edge(1, 2)
        assert g.is_divergent(0, 1, 1, 2) is False

    def test_is_divergent_invalid_edge(self):
        """Testa is_divergent com aresta inexistente."""
        g = MinimalGraph(4)
        g.add_edge(0, 1)

        with pytest.raises(InvalidEdgeException):
            g.is_divergent(0, 1, 2, 3)  # Aresta (2,3) nao existe

    def test_is_convergent(self):
        """Testa deteccao de arestas convergentes."""
        g = MinimalGraph(4)
        g.add_edge(0, 2)
        g.add_edge(1, 2)

        # Mesmo destino, origens diferentes
        assert g.is_convergent(0, 2, 1, 2) is True

        # Destinos diferentes
        g.add_edge(0, 1)
        assert g.is_convergent(0, 1, 0, 2) is False

    def test_is_incident(self):
        """Testa incidencia vertice-aresta."""
        g = MinimalGraph(4)
        g.add_edge(0, 1)

        # Vertice e origem
        assert g.is_incident(0, 1, 0) is True

        # Vertice e destino
        assert g.is_incident(0, 1, 1) is True

        # Vertice nao e incidente
        assert g.is_incident(0, 1, 2) is False

    def test_is_incident_invalid_edge(self):
        """Testa is_incident com aresta inexistente."""
        g = MinimalGraph(4)

        with pytest.raises(InvalidEdgeException):
            g.is_incident(0, 1, 2)

    def test_is_empty_graph(self):
        """Testa deteccao de grafo vazio."""
        g = MinimalGraph(3)

        # Grafo sem arestas e vazio
        assert g.is_empty_graph() is True

        # Adiciona aresta
        g.add_edge(0, 1)
        assert g.is_empty_graph() is False

        # Remove aresta
        g.remove_edge(0, 1)
        assert g.is_empty_graph() is True

    def test_is_complete_graph(self):
        """Testa deteccao de grafo completo."""
        g = MinimalGraph(3)

        # Grafo sem arestas nao e completo
        assert g.is_complete_graph() is False

        # Adiciona todas as arestas necessarias: 3 * (3-1) = 6
        g.add_edge(0, 1)
        g.add_edge(0, 2)
        g.add_edge(1, 0)
        g.add_edge(1, 2)
        g.add_edge(2, 0)
        g.add_edge(2, 1)

        assert g.is_complete_graph() is True

    def test_is_complete_graph_single_vertex(self):
        """Testa grafo completo com 1 vertice."""
        g = MinimalGraph(1)
        assert g.is_complete_graph() is True

    def test_validate_vertex(self):
        """Testa validacao de vertices."""
        g = MinimalGraph(3)

        # Vertices validos nao devem lancar excecao
        g._validate_vertex(0)
        g._validate_vertex(1)
        g._validate_vertex(2)

        # Vertices invalidos devem lancar excecao
        with pytest.raises(InvalidVertexException):
            g._validate_vertex(-1)

        with pytest.raises(InvalidVertexException):
            g._validate_vertex(3)

    def test_validate_edge(self):
        """Testa validacao de arestas."""
        g = MinimalGraph(3)

        # Aresta valida nao deve lancar excecao
        g._validate_edge(0, 1)

        # Laco deve lancar excecao
        with pytest.raises(InvalidEdgeException):
            g._validate_edge(0, 0)

        # Vertices invalidos devem lancar excecao
        with pytest.raises(InvalidVertexException):
            g._validate_edge(-1, 0)

        with pytest.raises(InvalidVertexException):
            g._validate_edge(0, 5)

    def test_str_representation(self):
        """Testa representacao em string."""
        g = MinimalGraph(5)
        g.add_edge(0, 1)

        str_repr = str(g)
        assert "MinimalGraph" in str_repr
        assert "5" in str_repr  # numero de vertices
        assert "1" in str_repr  # numero de arestas

    def test_repr_representation(self):
        """Testa representacao oficial."""
        g = MinimalGraph(3)

        repr_str = repr(g)
        assert "MinimalGraph" in repr_str
        assert "3" in repr_str
