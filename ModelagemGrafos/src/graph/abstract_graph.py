from abc import ABC, abstractmethod
from typing import List, Optional
import numpy as np
from .exceptions import InvalidVertexException, InvalidEdgeException


class AbstractGraph(ABC):
    """
    Classe abstrata base para grafos direcionados simples.

    Define a API comum e implementa metodos compartilhados entre
    diferentes representacoes de grafos (matriz, lista, etc.).

    Grafos simples nao permitem:
    - Lacos (arestas de um vertice para ele mesmo)
    - Multiplas arestas entre o mesmo par de vertices

    Attributes:
        _num_vertices: Numero de vertices do grafo
        _num_edges: Numero de arestas do grafo
        _vertex_weights: Array de pesos dos vertices
        _vertex_labels: Lista de rotulos dos vertices
    """

    def __init__(self, num_vertices: int):
        """
        Inicializa o grafo com numero especificado de vertices.

        Args:
            num_vertices: Numero de vertices do grafo (>= 0)

        Raises:
            ValueError: Se num_vertices < 0
        """
        if num_vertices < 0:
            raise ValueError("Numero de vertices deve ser >= 0")

        self._num_vertices = num_vertices
        self._num_edges = 0

        # Pesos e rotulos dos vertices
        self._vertex_weights = np.zeros(num_vertices, dtype=float)
        self._vertex_labels: List[Optional[str]] = [None] * num_vertices

    # ========================================================================
    # PROPRIEDADES
    # ========================================================================

    @property
    def num_vertices(self) -> int:
        """Retorna o numero de vertices do grafo."""
        return self._num_vertices

    @property
    def num_edges(self) -> int:
        """Retorna o numero de arestas do grafo."""
        return self._num_edges

    # ========================================================================
    # METODOS ABSTRATOS (devem ser implementados pelas subclasses)
    # ========================================================================

    @abstractmethod
    def has_edge(self, u: int, v: int) -> bool:
        """
        Verifica se existe aresta de u para v.

        Args:
            u: Vertice origem
            v: Vertice destino

        Returns:
            True se existe aresta u -> v, False caso contrario

        Raises:
            InvalidVertexException: Se u ou v fora do intervalo
        """
        pass

    @abstractmethod
    def add_edge(self, u: int, v: int) -> None:
        """
        Adiciona aresta direcionada de u para v.

        Operacao idempotente: nao duplica aresta existente.

        Args:
            u: Vertice origem
            v: Vertice destino

        Raises:
            InvalidVertexException: Se u ou v fora do intervalo
            InvalidEdgeException: Se u == v (laco)
        """
        pass

    @abstractmethod
    def remove_edge(self, u: int, v: int) -> None:
        """
        Remove aresta de u para v, se existir.

        Operacao idempotente: nao gera erro se aresta nao existe.

        Args:
            u: Vertice origem
            v: Vertice destino

        Raises:
            InvalidVertexException: Se u ou v fora do intervalo
        """
        pass

    @abstractmethod
    def get_vertex_in_degree(self, u: int) -> int:
        """
        Calcula o grau de entrada do vertice u.

        Grau de entrada = numero de arestas que chegam em u.

        Args:
            u: Vertice

        Returns:
            Grau de entrada do vertice

        Raises:
            InvalidVertexException: Se u fora do intervalo
        """
        pass

    @abstractmethod
    def get_vertex_out_degree(self, u: int) -> int:
        """
        Calcula o grau de saida do vertice u.

        Grau de saida = numero de arestas que saem de u.

        Args:
            u: Vertice

        Returns:
            Grau de saida do vertice

        Raises:
            InvalidVertexException: Se u fora do intervalo
        """
        pass

    @abstractmethod
    def set_edge_weight(self, u: int, v: int, weight: float) -> None:
        """
        Define o peso da aresta (u, v).

        Args:
            u: Vertice origem
            v: Vertice destino
            weight: Peso da aresta

        Raises:
            InvalidVertexException: Se u ou v fora do intervalo
            InvalidEdgeException: Se aresta nao existe
        """
        pass

    @abstractmethod
    def get_edge_weight(self, u: int, v: int) -> float:
        """
        Retorna o peso da aresta (u, v).

        Args:
            u: Vertice origem
            v: Vertice destino

        Returns:
            Peso da aresta

        Raises:
            InvalidVertexException: Se u ou v fora do intervalo
            InvalidEdgeException: Se aresta nao existe
        """
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """
        Verifica se o grafo e fortemente conexo.

        Um grafo direcionado e fortemente conexo se existe caminho
        entre todo par de vertices (em ambas as direcoes).

        Returns:
            True se grafo e fortemente conexo, False caso contrario
        """
        pass

    @abstractmethod
    def get_successors(self, u: int) -> List[int]:
        """
        Retorna lista de sucessores do vertice u.

        Sucessores sao vertices v tais que existe aresta u -> v.

        Args:
            u: Vertice

        Returns:
            Lista de indices dos sucessores

        Raises:
            InvalidVertexException: Se u fora do intervalo
        """
        pass

    @abstractmethod
    def get_predecessors(self, u: int) -> List[int]:
        """
        Retorna lista de predecessores do vertice u.

        Predecessores sao vertices v tais que existe aresta v -> u.

        Args:
            u: Vertice

        Returns:
            Lista de indices dos predecessores

        Raises:
            InvalidVertexException: Se u fora do intervalo
        """
        pass

    # ========================================================================
    # METODOS CONCRETOS - Contadores
    # ========================================================================

    def get_vertex_count(self) -> int:
        """
        Retorna o numero de vertices do grafo.

        Returns:
            Numero de vertices
        """
        return self._num_vertices

    def get_edge_count(self) -> int:
        """
        Retorna o numero de arestas do grafo.

        Returns:
            Numero de arestas
        """
        return self._num_edges

    def get_vertex_total_degree(self, u: int) -> int:
        """
        Retorna o grau total do vertice u.

        O grau total e a soma do grau de entrada e grau de saida.

        Args:
            u: Vertice

        Returns:
            Grau total do vertice (in_degree + out_degree)

        Raises:
            InvalidVertexException: Se u fora do intervalo
        """
        return self.get_vertex_in_degree(u) + self.get_vertex_out_degree(u)

    # ========================================================================
    # METODOS CONCRETOS - Pesos e Rotulos
    # ========================================================================

    def set_vertex_weight(self, v: int, weight: float) -> None:
        """
        Define o peso do vertice v.

        Args:
            v: Indice do vertice
            weight: Peso a ser definido

        Raises:
            InvalidVertexException: Se v fora do intervalo
        """
        self._validate_vertex(v)
        self._vertex_weights[v] = weight

    def get_vertex_weight(self, v: int) -> float:
        """
        Retorna o peso do vertice v.

        Args:
            v: Indice do vertice

        Returns:
            Peso do vertice

        Raises:
            InvalidVertexException: Se v fora do intervalo
        """
        self._validate_vertex(v)
        return float(self._vertex_weights[v])

    def set_vertex_label(self, v: int, label: str) -> None:
        """
        Define o rotulo do vertice v.

        Args:
            v: Indice do vertice
            label: Rotulo a ser definido

        Raises:
            InvalidVertexException: Se v fora do intervalo
        """
        self._validate_vertex(v)
        self._vertex_labels[v] = label

    def get_vertex_label(self, v: int) -> Optional[str]:
        """
        Retorna o rotulo do vertice v.

        Args:
            v: Indice do vertice

        Returns:
            Rotulo do vertice, ou None se nao definido

        Raises:
            InvalidVertexException: Se v fora do intervalo
        """
        self._validate_vertex(v)
        return self._vertex_labels[v]

    # ========================================================================
    # METODOS CONCRETOS - Relacoes entre Vertices e Arestas
    # ========================================================================

    def is_successor(self, u: int, v: int) -> bool:
        """
        Verifica se v e sucessor de u (existe aresta u -> v).

        Args:
            u: Vertice origem
            v: Vertice destino

        Returns:
            True se v e sucessor de u

        Raises:
            InvalidVertexException: Se u ou v fora do intervalo
        """
        return self.has_edge(u, v)

    def is_predecessor(self, u: int, v: int) -> bool:
        """
        Verifica se u e predecessor de v (existe aresta u -> v).

        Args:
            u: Vertice origem
            v: Vertice destino

        Returns:
            True se u e predecessor de v

        Raises:
            InvalidVertexException: Se u ou v fora do intervalo
        """
        return self.has_edge(u, v)

    def is_divergent(self, u1: int, v1: int, u2: int, v2: int) -> bool:
        """
        Verifica se as arestas (u1,v1) e (u2,v2) sao divergentes.

        Duas arestas sao divergentes se saem do mesmo vertice:
        u1 == u2 e v1 != v2

        Args:
            u1: Vertice origem da primeira aresta
            v1: Vertice destino da primeira aresta
            u2: Vertice origem da segunda aresta
            v2: Vertice destino da segunda aresta

        Returns:
            True se as arestas sao divergentes

        Raises:
            InvalidVertexException: Se algum vertice fora do intervalo
            InvalidEdgeException: Se alguma aresta nao existe ou e invalida
        """
        self._validate_edge(u1, v1)
        self._validate_edge(u2, v2)

        if not self.has_edge(u1, v1):
            raise InvalidEdgeException(f"Aresta ({u1},{v1}) nao existe")
        if not self.has_edge(u2, v2):
            raise InvalidEdgeException(f"Aresta ({u2},{v2}) nao existe")

        return u1 == u2 and v1 != v2

    def is_convergent(self, u1: int, v1: int, u2: int, v2: int) -> bool:
        """
        Verifica se as arestas (u1,v1) e (u2,v2) sao convergentes.

        Duas arestas sao convergentes se chegam ao mesmo vertice:
        v1 == v2 e u1 != u2

        Args:
            u1: Vertice origem da primeira aresta
            v1: Vertice destino da primeira aresta
            u2: Vertice origem da segunda aresta
            v2: Vertice destino da segunda aresta

        Returns:
            True se as arestas sao convergentes

        Raises:
            InvalidVertexException: Se algum vertice fora do intervalo
            InvalidEdgeException: Se alguma aresta nao existe ou e invalida
        """
        self._validate_edge(u1, v1)
        self._validate_edge(u2, v2)

        if not self.has_edge(u1, v1):
            raise InvalidEdgeException(f"Aresta ({u1},{v1}) nao existe")
        if not self.has_edge(u2, v2):
            raise InvalidEdgeException(f"Aresta ({u2},{v2}) nao existe")

        return v1 == v2 and u1 != u2

    def is_incident(self, u: int, v: int, x: int) -> bool:
        """
        Verifica se o vertice x e incidente a aresta (u,v).

        Um vertice e incidente a uma aresta se e origem ou destino.

        Args:
            u: Vertice origem da aresta
            v: Vertice destino da aresta
            x: Vertice a verificar

        Returns:
            True se x e incidente a aresta (u,v)

        Raises:
            InvalidVertexException: Se algum vertice fora do intervalo
            InvalidEdgeException: Se aresta nao existe
        """
        self._validate_vertex(x)
        if not self.has_edge(u, v):
            raise InvalidEdgeException(f"Aresta ({u},{v}) nao existe")
        return x == u or x == v

    # ========================================================================
    # METODOS CONCRETOS - Propriedades do Grafo
    # ========================================================================

    def is_empty_graph(self) -> bool:
        """
        Verifica se o grafo e vazio (nao possui arestas).

        Returns:
            True se grafo nao possui arestas
        """
        return self._num_edges == 0

    def is_complete_graph(self) -> bool:
        """
        Verifica se o grafo e completo.

        Um grafo direcionado completo possui aresta entre todo par
        de vertices distintos (em ambas as direcoes).
        Total esperado: V * (V - 1)

        Returns:
            True se grafo e completo
        """
        if self._num_vertices <= 1:
            return True
        expected_edges = self._num_vertices * (self._num_vertices - 1)
        return self._num_edges == expected_edges

    # ========================================================================
    # METODOS DE VALIDACAO
    # ========================================================================

    def _validate_vertex(self, v: int) -> None:
        """
        Valida se indice de vertice e valido.

        Args:
            v: Indice do vertice

        Raises:
            InvalidVertexException: Se vertice invalido
        """
        if not (0 <= v < self._num_vertices):
            raise InvalidVertexException(
                vertex=v,
                max_vertex=self._num_vertices - 1
            )

    def _validate_edge(self, u: int, v: int) -> None:
        """
        Valida se aresta e valida.

        Verifica:
        - Se vertices sao validos
        - Se nao e um laco (u == v)

        Args:
            u: Vertice origem
            v: Vertice destino

        Raises:
            InvalidVertexException: Se vertices invalidos
            InvalidEdgeException: Se u == v (laco)
        """
        self._validate_vertex(u)
        self._validate_vertex(v)

        if u == v:
            raise InvalidEdgeException.loop_not_allowed(u)

    # ========================================================================
    # EXPORTACAO
    # ========================================================================

    def export_to_gephi(self, path: str) -> None:
        """
        Exporta grafo no formato GEXF para visualizacao no GEPHI.

        Args:
            path: Caminho do arquivo (ex: 'output/gephi/grafo.gexf')

        Raises:
            ImportError: Se modulo de exportacao nao disponivel
            IOError: Se erro ao escrever arquivo
        """
        from .exporters.gephi_exporter import GephiExporter
        exporter = GephiExporter(self)
        exporter.export(path)

    # ========================================================================
    # METODOS UTILITARIOS
    # ========================================================================

    def __str__(self) -> str:
        """
        Representacao em string do grafo.

        Returns:
            String descrevendo o grafo
        """
        return (f"{self.__class__.__name__}("
                f"vertices={self._num_vertices}, "
                f"arestas={self._num_edges})")

    def __repr__(self) -> str:
        """
        Representacao oficial do grafo.

        Returns:
            String que pode recriar o objeto
        """
        return self.__str__()
