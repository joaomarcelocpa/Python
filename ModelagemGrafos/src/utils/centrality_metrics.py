"""
Métricas de Centralidade para Grafos
Implementação própria sem dependências externas (NetworkX, etc.)
"""

from typing import Dict, List
import numpy as np
from collections import deque
from src.graph.abstract_graph import AbstractGraph


class CentralityMetrics:
    """
    Calcula métricas de centralidade para grafos direcionados.
    """

    def __init__(self, graph: AbstractGraph):
        """
        Inicializa as métricas de centralidade.

        Args:
            graph: Grafo a ser analisado
        """
        self.graph = graph
        self.num_vertices = graph.num_vertices

    def degree_centrality(self) -> Dict[str, Dict[int, float]]:
        """
        Calcula a centralidade de grau para todos os vértices.

        Para grafos direcionados, calcula:
        - In-degree centrality: número de arestas que chegam ao vértice
        - Out-degree centrality: número de arestas que saem do vértice
        - Total degree centrality: soma dos dois

        Valores são normalizados dividindo pelo número máximo possível de conexões (n-1).

        Returns:
            Dicionário com 'in_degree', 'out_degree' e 'total' para cada vértice
        """
        if self.num_vertices <= 1:
            return {
                'in_degree': {},
                'out_degree': {},
                'total': {}
            }

        in_degree = {}
        out_degree = {}
        total_degree = {}

        # Calcula graus
        for v in range(self.num_vertices):
            in_deg = self.graph.get_vertex_in_degree(v)
            out_deg = self.graph.get_vertex_out_degree(v)

            # Normaliza pelo número máximo de conexões (n-1)
            max_degree = self.num_vertices - 1
            in_degree[v] = in_deg / max_degree if max_degree > 0 else 0
            out_degree[v] = out_deg / max_degree if max_degree > 0 else 0
            total_degree[v] = (in_deg + out_deg) / (2 * max_degree) if max_degree > 0 else 0

        return {
            'in_degree': in_degree,
            'out_degree': out_degree,
            'total': total_degree
        }

    def betweenness_centrality(self) -> Dict[int, float]:
        """
        Calcula a centralidade de intermediação (betweenness centrality).

        Mede quantos caminhos mínimos entre pares de vértices passam por cada vértice.
        Identifica "pontes" na rede que conectam diferentes grupos.

        Usa o algoritmo de Brandes para grafos direcionados.

        Returns:
            Dicionário {vértice: betweenness_centrality}
        """
        if self.num_vertices <= 2:
            return {v: 0.0 for v in range(self.num_vertices)}

        betweenness = {v: 0.0 for v in range(self.num_vertices)}

        # Para cada vértice como origem
        for s in range(self.num_vertices):
            # Usa BFS para encontrar caminhos mínimos
            stack = []
            predecessors = {v: [] for v in range(self.num_vertices)}
            sigma = {v: 0 for v in range(self.num_vertices)}
            sigma[s] = 1
            dist = {v: -1 for v in range(self.num_vertices)}
            dist[s] = 0

            queue = deque([s])

            # BFS
            while queue:
                v = queue.popleft()
                stack.append(v)

                for w in self.graph.get_successors(v):
                    # Primeira vez visitando w?
                    if dist[w] < 0:
                        queue.append(w)
                        dist[w] = dist[v] + 1

                    # Caminho mínimo para w via v?
                    if dist[w] == dist[v] + 1:
                        sigma[w] += sigma[v]
                        predecessors[w].append(v)

            # Acumula contribuições de dependência
            delta = {v: 0.0 for v in range(self.num_vertices)}

            # Volta pela pilha (ordem decrescente de distância)
            while stack:
                w = stack.pop()
                for v in predecessors[w]:
                    delta[v] += (sigma[v] / sigma[w]) * (1 + delta[w])
                if w != s:
                    betweenness[w] += delta[w]

        # Normaliza
        # Para grafos direcionados: divide por (n-1)(n-2)
        n = self.num_vertices
        if n > 2:
            scale = 1.0 / ((n - 1) * (n - 2))
            for v in betweenness:
                betweenness[v] *= scale

        return betweenness

    def closeness_centrality(self) -> Dict[int, float]:
        """
        Calcula a centralidade de proximidade (closeness centrality).

        Mede quão próximo um vértice está de todos os outros.
        Calcula a média das distâncias mínimas para todos os outros vértices.

        Para grafos direcionados, calcula a versão out-closeness (distâncias saindo do vértice).

        Returns:
            Dicionário {vértice: closeness_centrality}
        """
        if self.num_vertices <= 1:
            return {v: 0.0 for v in range(self.num_vertices)}

        closeness = {}

        for v in range(self.num_vertices):
            # BFS para calcular distâncias
            distances = self._bfs_distances(v)

            # Soma das distâncias para vértices alcançáveis
            reachable = [d for d in distances.values() if d > 0]

            if len(reachable) == 0:
                closeness[v] = 0.0
            else:
                # Closeness = (n-1) / soma_distâncias
                # Multiplicado pela proporção de vértices alcançáveis
                total_distance = sum(reachable)
                n_reachable = len(reachable)
                n = self.num_vertices

                if total_distance > 0:
                    closeness[v] = (n_reachable / (n - 1)) * (n_reachable / total_distance)
                else:
                    closeness[v] = 0.0

        return closeness

    def pagerank(self, damping: float = 0.85, max_iter: int = 100, tol: float = 1e-6) -> Dict[int, float]:
        """
        Calcula o PageRank para cada vértice.

        Mede a importância de cada vértice baseado na estrutura de links.
        Vértices importantes recebem links de outros vértices importantes.

        Args:
            damping: Fator de amortecimento (probabilidade de seguir links)
            max_iter: Número máximo de iterações
            tol: Tolerância para convergência

        Returns:
            Dicionário {vértice: pagerank_score}
        """
        if self.num_vertices == 0:
            return {}

        n = self.num_vertices

        # Inicializa PageRank uniformemente
        pagerank = {v: 1.0 / n for v in range(n)}

        # Iterações do algoritmo
        for _ in range(max_iter):
            new_pagerank = {}
            max_diff = 0.0

            for v in range(n):
                # Componente de teleporte
                rank = (1 - damping) / n

                # Soma das contribuições dos predecessores
                for u in self.graph.get_predecessors(v):
                    out_degree = self.graph.get_vertex_out_degree(u)
                    if out_degree > 0:
                        rank += damping * (pagerank[u] / out_degree)

                new_pagerank[v] = rank
                max_diff = max(max_diff, abs(new_pagerank[v] - pagerank[v]))

            pagerank = new_pagerank

            # Verifica convergência
            if max_diff < tol:
                break

        return pagerank

    def eigenvector_centrality(self, max_iter: int = 100, tol: float = 1e-6) -> Dict[int, float]:
        """
        Calcula a centralidade de autovetor (eigenvector centrality).

        Similar ao PageRank, mas sem fator de damping.
        A centralidade de um vértice é proporcional à soma das centralidades
        de seus predecessores.

        Args:
            max_iter: Número máximo de iterações
            tol: Tolerância para convergência

        Returns:
            Dicionário {vértice: eigenvector_centrality}
        """
        if self.num_vertices == 0:
            return {}

        n = self.num_vertices

        # Inicializa com valores uniformes
        centrality = {v: 1.0 / n for v in range(n)}

        # Power iteration
        for _ in range(max_iter):
            new_centrality = {v: 0.0 for v in range(n)}

            # Para cada vértice, soma contribuições dos predecessores
            for v in range(n):
                for u in self.graph.get_predecessors(v):
                    new_centrality[v] += centrality[u]

            # Normaliza
            norm = sum(new_centrality.values())
            if norm > 0:
                new_centrality = {v: val / norm for v, val in new_centrality.items()}

            # Verifica convergência
            max_diff = max(abs(new_centrality[v] - centrality[v]) for v in range(n))
            centrality = new_centrality

            if max_diff < tol:
                break

        return centrality

    def _bfs_distances(self, source: int) -> Dict[int, int]:
        """
        Calcula distâncias mínimas de um vértice origem para todos os outros usando BFS.

        Args:
            source: Vértice origem

        Returns:
            Dicionário {vértice: distância}
        """
        distances = {v: -1 for v in range(self.num_vertices)}
        distances[source] = 0

        queue = deque([source])

        while queue:
            v = queue.popleft()
            for w in self.graph.get_successors(v):
                if distances[w] < 0:
                    distances[w] = distances[v] + 1
                    queue.append(w)

        return distances

    def get_all_centralities(self) -> Dict[str, Dict[int, float]]:
        """
        Calcula todas as métricas de centralidade de uma vez.

        Returns:
            Dicionário com todas as métricas de centralidade
        """
        result = {}

        # Degree centrality
        degree = self.degree_centrality()
        result['degree_in'] = degree['in_degree']
        result['degree_out'] = degree['out_degree']
        result['degree_total'] = degree['total']

        # Outras centralidades
        result['betweenness'] = self.betweenness_centrality()
        result['closeness'] = self.closeness_centrality()
        result['pagerank'] = self.pagerank()
        result['eigenvector'] = self.eigenvector_centrality()

        return result
