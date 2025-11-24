"""
Testes para a classe AdjacencyMatrixGraph.

Testa a implementacao concreta de grafos usando matriz de adjacencia,
incluindo todas as operacoes, validacoes e propriedades.
"""

import pytest
import numpy as np
from src.graph.adjacency_matrix_graph import AdjacencyMatrixGraph
from src.graph.exceptions import InvalidVertexException, InvalidEdgeException


class TestAdjacencyMatrixGraph:
    """Testes para AdjacencyMatrixGraph."""

    def test_initialization(self):
        """Testa inicializacao basica."""
        g = AdjacencyMatrixGraph(5)
        assert g.get_vertex_count() == 5
        assert g.get_edge_count() == 0
        assert g.num_vertices == 5
        assert g.num_edges == 0

    def test_initialization_zero_vertices(self):
        """Testa grafo com zero vertices."""
        g = AdjacencyMatrixGraph(0)
        assert g.get_vertex_count() == 0
        assert g.get_edge_count() == 0

    def test_initialization_invalid(self):
        """Testa inicializacao com numero invalido de vertices."""
        with pytest.raises(ValueError):
            AdjacencyMatrixGraph(-1)

    def test_add_edge_basic(self):
        """Testa adicao basica de aresta."""
        g = AdjacencyMatrixGraph(3)

        # Adiciona aresta 0 -> 1
        g.add_edge(0, 1)
        assert g.has_edge(0, 1) is True
        assert g.get_edge_count() == 1

        # Aresta reversa nao existe
        assert g.has_edge(1, 0) is False

    def test_add_edge_idempotent(self):
        """Testa que add_edge e idempotente."""
        g = AdjacencyMatrixGraph(3)

        # Adiciona mesma aresta multiplas vezes
        g.add_edge(0, 1)
        assert g.get_edge_count() == 1

        g.add_edge(0, 1)
        assert g.get_edge_count() == 1  # Nao deve incrementar

        g.add_edge(0, 1)
        assert g.get_edge_count() == 1  # Ainda 1

    def test_add_edge_loop_not_allowed(self):
        """Testa que lacos nao sao permitidos."""
        g = AdjacencyMatrixGraph(3)

        with pytest.raises(InvalidEdgeException):
            g.add_edge(0, 0)

        with pytest.raises(InvalidEdgeException):
            g.add_edge(2, 2)

    def test_add_edge_invalid_vertices(self):
        """Testa adicao de aresta com vertices invalidos."""
        g = AdjacencyMatrixGraph(3)

        # Vertice negativo
        with pytest.raises(InvalidVertexException):
            g.add_edge(-1, 0)

        # Vertice fora dos limites
        with pytest.raises(InvalidVertexException):
            g.add_edge(0, 5)

    def test_has_edge(self):
        """Testa verificacao de existencia de aresta."""
        g = AdjacencyMatrixGraph(4)

        # Inicialmente nenhuma aresta
        assert g.has_edge(0, 1) is False

        # Adiciona aresta
        g.add_edge(0, 1)
        assert g.has_edge(0, 1) is True

        # Outras arestas nao existem
        assert g.has_edge(1, 0) is False
        assert g.has_edge(0, 2) is False

    def test_has_edge_invalid_vertices(self):
        """Testa has_edge com vertices invalidos."""
        g = AdjacencyMatrixGraph(3)

        with pytest.raises(InvalidVertexException):
            g.has_edge(-1, 0)

        with pytest.raises(InvalidVertexException):
            g.has_edge(0, 10)

    def test_remove_edge(self):
        """Testa remocao de aresta."""
        g = AdjacencyMatrixGraph(3)

        # Adiciona e remove aresta
        g.add_edge(0, 1)
        assert g.get_edge_count() == 1
        assert g.has_edge(0, 1) is True

        g.remove_edge(0, 1)
        assert g.get_edge_count() == 0
        assert g.has_edge(0, 1) is False

    def test_remove_edge_nonexistent(self):
        """Testa remocao de aresta que nao existe."""
        g = AdjacencyMatrixGraph(3)

        # Remover aresta inexistente nao deve causar erro
        g.remove_edge(0, 1)
        assert g.get_edge_count() == 0

    def test_remove_edge_invalid_vertices(self):
        """Testa remocao com vertices invalidos."""
        g = AdjacencyMatrixGraph(3)

        with pytest.raises(InvalidVertexException):
            g.remove_edge(-1, 0)

        with pytest.raises(InvalidVertexException):
            g.remove_edge(0, 5)

    def test_vertex_in_degree(self):
        """Testa calculo de grau de entrada."""
        g = AdjacencyMatrixGraph(4)

        # Inicialmente grau 0
        assert g.get_vertex_in_degree(1) == 0

        # Adiciona arestas chegando em 1
        g.add_edge(0, 1)
        assert g.get_vertex_in_degree(1) == 1

        g.add_edge(2, 1)
        assert g.get_vertex_in_degree(1) == 2

        g.add_edge(3, 1)
        assert g.get_vertex_in_degree(1) == 3

        # Outros vertices ainda grau 0
        assert g.get_vertex_in_degree(0) == 0

    def test_vertex_out_degree(self):
        """Testa calculo de grau de saida."""
        g = AdjacencyMatrixGraph(4)

        # Inicialmente grau 0
        assert g.get_vertex_out_degree(0) == 0

        # Adiciona arestas saindo de 0
        g.add_edge(0, 1)
        assert g.get_vertex_out_degree(0) == 1

        g.add_edge(0, 2)
        assert g.get_vertex_out_degree(0) == 2

        g.add_edge(0, 3)
        assert g.get_vertex_out_degree(0) == 3

        # Outros vertices ainda grau 0
        assert g.get_vertex_out_degree(1) == 0

    def test_vertex_total_degree(self):
        """Testa calculo de grau total."""
        g = AdjacencyMatrixGraph(4)

        # Adiciona arestas
        g.add_edge(0, 1)  # 0: out+1, 1: in+1
        g.add_edge(1, 2)  # 1: out+1, 2: in+1
        g.add_edge(2, 1)  # 2: out+1, 1: in+1

        # Vertice 1: in=2, out=1, total=3
        assert g.get_vertex_in_degree(1) == 2
        assert g.get_vertex_out_degree(1) == 1
        assert g.get_vertex_total_degree(1) == 3

    def test_edge_weights(self):
        """Testa pesos de arestas."""
        g = AdjacencyMatrixGraph(3)

        # Adiciona aresta
        g.add_edge(0, 1)

        # Peso inicial deve ser 0
        assert g.get_edge_weight(0, 1) == 0.0

        # Define peso
        g.set_edge_weight(0, 1, 5.5)
        assert g.get_edge_weight(0, 1) == 5.5

        # Define peso negativo
        g.set_edge_weight(0, 1, -3.2)
        assert g.get_edge_weight(0, 1) == -3.2

    def test_edge_weight_nonexistent_edge(self):
        """Testa peso de aresta inexistente."""
        g = AdjacencyMatrixGraph(3)

        # Tentar definir peso de aresta inexistente
        with pytest.raises(InvalidEdgeException):
            g.set_edge_weight(0, 1, 5.0)

        # Tentar obter peso de aresta inexistente
        with pytest.raises(InvalidEdgeException):
            g.get_edge_weight(0, 1)

    def test_successors(self):
        """Testa obtencao de sucessores."""
        g = AdjacencyMatrixGraph(5)

        # Adiciona arestas 0 -> 1, 0 -> 2, 0 -> 3
        g.add_edge(0, 1)
        g.add_edge(0, 2)
        g.add_edge(0, 3)

        successors = g.get_successors(0)
        assert len(successors) == 3
        assert 1 in successors
        assert 2 in successors
        assert 3 in successors

        # Vertice sem sucessores
        assert g.get_successors(1) == []

    def test_predecessors(self):
        """Testa obtencao de predecessores."""
        g = AdjacencyMatrixGraph(5)

        # Adiciona arestas 1 -> 0, 2 -> 0, 3 -> 0
        g.add_edge(1, 0)
        g.add_edge(2, 0)
        g.add_edge(3, 0)

        predecessors = g.get_predecessors(0)
        assert len(predecessors) == 3
        assert 1 in predecessors
        assert 2 in predecessors
        assert 3 in predecessors

        # Vertice sem predecessores
        assert g.get_predecessors(1) == []

    def test_is_successor(self):
        """Testa verificacao de sucessor."""
        g = AdjacencyMatrixGraph(3)
        g.add_edge(0, 1)

        assert g.is_successor(0, 1) is True
        assert g.is_successor(0, 2) is False
        assert g.is_successor(1, 0) is False

    def test_is_predecessor(self):
        """Testa verificacao de predecessor."""
        g = AdjacencyMatrixGraph(3)
        g.add_edge(0, 1)

        # 0 e predecessor de 1 (existe 0 -> 1)
        assert g.is_predecessor(0, 1) is True
        assert g.is_predecessor(2, 1) is False
        assert g.is_predecessor(1, 0) is False

    def test_is_empty_graph(self):
        """Testa deteccao de grafo vazio."""
        g = AdjacencyMatrixGraph(3)

        # Inicialmente vazio
        assert g.is_empty_graph() is True

        # Adiciona aresta
        g.add_edge(0, 1)
        assert g.is_empty_graph() is False

        # Remove aresta
        g.remove_edge(0, 1)
        assert g.is_empty_graph() is True

    def test_is_complete_graph(self):
        """Testa deteccao de grafo completo."""
        g = AdjacencyMatrixGraph(3)

        # Inicialmente nao e completo
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
        g = AdjacencyMatrixGraph(1)
        assert g.is_complete_graph() is True

    def test_is_connected_simple(self):
        """Testa conectividade em grafo simples."""
        g = AdjacencyMatrixGraph(3)

        # Grafo desconexo
        g.add_edge(0, 1)
        assert g.is_connected() is False

        # Adiciona mais arestas para conectar
        g.add_edge(1, 2)
        g.add_edge(2, 0)

        # Agora e fortemente conexo
        assert g.is_connected() is True

    def test_is_connected_empty(self):
        """Testa conectividade de grafo vazio."""
        g = AdjacencyMatrixGraph(0)
        assert g.is_connected() is True

        g2 = AdjacencyMatrixGraph(1)
        assert g2.is_connected() is True

    def test_is_divergent(self):
        """Testa deteccao de arestas divergentes."""
        g = AdjacencyMatrixGraph(4)
        g.add_edge(0, 1)
        g.add_edge(0, 2)

        # Mesma origem, destinos diferentes
        assert g.is_divergent(0, 1, 0, 2) is True

        # Origens diferentes
        g.add_edge(1, 2)
        assert g.is_divergent(0, 1, 1, 2) is False

    def test_is_convergent(self):
        """Testa deteccao de arestas convergentes."""
        g = AdjacencyMatrixGraph(4)
        g.add_edge(0, 2)
        g.add_edge(1, 2)

        # Mesmo destino, origens diferentes
        assert g.is_convergent(0, 2, 1, 2) is True

        # Destinos diferentes
        g.add_edge(0, 1)
        assert g.is_convergent(0, 1, 0, 2) is False

    def test_is_incident(self):
        """Testa incidencia vertice-aresta."""
        g = AdjacencyMatrixGraph(4)
        g.add_edge(0, 1)

        # Vertice e origem
        assert g.is_incident(0, 1, 0) is True

        # Vertice e destino
        assert g.is_incident(0, 1, 1) is True

        # Vertice nao e incidente
        assert g.is_incident(0, 1, 2) is False

    def test_get_adjacency_matrix(self):
        """Testa obtencao da matriz de adjacencia."""
        g = AdjacencyMatrixGraph(3)
        g.add_edge(0, 1)
        g.add_edge(1, 2)

        matrix = g.get_adjacency_matrix()

        # Verifica que e uma copia
        assert isinstance(matrix, np.ndarray)
        assert matrix.shape == (3, 3)

        # Verifica valores
        assert matrix[0, 1] is True or matrix[0, 1] == True
        assert matrix[1, 2] is True or matrix[1, 2] == True
        assert matrix[0, 2] is False or matrix[0, 2] == False

    def test_get_edge_weights_matrix(self):
        """Testa obtencao da matriz de pesos."""
        g = AdjacencyMatrixGraph(3)
        g.add_edge(0, 1)
        g.set_edge_weight(0, 1, 5.5)

        weights = g.get_edge_weights_matrix()

        # Verifica que e uma copia
        assert isinstance(weights, np.ndarray)
        assert weights.shape == (3, 3)

        # Verifica valores
        assert weights[0, 1] == 5.5
        assert weights[1, 0] == 0.0

    def test_multiple_edges_scenario(self):
        """Testa cenario com multiplas arestas."""
        g = AdjacencyMatrixGraph(5)

        # Cria um grafo mais complexo
        edges = [
            (0, 1), (0, 2),
            (1, 2), (1, 3),
            (2, 3), (2, 4),
            (3, 4),
            (4, 0)
        ]

        for u, v in edges:
            g.add_edge(u, v)

        assert g.get_edge_count() == len(edges)

        # Verifica algumas propriedades
        assert g.get_vertex_out_degree(0) == 2
        assert g.get_vertex_in_degree(4) == 2

    def test_vertex_labels(self):
        """Testa rotulos de vertices."""
        g = AdjacencyMatrixGraph(3)

        # Label inicial None
        assert g.get_vertex_label(0) is None

        # Define label
        g.set_vertex_label(0, "Node_A")
        assert g.get_vertex_label(0) == "Node_A"

        # Substitui label
        g.set_vertex_label(0, "Node_B")
        assert g.get_vertex_label(0) == "Node_B"

    def test_vertex_weights(self):
        """Testa pesos de vertices."""
        g = AdjacencyMatrixGraph(3)

        # Peso inicial 0
        assert g.get_vertex_weight(0) == 0.0

        # Define peso
        g.set_vertex_weight(0, 10.5)
        assert g.get_vertex_weight(0) == 10.5

        # Define peso negativo
        g.set_vertex_weight(1, -5.0)
        assert g.get_vertex_weight(1) == -5.0

    def test_str_representation(self):
        """Testa representacao em string."""
        g = AdjacencyMatrixGraph(5)
        g.add_edge(0, 1)

        str_repr = str(g)
        assert "AdjacencyMatrixGraph" in str_repr
        assert "5" in str_repr  # numero de vertices
        assert "1" in str_repr  # numero de arestas

    def test_repr_representation(self):
        """Testa representacao oficial."""
        g = AdjacencyMatrixGraph(3)

        repr_str = repr(g)
        assert "AdjacencyMatrixGraph" in repr_str
        assert "3" in repr_str
