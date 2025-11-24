"""
Métricas de Comunidade para Grafos
Detecção de comunidades e análise de bridging ties
Implementação própria sem dependências externas
"""

from typing import Dict, List, Set, Tuple
import numpy as np
from collections import defaultdict, deque
from src.graph.abstract_graph import AbstractGraph


class CommunityMetrics:
    """
    Calcula métricas de comunidade e detecta comunidades em grafos direcionados.
    """

    def __init__(self, graph: AbstractGraph):
        """
        Inicializa as métricas de comunidade.

        Args:
            graph: Grafo a ser analisado
        """
        self.graph = graph
        self.num_vertices = graph.num_vertices

    def detect_communities_louvain(self, max_iter: int = 100) -> Dict[int, int]:
        """
        Detecta comunidades usando o algoritmo de Louvain adaptado para grafos direcionados.

        O algoritmo maximiza a modularidade através de:
        1. Inicialmente cada vértice é sua própria comunidade
        2. Para cada vértice, testa movê-lo para comunidade de vizinhos
        3. Move se aumentar a modularidade
        4. Repete até convergência

        Args:
            max_iter: Número máximo de iterações

        Returns:
            Dicionário {vértice: id_comunidade}
        """
        if self.num_vertices == 0:
            return {}

        # Inicializa cada vértice em sua própria comunidade
        communities = {v: v for v in range(self.num_vertices)}

        # Calcula graus totais
        total_edges = self.graph.num_edges
        if total_edges == 0:
            return communities

        # Calcula graus de cada vértice
        degrees = {}
        for v in range(self.num_vertices):
            degrees[v] = self.graph.get_vertex_in_degree(v) + self.graph.get_vertex_out_degree(v)

        improved = True
        iteration = 0

        while improved and iteration < max_iter:
            improved = False
            iteration += 1

            # Para cada vértice (em ordem aleatória para melhor convergência)
            vertices = list(range(self.num_vertices))
            np.random.shuffle(vertices)

            for v in vertices:
                # Comunidade atual
                current_comm = communities[v]

                # Encontra comunidades dos vizinhos
                neighbor_comms = set()
                for neighbor in self.graph.get_successors(v):
                    neighbor_comms.add(communities[neighbor])
                for neighbor in self.graph.get_predecessors(v):
                    neighbor_comms.add(communities[neighbor])

                if not neighbor_comms:
                    continue

                # Remove da comunidade atual temporariamente
                communities[v] = -1

                # Calcula modularidade atual
                current_modularity = self._calculate_modularity(communities, degrees, total_edges)

                # Testa cada comunidade vizinha
                best_comm = current_comm
                best_modularity = current_modularity

                for comm in neighbor_comms:
                    # Testa mover para esta comunidade
                    communities[v] = comm
                    mod = self._calculate_modularity(communities, degrees, total_edges)

                    if mod > best_modularity:
                        best_modularity = mod
                        best_comm = comm

                # Aplica melhor escolha
                communities[v] = best_comm

                if best_comm != current_comm:
                    improved = True

        # Renumera comunidades sequencialmente
        communities = self._renumber_communities(communities)

        return communities

    def detect_communities_label_propagation(self, max_iter: int = 100) -> Dict[int, int]:
        """
        Detecta comunidades usando Label Propagation.

        Algoritmo:
        1. Cada vértice começa com label único
        2. Cada vértice adota o label mais comum entre seus vizinhos
        3. Repete até convergência

        Args:
            max_iter: Número máximo de iterações

        Returns:
            Dicionário {vértice: id_comunidade}
        """
        if self.num_vertices == 0:
            return {}

        # Inicializa labels
        labels = {v: v for v in range(self.num_vertices)}

        for iteration in range(max_iter):
            changed = False

            # Para cada vértice em ordem aleatória
            vertices = list(range(self.num_vertices))
            np.random.shuffle(vertices)

            for v in vertices:
                # Conta labels dos vizinhos
                neighbor_labels = []

                for neighbor in self.graph.get_successors(v):
                    neighbor_labels.append(labels[neighbor])
                for neighbor in self.graph.get_predecessors(v):
                    neighbor_labels.append(labels[neighbor])

                if not neighbor_labels:
                    continue

                # Encontra label mais comum
                label_counts = defaultdict(int)
                for label in neighbor_labels:
                    label_counts[label] += 1

                most_common_label = max(label_counts.items(), key=lambda x: x[1])[0]

                # Atualiza se mudou
                if labels[v] != most_common_label:
                    labels[v] = most_common_label
                    changed = True

            # Convergiu?
            if not changed:
                break

        # Renumera comunidades
        labels = self._renumber_communities(labels)

        return labels

    def modularity(self, communities: Dict[int, int]) -> float:
        """
        Calcula a modularidade de uma divisão em comunidades.

        Modularidade mede a qualidade da divisão em comunidades.
        Valores altos indicam que há mais conexões dentro das comunidades
        do que seria esperado em uma rede aleatória.

        Fórmula para grafos direcionados:
        Q = (1/m) * Σ[A_ij - (k_out_i * k_in_j)/m] * δ(c_i, c_j)

        Args:
            communities: Dicionário {vértice: id_comunidade}

        Returns:
            Modularidade (geralmente entre -0.5 e 1.0)
        """
        total_edges = self.graph.num_edges
        if total_edges == 0:
            return 0.0

        # Calcula graus
        degrees = {}
        for v in range(self.num_vertices):
            degrees[v] = self.graph.get_vertex_in_degree(v) + self.graph.get_vertex_out_degree(v)

        return self._calculate_modularity(communities, degrees, total_edges)

    def _calculate_modularity(self, communities: Dict[int, int],
                             degrees: Dict[int, int], total_edges: int) -> float:
        """
        Calcula modularidade (método auxiliar) para grafos direcionados.

        Fórmula: Q = (1/m) * Σ[A_ij - (k_out_i * k_in_j)/m] * δ(c_i, c_j)

        Args:
            communities: Dicionário de comunidades
            degrees: Dicionário de graus (não usado, calculamos in/out separadamente)
            total_edges: Número total de arestas

        Returns:
            Modularidade
        """
        if total_edges == 0:
            return 0.0

        modularity = 0.0

        for i in range(self.num_vertices):
            if communities.get(i, -1) < 0:
                continue

            # Grau de saída de i
            k_out_i = self.graph.get_vertex_out_degree(i)

            for j in range(self.num_vertices):
                if communities.get(j, -1) < 0:
                    continue

                # Mesma comunidade?
                if communities[i] == communities[j]:
                    # A_ij (1 se existe aresta i->j, 0 caso contrário)
                    a_ij = 1 if self.graph.has_edge(i, j) else 0

                    # Grau de entrada de j
                    k_in_j = self.graph.get_vertex_in_degree(j)

                    # Termo esperado: (k_out_i * k_in_j) / m
                    expected = (k_out_i * k_in_j) / total_edges if total_edges > 0 else 0

                    modularity += a_ij - expected

        # Normaliza por m (não por 2m, pois é grafo direcionado)
        return modularity / total_edges if total_edges > 0 else 0.0

    def _renumber_communities(self, communities: Dict[int, int]) -> Dict[int, int]:
        """
        Renumera comunidades sequencialmente a partir de 0.

        Args:
            communities: Dicionário original

        Returns:
            Dicionário renumerado
        """
        unique_comms = sorted(set(communities.values()))
        comm_map = {old: new for new, old in enumerate(unique_comms)}

        return {v: comm_map[c] for v, c in communities.items()}

    def bridging_ties(self, communities: Dict[int, int] = None) -> Dict[int, float]:
        """
        Identifica bridging ties - vértices que conectam diferentes comunidades.

        Um vértice tem alto bridging coefficient se conecta múltiplas comunidades.

        Se communities não fornecido, detecta automaticamente.

        Args:
            communities: Dicionário {vértice: id_comunidade} (opcional)

        Returns:
            Dicionário {vértice: bridging_coefficient}
        """
        # Detecta comunidades se não fornecidas
        if communities is None:
            communities = self.detect_communities_louvain()

        if not communities:
            return {}

        bridging_scores = {}

        for v in range(self.num_vertices):
            # Comunidades dos vizinhos
            neighbor_communities = set()

            for neighbor in self.graph.get_successors(v):
                if neighbor in communities:
                    neighbor_communities.add(communities[neighbor])

            for neighbor in self.graph.get_predecessors(v):
                if neighbor in communities:
                    neighbor_communities.add(communities[neighbor])

            # Bridging coefficient = número de comunidades diferentes conectadas
            # Normalizado pelo número total de comunidades
            num_communities = len(set(communities.values()))

            if num_communities > 1:
                bridging_scores[v] = len(neighbor_communities) / num_communities
            else:
                bridging_scores[v] = 0.0

        return bridging_scores

    def inter_community_edges(self, communities: Dict[int, int]) -> Dict[Tuple[int, int], int]:
        """
        Conta arestas entre diferentes comunidades.

        Args:
            communities: Dicionário {vértice: id_comunidade}

        Returns:
            Dicionário {(comunidade1, comunidade2): número_de_arestas}
        """
        inter_edges = defaultdict(int)

        for u in range(self.num_vertices):
            comm_u = communities.get(u)
            if comm_u is None:
                continue

            for v in self.graph.get_successors(u):
                comm_v = communities.get(v)
                if comm_v is None:
                    continue

                # Aresta entre comunidades diferentes?
                if comm_u != comm_v:
                    key = tuple(sorted([comm_u, comm_v]))
                    inter_edges[key] += 1

        return dict(inter_edges)

    def community_statistics(self, communities: Dict[int, int]) -> Dict[int, Dict[str, any]]:
        """
        Calcula estatísticas para cada comunidade.

        Args:
            communities: Dicionário {vértice: id_comunidade}

        Returns:
            Dicionário {id_comunidade: estatísticas}
        """
        stats = defaultdict(lambda: {
            'size': 0,
            'internal_edges': 0,
            'external_edges': 0,
            'members': []
        })

        # Conta membros
        for v, comm in communities.items():
            stats[comm]['size'] += 1
            stats[comm]['members'].append(v)

        # Conta arestas
        for u in range(self.num_vertices):
            comm_u = communities.get(u)
            if comm_u is None:
                continue

            for v in self.graph.get_successors(u):
                comm_v = communities.get(v)
                if comm_v is None:
                    continue

                if comm_u == comm_v:
                    stats[comm_u]['internal_edges'] += 1
                else:
                    stats[comm_u]['external_edges'] += 1

        return dict(stats)

    def get_all_community_metrics(self) -> Dict[str, any]:
        """
        Calcula todas as métricas de comunidade de uma vez.

        Returns:
            Dicionário com todas as métricas de comunidade
        """
        # Usa apenas Label Propagation (muito mais rápido que Louvain)
        # Label Propagation: ~0.03s vs Louvain: ~25s em grafos esparsos
        best_communities = self.detect_communities_label_propagation()
        best_modularity = self.modularity(best_communities)
        method = 'label_propagation'

        # Calcula métricas adicionais
        bridging = self.bridging_ties(best_communities)
        inter_edges = self.inter_community_edges(best_communities)
        comm_stats = self.community_statistics(best_communities)

        return {
            'communities': best_communities,
            'method': method,
            'modularity': best_modularity,
            'num_communities': len(set(best_communities.values())),
            'bridging_ties': bridging,
            'inter_community_edges': inter_edges,
            'community_statistics': comm_stats
        }
