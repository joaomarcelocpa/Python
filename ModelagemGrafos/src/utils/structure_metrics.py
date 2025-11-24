"""
Métricas de Estrutura e Coesão para Grafos
Implementação própria sem dependências externas
"""

from typing import Dict, List, Set
import numpy as np
from src.graph.abstract_graph import AbstractGraph


class StructureMetrics:
    """
    Calcula métricas de estrutura e coesão para grafos direcionados.
    """

    def __init__(self, graph: AbstractGraph):
        """
        Inicializa as métricas de estrutura.

        Args:
            graph: Grafo a ser analisado
        """
        self.graph = graph
        self.num_vertices = graph.num_vertices

    def network_density(self) -> float:
        """
        Calcula a densidade da rede.

        Densidade = número de arestas existentes / número máximo possível de arestas

        Para grafos direcionados simples:
        - Máximo de arestas = n * (n - 1)
        - Densidade = m / (n * (n - 1))

        Onde n = número de vértices, m = número de arestas

        Returns:
            Densidade da rede (0.0 a 1.0)
        """
        if self.num_vertices <= 1:
            return 0.0

        num_edges = self.graph.num_edges
        max_edges = self.num_vertices * (self.num_vertices - 1)

        return num_edges / max_edges if max_edges > 0 else 0.0

    def clustering_coefficient(self) -> Dict[str, float]:
        """
        Calcula o coeficiente de aglomeração (clustering coefficient).

        Para grafos direcionados, usa a definição que conta triângulos direcionados.

        Coeficiente local: para cada vértice, mede quantos de seus vizinhos
        também são vizinhos entre si.

        Coeficiente global: média dos coeficientes locais.

        Returns:
            Dicionário com:
            - 'local': Dict[vértice, coeficiente_local]
            - 'average': coeficiente médio da rede
            - 'global': coeficiente global (transitivity)
        """
        local_coefficients = {}

        for v in range(self.num_vertices):
            # Obtém vizinhos (união de sucessores e predecessores)
            successors = set(self.graph.get_successors(v))
            predecessors = set(self.graph.get_predecessors(v))
            neighbors = successors.union(predecessors)

            k = len(neighbors)

            # Se vértice tem menos de 2 vizinhos, coeficiente = 0
            if k < 2:
                local_coefficients[v] = 0.0
                continue

            # Conta conexões entre vizinhos
            connections = 0
            neighbors_list = list(neighbors)

            for i in range(len(neighbors_list)):
                for j in range(len(neighbors_list)):
                    if i != j:
                        u = neighbors_list[i]
                        w = neighbors_list[j]
                        if self.graph.has_edge(u, w):
                            connections += 1

            # Coeficiente = conexões reais / conexões possíveis
            # Para grafos direcionados: k * (k - 1) possíveis
            possible = k * (k - 1)
            local_coefficients[v] = connections / possible if possible > 0 else 0.0

        # Coeficiente médio
        average = np.mean(list(local_coefficients.values())) if local_coefficients else 0.0

        # Coeficiente global (transitivity)
        global_coef = self._global_clustering_coefficient()

        return {
            'local': local_coefficients,
            'average': float(average),
            'global': global_coef
        }

    def _global_clustering_coefficient(self) -> float:
        """
        Calcula o coeficiente de aglomeração global (transitivity).

        Transitivity = (3 × número de triângulos) / número de tríades conectadas

        Returns:
            Coeficiente global
        """
        triangles = 0
        triads = 0

        for v in range(self.num_vertices):
            neighbors = list(set(self.graph.get_successors(v)).union(
                set(self.graph.get_predecessors(v))))

            for i in range(len(neighbors)):
                for j in range(i + 1, len(neighbors)):
                    u = neighbors[i]
                    w = neighbors[j]

                    # Conta tríade
                    triads += 1

                    # Verifica se forma triângulo
                    if self.graph.has_edge(u, w) or self.graph.has_edge(w, u):
                        triangles += 1

        return (3 * triangles) / triads if triads > 0 else 0.0

    def assortativity(self) -> float:
        """
        Calcula a assortatividade da rede (degree assortativity).

        Mede a tendência de vértices com graus similares se conectarem.

        Valores:
        - Positivo: vértices com muitas conexões tendem a se conectar entre si
        - Negativo: vértices com muitas conexões tendem a se conectar com vértices com poucas conexões
        - Zero: conexões são aleatórias em relação ao grau

        Para grafos direcionados, usa o grau total (in + out).

        Returns:
            Coeficiente de assortatividade (-1.0 a 1.0)
        """
        if self.graph.num_edges == 0:
            return 0.0

        # Calcula graus
        degrees = [
            self.graph.get_vertex_in_degree(v) + self.graph.get_vertex_out_degree(v)
            for v in range(self.num_vertices)
        ]

        # Para cada aresta, coleta o grau dos vértices conectados
        degree_products = []
        degree_sums = []
        degree_squares = []

        for u in range(self.num_vertices):
            for v in self.graph.get_successors(u):
                deg_u = degrees[u]
                deg_v = degrees[v]

                degree_products.append(deg_u * deg_v)
                degree_sums.append(deg_u + deg_v)
                degree_squares.append(deg_u ** 2 + deg_v ** 2)

        if not degree_products:
            return 0.0

        m = len(degree_products)

        # Calcula assortatividade usando a fórmula de Pearson
        numerator = sum(degree_products) / m - (sum(degree_sums) / (2 * m)) ** 2
        denominator = sum(degree_squares) / (2 * m) - (sum(degree_sums) / (2 * m)) ** 2

        return numerator / denominator if denominator > 0 else 0.0

    def reciprocity(self) -> float:
        """
        Calcula a reciprocidade da rede.

        Mede a proporção de arestas bidirecionais (se existe u->v, também existe v->u).

        Returns:
            Reciprocidade (0.0 a 1.0)
        """
        if self.graph.num_edges == 0:
            return 0.0

        reciprocal_edges = 0
        total_edges = 0

        for u in range(self.num_vertices):
            for v in self.graph.get_successors(u):
                total_edges += 1
                # Verifica se existe aresta reversa
                if self.graph.has_edge(v, u):
                    reciprocal_edges += 1

        return reciprocal_edges / total_edges if total_edges > 0 else 0.0

    def average_path_length(self) -> float:
        """
        Calcula o comprimento médio dos caminhos mínimos na rede.

        Considera apenas pares de vértices conectados.

        Returns:
            Comprimento médio dos caminhos
        """
        from collections import deque

        if self.num_vertices <= 1:
            return 0.0

        total_distance = 0
        num_paths = 0

        for source in range(self.num_vertices):
            # BFS para calcular distâncias
            distances = {v: -1 for v in range(self.num_vertices)}
            distances[source] = 0

            queue = deque([source])

            while queue:
                v = queue.popleft()
                for w in self.graph.get_successors(v):
                    if distances[w] < 0:
                        distances[w] = distances[v] + 1
                        queue.append(w)

            # Soma distâncias para vértices alcançáveis
            for target in range(self.num_vertices):
                if target != source and distances[target] > 0:
                    total_distance += distances[target]
                    num_paths += 1

        return total_distance / num_paths if num_paths > 0 else 0.0

    def diameter(self) -> int:
        """
        Calcula o diâmetro da rede.

        Diâmetro = maior distância mínima entre qualquer par de vértices conectados.

        Returns:
            Diâmetro da rede (-1 se grafo desconectado)
        """
        from collections import deque

        if self.num_vertices <= 1:
            return 0

        max_distance = 0

        for source in range(self.num_vertices):
            # BFS
            distances = {v: -1 for v in range(self.num_vertices)}
            distances[source] = 0

            queue = deque([source])

            while queue:
                v = queue.popleft()
                for w in self.graph.get_successors(v):
                    if distances[w] < 0:
                        distances[w] = distances[v] + 1
                        queue.append(w)

            # Encontra maior distância a partir desta origem
            for dist in distances.values():
                if dist > max_distance:
                    max_distance = dist

        return max_distance if max_distance > 0 else -1

    def get_all_structure_metrics(self) -> Dict[str, any]:
        """
        Calcula todas as métricas de estrutura de uma vez.

        Returns:
            Dicionário com todas as métricas de estrutura
        """
        clustering = self.clustering_coefficient()

        return {
            'density': self.network_density(),
            'clustering_local': clustering['local'],
            'clustering_average': clustering['average'],
            'clustering_global': clustering['global'],
            'assortativity': self.assortativity(),
            'reciprocity': self.reciprocity(),
            'average_path_length': self.average_path_length(),
            'diameter': self.diameter()
        }
