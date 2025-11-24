"""
Implementacao de grafo usando matriz de adjacencia.

Esta implementacao usa arrays NumPy para representar o grafo como uma matriz,
oferecendo acesso O(1) para verificacao de arestas, mas usando O(V^2) de memoria.
"""

import numpy as np
from typing import List
from .abstract_graph import AbstractGraph
from .exceptions import InvalidVertexException, InvalidEdgeException


class AdjacencyMatrixGraph(AbstractGraph):
    """
    Grafo direcionado simples implementado com matriz de adjacencia.

    Usa uma matriz booleana NxN onde matriz[i][j] = True indica uma aresta i -> j.
    Uma segunda matriz armazena os pesos das arestas.

    Complexidade de espaco: O(V^2)
    Complexidade de has_edge: O(1)
    Complexidade de add_edge: O(1)
    Complexidade de get_vertex_degree: O(V)

    Attributes:
        _adjacency_matrix: Matriz booleana NxN de adjacencias
        _edge_weights: Matriz de floats NxN com pesos das arestas
    """

    def __init__(self, num_vertices: int):
        """
        Inicializa grafo com numero especificado de vertices.

        Args:
            num_vertices: Numero de vertices do grafo (>= 0)

        Raises:
            ValueError: Se num_vertices < 0
        """
        super().__init__(num_vertices)

        # Matriz de adjacencia: True se aresta existe
        self._adjacency_matrix = np.zeros(
            (num_vertices, num_vertices),
            dtype=bool
        )

        # Matriz de pesos das arestas
        self._edge_weights = np.zeros(
            (num_vertices, num_vertices),
            dtype=float
        )

    def has_edge(self, u: int, v: int) -> bool:
        """
        Verifica se existe aresta u -> v.

        Complexidade: O(1)

        Args:
            u: Vertice de origem
            v: Vertice de destino

        Returns:
            True se a aresta existe, False caso contrario

        Raises:
            InvalidVertexException: Se u ou v fora dos limites
        """
        self._validate_vertex(u)
        self._validate_vertex(v)
        return bool(self._adjacency_matrix[u, v])

    def add_edge(self, u: int, v: int) -> None:
        """
        Adiciona aresta u -> v ao grafo.

        Esta operacao e idempotente: adicionar uma aresta que ja existe
        nao tem efeito e nao gera erro.

        Complexidade: O(1)

        Args:
            u: Vertice de origem
            v: Vertice de destino

        Raises:
            InvalidVertexException: Se u ou v fora dos limites
            InvalidEdgeException: Se u == v (lacos nao permitidos)
        """
        self._validate_edge(u, v)

        # Idempotente: so incrementa se aresta nao existia
        if not self._adjacency_matrix[u, v]:
            self._adjacency_matrix[u, v] = True
            self._edge_weights[u, v] = 0.0
            self._num_edges += 1

    def remove_edge(self, u: int, v: int) -> None:
        """
        Remove aresta u -> v do grafo.

        Se a aresta nao existe, a operacao nao tem efeito.

        Complexidade: O(1)

        Args:
            u: Vertice de origem
            v: Vertice de destino

        Raises:
            InvalidVertexException: Se u ou v fora dos limites
        """
        self._validate_vertex(u)
        self._validate_vertex(v)

        if self._adjacency_matrix[u, v]:
            self._adjacency_matrix[u, v] = False
            self._edge_weights[u, v] = 0.0
            self._num_edges -= 1

    def get_vertex_in_degree(self, u: int) -> int:
        """
        Retorna o grau de entrada do vertice u.

        Conta quantas arestas chegam em u (v -> u para todo v).

        Complexidade: O(V)

        Args:
            u: Vertice a verificar

        Returns:
            Numero de arestas que chegam em u

        Raises:
            InvalidVertexException: Se u fora dos limites
        """
        self._validate_vertex(u)
        # Soma a coluna u (todas as arestas ? -> u)
        return int(np.sum(self._adjacency_matrix[:, u]))

    def get_vertex_out_degree(self, u: int) -> int:
        """
        Retorna o grau de saida do vertice u.

        Conta quantas arestas saem de u (u -> v para todo v).

        Complexidade: O(V)

        Args:
            u: Vertice a verificar

        Returns:
            Numero de arestas que saem de u

        Raises:
            InvalidVertexException: Se u fora dos limites
        """
        self._validate_vertex(u)
        # Soma a linha u (todas as arestas u -> ?)
        return int(np.sum(self._adjacency_matrix[u, :]))

    def set_edge_weight(self, u: int, v: int, weight: float) -> None:
        """
        Define o peso da aresta u -> v.

        A aresta deve existir antes de definir o peso.

        Complexidade: O(1)

        Args:
            u: Vertice de origem
            v: Vertice de destino
            weight: Peso da aresta (pode ser negativo)

        Raises:
            InvalidVertexException: Se u ou v fora dos limites
            InvalidEdgeException: Se a aresta nao existe
        """
        self._validate_vertex(u)
        self._validate_vertex(v)

        if not self._adjacency_matrix[u, v]:
            raise InvalidEdgeException.edge_not_found(u, v)

        self._edge_weights[u, v] = weight

    def get_edge_weight(self, u: int, v: int) -> float:
        """
        Retorna o peso da aresta u -> v.

        Complexidade: O(1)

        Args:
            u: Vertice de origem
            v: Vertice de destino

        Returns:
            Peso da aresta

        Raises:
            InvalidVertexException: Se u ou v fora dos limites
            InvalidEdgeException: Se a aresta nao existe
        """
        self._validate_vertex(u)
        self._validate_vertex(v)

        if not self._adjacency_matrix[u, v]:
            raise InvalidEdgeException.edge_not_found(u, v)

        return float(self._edge_weights[u, v])

    def is_connected(self) -> bool:
        """
        Verifica se o grafo e fortemente conexo.

        Um grafo direcionado e fortemente conexo se existe um caminho
        de qualquer vertice para qualquer outro vertice.

        Usa DFS a partir de cada vertice para verificar alcancabilidade.

        Complexidade: O(V * (V + E)) = O(V^3) no pior caso

        Returns:
            True se o grafo e fortemente conexo, False caso contrario
        """
        if self._num_vertices == 0:
            return True

        if self._num_vertices == 1:
            return True

        # Para cada vertice, verifica se alcanca todos os outros
        for start in range(self._num_vertices):
            visited = self._dfs_from(start)
            if len(visited) != self._num_vertices:
                return False

        return True

    def _dfs_from(self, start: int) -> set:
        """
        Realiza DFS a partir de um vertice e retorna vertices alcancados.

        Args:
            start: Vertice inicial

        Returns:
            Conjunto de vertices alcancados a partir de start
        """
        visited = set()
        stack = [start]

        while stack:
            u = stack.pop()
            if u in visited:
                continue

            visited.add(u)

            # Adiciona todos os sucessores nao visitados
            for v in range(self._num_vertices):
                if self._adjacency_matrix[u, v] and v not in visited:
                    stack.append(v)

        return visited

    def get_successors(self, u: int) -> List[int]:
        """
        Retorna lista de sucessores do vertice u.

        Sucessores sao vertices v tais que existe aresta u -> v.

        Complexidade: O(V)

        Args:
            u: Vertice a verificar

        Returns:
            Lista de indices dos vertices sucessores

        Raises:
            InvalidVertexException: Se u fora dos limites
        """
        self._validate_vertex(u)

        # Encontra todos os v onde adjacency_matrix[u, v] = True
        successors = []
        for v in range(self._num_vertices):
            if self._adjacency_matrix[u, v]:
                successors.append(v)

        return successors

    def get_predecessors(self, u: int) -> List[int]:
        """
        Retorna lista de predecessores do vertice u.

        Predecessores sao vertices v tais que existe aresta v -> u.

        Complexidade: O(V)

        Args:
            u: Vertice a verificar

        Returns:
            Lista de indices dos vertices predecessores

        Raises:
            InvalidVertexException: Se u fora dos limites
        """
        self._validate_vertex(u)

        # Encontra todos os v onde adjacency_matrix[v, u] = True
        predecessors = []
        for v in range(self._num_vertices):
            if self._adjacency_matrix[v, u]:
                predecessors.append(v)

        return predecessors

    def get_adjacency_matrix(self) -> np.ndarray:
        """
        Retorna copia da matriz de adjacencia.

        Returns:
            Copia da matriz de adjacencia booleana
        """
        return self._adjacency_matrix.copy()

    def get_edge_weights_matrix(self) -> np.ndarray:
        """
        Retorna copia da matriz de pesos.

        Returns:
            Copia da matriz de pesos das arestas
        """
        return self._edge_weights.copy()
