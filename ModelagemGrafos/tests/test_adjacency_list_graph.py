"""
Testes para a classe AdjacencyListGraph.

Testa a implementacao concreta de grafos usando lista de adjacencia,
incluindo todas as operacoes, validacoes e propriedades.
"""

import pytest
from src.graph.adjacency_list_graph import AdjacencyListGraph
from src.graph.exceptions import InvalidVertexException, InvalidEdgeException


class TestAdjacencyListGraph:
    """Testes para AdjacencyListGraph."""

    def test_initialization(self):
        """Testa inicializacao basica."""
        g = AdjacencyListGraph(5)
        assert g.get_vertex_count() == 5
        assert g.get_edge_count() == 0
        assert g.num_vertices == 5
        assert g.num_edges == 0

    def test_initialization_zero_vertices(self):
        """Testa grafo com zero vertices."""
        g = AdjacencyListGraph(0)
        assert g.get_vertex_count() == 0
        assert g.get_edge_count() == 0

    def test_initialization_invalid(self):
        """Testa inicializacao com numero invalido de vertices."""
        with pytest.raises(ValueError):
            AdjacencyListGraph(-1)

    def test_add_edge_basic(self):
        """Testa adicao basica de aresta."""
        g = AdjacencyListGraph(3)

        # Adiciona aresta 0 -> 1
        g.add_edge(0, 1)
        assert g.has_edge(0, 1) is True
        assert g.get_edge_count() == 1

        # Aresta reversa nao existe
        assert g.has_edge(1, 0) is False

    def test_add_edge_idempotent(self):
        """Testa que add_edge e idempotente."""
        g = AdjacencyListGraph(3)

        # Adiciona mesma aresta multiplas vezes
        g.add_edge(0, 1)
        assert g.get_edge_count() == 1

        g.add_edge(0, 1)
        assert g.get_edge_count() == 1  # Nao deve incrementar

        g.add_edge(0, 1)
        assert g.get_edge_count() == 1  # Ainda 1

    def test_add_edge_loop_not_allowed(self):
        """Testa que lacos nao sao permitidos."""
        g = AdjacencyListGraph(3)

        with pytest.raises(InvalidEdgeException):
            g.add_edge(0, 0)

        with pytest.raises(InvalidEdgeException):
            g.add_edge(2, 2)

    def test_add_edge_invalid_vertices(self):
        """Testa adicao de aresta com vertices invalidos."""
        g = AdjacencyListGraph(3)

        # Vertice negativo
        with pytest.raises(InvalidVertexException):
            g.add_edge(-1, 0)

        # Vertice fora dos limites
        with pytest.raises(InvalidVertexException):
            g.add_edge(0, 5)

    def test_has_edge(self):
        """Testa verificacao de existencia de aresta."""
        g = AdjacencyListGraph(4)

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
        g = AdjacencyListGraph(3)

        with pytest.raises(InvalidVertexException):
            g.has_edge(-1, 0)

        with pytest.raises(InvalidVertexException):
            g.has_edge(0, 10)

    def test_remove_edge(self):
        """Testa remocao de aresta."""
        g = AdjacencyListGraph(3)

        # Adiciona e remove aresta
        g.add_edge(0, 1)
        assert g.get_edge_count() == 1
        assert g.has_edge(0, 1) is True

        g.remove_edge(0, 1)
        assert g.get_edge_count() == 0
        assert g.has_edge(0, 1) is False

    def test_remove_edge_nonexistent(self):
        """Testa remocao de aresta que nao existe."""
        g = AdjacencyListGraph(3)

        # Remover aresta inexistente nao deve causar erro
        g.remove_edge(0, 1)
        assert g.get_edge_count() == 0

    def test_remove_edge_invalid_vertices(self):
        """Testa remocao com vertices invalidos."""
        g = AdjacencyListGraph(3)

        with pytest.raises(InvalidVertexException):
            g.remove_edge(-1, 0)

        with pytest.raises(InvalidVertexException):
            g.remove_edge(0, 5)

    def test_vertex_in_degree(self):
        """Testa calculo de grau de entrada."""
        g = AdjacencyListGraph(4)

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
        g = AdjacencyListGraph(4)

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
        g = AdjacencyListGraph(4)

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
        g = AdjacencyListGraph(3)

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
        g = AdjacencyListGraph(3)

        # Tentar definir peso de aresta inexistente
        with pytest.raises(InvalidEdgeException):
            g.set_edge_weight(0, 1, 5.0)

        # Tentar obter peso de aresta inexistente
        with pytest.raises(InvalidEdgeException):
            g.get_edge_weight(0, 1)

    def test_successors(self):
        """Testa obtencao de sucessores."""
        g = AdjacencyListGraph(5)

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
        g = AdjacencyListGraph(5)

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
        g = AdjacencyListGraph(3)
        g.add_edge(0, 1)

        assert g.is_successor(0, 1) is True
        assert g.is_successor(0, 2) is False
        assert g.is_successor(1, 0) is False

    def test_is_predecessor(self):
        """Testa verificacao de predecessor."""
        g = AdjacencyListGraph(3)
        g.add_edge(0, 1)

        # 0 e predecessor de 1 (existe 0 -> 1)
        assert g.is_predecessor(0, 1) is True
        assert g.is_predecessor(2, 1) is False
        assert g.is_predecessor(1, 0) is False

    def test_is_empty_graph(self):
        """Testa deteccao de grafo vazio."""
        g = AdjacencyListGraph(3)

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
        g = AdjacencyListGraph(3)

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
        g = AdjacencyListGraph(1)
        assert g.is_complete_graph() is True

    def test_is_connected_simple(self):
        """Testa conectividade em grafo simples."""
        g = AdjacencyListGraph(3)

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
        g = AdjacencyListGraph(0)
        assert g.is_connected() is True

        g2 = AdjacencyListGraph(1)
        assert g2.is_connected() is True

    def test_is_divergent(self):
        """Testa deteccao de arestas divergentes."""
        g = AdjacencyListGraph(4)
        g.add_edge(0, 1)
        g.add_edge(0, 2)

        # Mesma origem, destinos diferentes
        assert g.is_divergent(0, 1, 0, 2) is True

        # Origens diferentes
        g.add_edge(1, 2)
        assert g.is_divergent(0, 1, 1, 2) is False

    def test_is_convergent(self):
        """Testa deteccao de arestas convergentes."""
        g = AdjacencyListGraph(4)
        g.add_edge(0, 2)
        g.add_edge(1, 2)

        # Mesmo destino, origens diferentes
        assert g.is_convergent(0, 2, 1, 2) is True

        # Destinos diferentes
        g.add_edge(0, 1)
        assert g.is_convergent(0, 1, 0, 2) is False

    def test_is_incident(self):
        """Testa incidencia vertice-aresta."""
        g = AdjacencyListGraph(4)
        g.add_edge(0, 1)

        # Vertice e origem
        assert g.is_incident(0, 1, 0) is True

        # Vertice e destino
        assert g.is_incident(0, 1, 1) is True

        # Vertice nao e incidente
        assert g.is_incident(0, 1, 2) is False

    def test_get_adjacency_list(self):
        """Testa obtencao da lista de adjacencia."""
        g = AdjacencyListGraph(3)
        g.add_edge(0, 1)
        g.add_edge(1, 2)

        adj_list = g.get_adjacency_list()

        # Verifica que e uma copia
        assert isinstance(adj_list, list)
        assert len(adj_list) == 3

        # Verifica valores
        assert 1 in adj_list[0]
        assert 2 in adj_list[1]
        assert len(adj_list[2]) == 0

        # Modifica copia nao deve afetar grafo original
        adj_list[0].append(2)
        # Grafo original ainda deve ter apenas 1 no successors de 0
        original_successors = g.get_successors(0)
        assert len(original_successors) == 1
        assert 1 in original_successors
        assert 2 not in original_successors

    def test_get_edge_weights_dict(self):
        """Testa obtencao do dicionario de pesos."""
        g = AdjacencyListGraph(3)
        g.add_edge(0, 1)
        g.set_edge_weight(0, 1, 5.5)

        weights = g.get_edge_weights_dict()

        # Verifica que e uma copia
        assert isinstance(weights, dict)

        # Verifica valores
        assert weights[(0, 1)] == 5.5

        # Modifica copia nao deve afetar grafo
        weights[(0, 1)] = 999
        assert g.get_edge_weight(0, 1) == 5.5

    def test_multiple_edges_scenario(self):
        """Testa cenario com multiplas arestas."""
        g = AdjacencyListGraph(5)

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
        g = AdjacencyListGraph(3)

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
        g = AdjacencyListGraph(3)

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
        g = AdjacencyListGraph(5)
        g.add_edge(0, 1)

        str_repr = str(g)
        assert "AdjacencyListGraph" in str_repr
        assert "5" in str_repr  # numero de vertices
        assert "1" in str_repr  # numero de arestas

    def test_repr_representation(self):
        """Testa representacao oficial."""
        g = AdjacencyListGraph(3)

        repr_str = repr(g)
        assert "AdjacencyListGraph" in repr_str
        assert "3" in repr_str

    def test_sparse_graph_efficiency(self):
        """Testa eficiencia em grafo esparso."""
        # Lista de adjacencia deve ser mais eficiente para grafos esparsos
        g = AdjacencyListGraph(100)

        # Adiciona poucas arestas
        g.add_edge(0, 1)
        g.add_edge(50, 51)
        g.add_edge(99, 0)

        # Verifica que funciona corretamente
        assert g.get_edge_count() == 3
        assert g.has_edge(0, 1) is True
        assert g.has_edge(50, 51) is True
        assert g.has_edge(99, 0) is True

        # Graus de saida devem ser rapidos (O(1))
        assert g.get_vertex_out_degree(0) == 1
        assert g.get_vertex_out_degree(1) == 0
