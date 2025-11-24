"""
Biblioteca de Grafos Direcionados Simples.

Este pacote fornece implementacoes de grafos direcionados simples
usando diferentes representacoes (matriz de adjacencia e lista de adjacencia).

Classes principais:
    - AbstractGraph: Classe abstrata base
    - AdjacencyMatrixGraph: Implementacao com matriz
    - AdjacencyListGraph: Implementacao com lista

Excecoes:
    - GraphException: Excecao base
    - InvalidVertexException: Vertice invalido
    - InvalidEdgeException: Aresta invalida
"""

from .abstract_graph import AbstractGraph
from .adjacency_matrix_graph import AdjacencyMatrixGraph
from .adjacency_list_graph import AdjacencyListGraph
from .exceptions import (
    GraphException,
    InvalidVertexException,
    InvalidEdgeException
)

__version__ = '1.0.0'
__author__ = 'Graph Library Team'

__all__ = [
    'AbstractGraph',
    'AdjacencyMatrixGraph',
    'AdjacencyListGraph',
    'GraphException',
    'InvalidVertexException',
    'InvalidEdgeException',
]
