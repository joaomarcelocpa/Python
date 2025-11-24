"""
Implementacao de grafo usando lista de adjacencia.

Esta implementacao usa listas Python para representar o grafo,
oferecendo uso eficiente de memoria O(V+E) e operacoes rapidas
para grafos esparsos.
"""

from typing import List, Dict, Tuple
from .abstract_graph import AbstractGraph
from .exceptions import InvalidVertexException, InvalidEdgeException


class AdjacencyListGraph(AbstractGraph):
    """
    Grafo direcionado simples implementado com lista de adjacencia.

    Usa uma lista de listas onde adjacency_list[i] contem os sucessores do vertice i.
    Um dicionario separado armazena os pesos das arestas.

    Complexidade de espaco: O(V + E)
    Complexidade de has_edge: O(grau_saida(u))
    Complexidade de add_edge: O(grau_saida(u)) - precisa verificar duplicacao
    Complexidade de get_vertex_out_degree: O(1)
    Complexidade de get_vertex_in_degree: O(E)

    Attributes:
        _adjacency_list: Lista de listas de sucessores
        _edge_weights: Dicionario (u,v) -> peso
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

        # Lista de adjacencia: para cada vertice, lista de sucessores
        self._adjacency_list: List[List[int]] = [[] for _ in range(num_vertices)]

        # Dicionario de pesos: (u, v) -> peso
        self._edge_weights: Dict[Tuple[int, int], float] = {}

    def has_edge(self, u: int, v: int) -> bool:
        """
        Verifica se existe aresta u -> v.

        Complexidade: O(grau_saida(u))

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
        return v in self._adjacency_list[u]

    def add_edge(self, u: int, v: int) -> None:
        """
        Adiciona aresta u -> v ao grafo.

        Esta operacao e idempotente: adicionar uma aresta que ja existe
        nao tem efeito e nao gera erro.

        Complexidade: O(grau_saida(u)) - precisa verificar se ja existe

        Args:
            u: Vertice de origem
            v: Vertice de destino

        Raises:
            InvalidVertexException: Se u ou v fora dos limites
            InvalidEdgeException: Se u == v (lacos nao permitidos)
        """
        self._validate_edge(u, v)

        # Idempotente: so adiciona se nao existe
        if v not in self._adjacency_list[u]:
            self._adjacency_list[u].append(v)
            self._edge_weights[(u, v)] = 0.0
            self._num_edges += 1

    def remove_edge(self, u: int, v: int) -> None:
        """
        Remove aresta u -> v do grafo.

        Se a aresta nao existe, a operacao nao tem efeito.

        Complexidade: O(grau_saida(u))

        Args:
            u: Vertice de origem
            v: Vertice de destino

        Raises:
            InvalidVertexException: Se u ou v fora dos limites
        """
        self._validate_vertex(u)
        self._validate_vertex(v)

        if v in self._adjacency_list[u]:
            self._adjacency_list[u].remove(v)
            del self._edge_weights[(u, v)]
            self._num_edges -= 1

    def get_vertex_in_degree(self, u: int) -> int:
        """
        Retorna o grau de entrada do vertice u.

        Conta quantas arestas chegam em u (v -> u para todo v).

        Complexidade: O(E) - precisa percorrer todas as listas

        Args:
            u: Vertice a verificar

        Returns:
            Numero de arestas que chegam em u

        Raises:
            InvalidVertexException: Se u fora dos limites
        """
        self._validate_vertex(u)

        # Conta quantos vertices tem u como sucessor
        count = 0
        for v in range(self._num_vertices):
            if u in self._adjacency_list[v]:
                count += 1
        return count

    def get_vertex_out_degree(self, u: int) -> int:
        """
        Retorna o grau de saida do vertice u.

        Conta quantas arestas saem de u (u -> v para todo v).

        Complexidade: O(1) - tamanho da lista de adjacencia

        Args:
            u: Vertice a verificar

        Returns:
            Numero de arestas que saem de u

        Raises:
            InvalidVertexException: Se u fora dos limites
        """
        self._validate_vertex(u)
        return len(self._adjacency_list[u])

    def set_edge_weight(self, u: int, v: int, weight: float) -> None:
        """
        Define o peso da aresta u -> v.

        A aresta deve existir antes de definir o peso.

        Complexidade: O(grau_saida(u)) - precisa verificar se aresta existe

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

        if v not in self._adjacency_list[u]:
            raise InvalidEdgeException.edge_not_found(u, v)

        self._edge_weights[(u, v)] = weight

    def get_edge_weight(self, u: int, v: int) -> float:
        """
        Retorna o peso da aresta u -> v.

        Complexidade: O(grau_saida(u)) - precisa verificar se aresta existe

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

        if v not in self._adjacency_list[u]:
            raise InvalidEdgeException.edge_not_found(u, v)

        return self._edge_weights[(u, v)]

    def is_connected(self) -> bool:
        """
        Verifica se o grafo e fortemente conexo.

        Um grafo direcionado e fortemente conexo se existe um caminho
        de qualquer vertice para qualquer outro vertice.

        Usa DFS a partir de cada vertice para verificar alcancabilidade.

        Complexidade: O(V * (V + E))

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
            for v in self._adjacency_list[u]:
                if v not in visited:
                    stack.append(v)

        return visited

    def get_successors(self, u: int) -> List[int]:
        """
        Retorna lista de sucessores do vertice u.

        Sucessores sao vertices v tais que existe aresta u -> v.

        Complexidade: O(1) - retorna copia da lista

        Args:
            u: Vertice a verificar

        Returns:
            Lista de indices dos vertices sucessores

        Raises:
            InvalidVertexException: Se u fora dos limites
        """
        self._validate_vertex(u)
        return self._adjacency_list[u].copy()

    def get_predecessors(self, u: int) -> List[int]:
        """
        Retorna lista de predecessores do vertice u.

        Predecessores sao vertices v tais que existe aresta v -> u.

        Complexidade: O(V + E) - precisa verificar todas as listas

        Args:
            u: Vertice a verificar

        Returns:
            Lista de indices dos vertices predecessores

        Raises:
            InvalidVertexException: Se u fora dos limites
        """
        self._validate_vertex(u)

        predecessors = []
        for v in range(self._num_vertices):
            if u in self._adjacency_list[v]:
                predecessors.append(v)

        return predecessors

    def get_adjacency_list(self) -> List[List[int]]:
        """
        Retorna copia profunda da lista de adjacencia.

        Returns:
            Copia da lista de adjacencia
        """
        return [neighbors.copy() for neighbors in self._adjacency_list]

    def get_edge_weights_dict(self) -> Dict[Tuple[int, int], float]:
        """
        Retorna copia do dicionario de pesos.

        Returns:
            Copia do dicionario de pesos das arestas
        """
        return self._edge_weights.copy()
