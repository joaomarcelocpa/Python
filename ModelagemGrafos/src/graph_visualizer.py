"""
Visualizador de grafos usando matplotlib
Trabalha diretamente com AdjacencyListGraph e AdjacencyMatrixGraph
"""

import math
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import numpy as np
from typing import Dict, Tuple, List
from src.graph.abstract_graph import AbstractGraph


class GraphVisualizer:
    """
    Visualizador de grafos customizado para os grafos implementados no projeto.
    Usa matplotlib para desenhar nós e arestas sem dependências externas como NetworkX.
    """

    def __init__(self, graph: AbstractGraph):
        """
        Inicializa o visualizador.

        Args:
            graph: Grafo a ser visualizado (AdjacencyListGraph ou AdjacencyMatrixGraph)
        """
        self.graph = graph
        self.positions = {}
        self.node_colors = {}
        self.edge_colors = {}

    def _circular_layout(self, num_vertices: int) -> Dict[int, Tuple[float, float]]:
        """
        Gera layout circular para os nós.

        Args:
            num_vertices: Número de vértices

        Returns:
            Dicionário {vertex_id: (x, y)}
        """
        positions = {}
        radius = 1.0

        for i in range(num_vertices):
            angle = 2 * math.pi * i / num_vertices
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            positions[i] = (x, y)

        return positions

    def _spring_layout(self, num_vertices: int, iterations: int = 50) -> Dict[int, Tuple[float, float]]:
        """
        Gera layout usando algoritmo de força (spring/force-directed).
        Implementação simplificada do algoritmo de Fruchterman-Reingold.

        Args:
            num_vertices: Número de vértices
            iterations: Número de iterações

        Returns:
            Dicionário {vertex_id: (x, y)}
        """
        # Inicializa posições aleatórias
        np.random.seed(42)
        positions = {i: (np.random.rand() * 2 - 1, np.random.rand() * 2 - 1)
                    for i in range(num_vertices)}

        # Parâmetros do algoritmo
        area = 4.0  # Área total
        k = math.sqrt(area / max(num_vertices, 1))  # Distância ideal

        # Temperatura inicial (controla o movimento)
        temp = 1.0
        cooling_factor = 0.95

        for iteration in range(iterations):
            # Calcula forças repulsivas entre todos os pares
            forces = {i: np.array([0.0, 0.0]) for i in range(num_vertices)}

            # Força repulsiva entre todos os nós
            for i in range(num_vertices):
                for j in range(i + 1, num_vertices):
                    pos_i = np.array(positions[i])
                    pos_j = np.array(positions[j])
                    delta = pos_i - pos_j
                    distance = max(np.linalg.norm(delta), 0.01)

                    # Força repulsiva (Coulomb)
                    repulsion = (k * k) / distance
                    force = (delta / distance) * repulsion

                    forces[i] += force
                    forces[j] -= force

            # Força atrativa entre nós conectados
            for i in range(num_vertices):
                neighbors = self.graph.get_successors(i)
                for j in neighbors:
                    pos_i = np.array(positions[i])
                    pos_j = np.array(positions[j])
                    delta = pos_i - pos_j
                    distance = max(np.linalg.norm(delta), 0.01)

                    # Força atrativa (Hooke)
                    attraction = (distance * distance) / k
                    force = (delta / distance) * attraction

                    forces[i] -= force

            # Atualiza posições
            for i in range(num_vertices):
                force = forces[i]
                force_magnitude = np.linalg.norm(force)

                if force_magnitude > 0:
                    displacement = (force / force_magnitude) * min(force_magnitude, temp)
                    new_pos = np.array(positions[i]) + displacement

                    # Limita dentro da área
                    new_pos = np.clip(new_pos, -2, 2)
                    positions[i] = tuple(new_pos)

            # Resfriamento
            temp *= cooling_factor

        return positions

    def _random_layout(self, num_vertices: int) -> Dict[int, Tuple[float, float]]:
        """
        Gera layout aleatório para os nós.

        Args:
            num_vertices: Número de vértices

        Returns:
            Dicionário {vertex_id: (x, y)}
        """
        np.random.seed(42)
        positions = {}

        for i in range(num_vertices):
            x = np.random.rand() * 2 - 1
            y = np.random.rand() * 2 - 1
            positions[i] = (x, y)

        return positions

    def set_layout(self, layout: str = "spring"):
        """
        Define o layout do grafo.

        Args:
            layout: Tipo de layout ("circular", "spring", "random")
        """
        num_vertices = self.graph.num_vertices()

        if num_vertices == 0:
            self.positions = {}
            return

        if layout == "circular":
            self.positions = self._circular_layout(num_vertices)
        elif layout == "spring":
            self.positions = self._spring_layout(num_vertices)
        elif layout == "random":
            self.positions = self._random_layout(num_vertices)
        else:
            raise ValueError(f"Layout desconhecido: {layout}")

    def draw(
        self,
        fig: Figure = None,
        ax: plt.Axes = None,
        show_labels: bool = True,
        show_weights: bool = False,
        node_size: int = 300,
        font_size: int = 8,
        layout: str = "spring"
    ) -> Tuple[Figure, plt.Axes]:
        """
        Desenha o grafo.

        Args:
            fig: Figura matplotlib (cria nova se None)
            ax: Eixo matplotlib (cria novo se None)
            show_labels: Se True, mostra labels dos nós
            show_weights: Se True, mostra pesos das arestas
            node_size: Tamanho dos nós
            font_size: Tamanho da fonte
            layout: Tipo de layout

        Returns:
            Tuple (Figure, Axes)
        """
        # Cria figura se necessário
        if fig is None or ax is None:
            fig, ax = plt.subplots(figsize=(10, 8))

        ax.clear()

        num_vertices = self.graph.num_vertices()

        if num_vertices == 0:
            ax.text(0.5, 0.5, "Grafo vazio", ha='center', va='center',
                   transform=ax.transAxes, fontsize=14)
            ax.set_xlim(-1, 1)
            ax.set_ylim(-1, 1)
            ax.axis('off')
            return fig, ax

        # Gera layout
        self.set_layout(layout)

        # Desenha arestas primeiro (para ficarem atrás dos nós)
        for i in range(num_vertices):
            neighbors = self.graph.get_successors(i)
            for j in neighbors:
                x1, y1 = self.positions[i]
                x2, y2 = self.positions[j]

                # Cor e largura da aresta baseado no peso
                if self.graph.has_weights():
                    weight = self.graph.get_edge_weight(i, j)
                    # Normaliza peso para largura (1-5)
                    line_width = min(max(weight / 2, 0.5), 5)
                    alpha = min(weight / 10, 0.8)
                else:
                    line_width = 1
                    alpha = 0.5

                # Desenha aresta
                ax.plot([x1, x2], [y1, y2], 'gray', linewidth=line_width,
                       alpha=alpha, zorder=1)

                # Desenha seta para indicar direção
                dx = x2 - x1
                dy = y2 - y1
                length = math.sqrt(dx**2 + dy**2)

                if length > 0:
                    # Posição da ponta da seta (80% do caminho)
                    arrow_pos = 0.8
                    arrow_x = x1 + dx * arrow_pos
                    arrow_y = y1 + dy * arrow_pos

                    # Tamanho da seta
                    arrow_size = 0.02

                    ax.arrow(arrow_x, arrow_y, dx * 0.001, dy * 0.001,
                            head_width=arrow_size, head_length=arrow_size,
                            fc='gray', ec='gray', alpha=alpha, zorder=2)

                # Mostra peso se solicitado
                if show_weights and self.graph.has_weights():
                    weight = self.graph.get_edge_weight(i, j)
                    mid_x = (x1 + x2) / 2
                    mid_y = (y1 + y2) / 2
                    ax.text(mid_x, mid_y, f'{weight:.1f}',
                           fontsize=font_size - 2,
                           ha='center', va='center',
                           bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                                   edgecolor='none', alpha=0.7),
                           zorder=3)

        # Desenha nós
        for i in range(num_vertices):
            x, y = self.positions[i]

            # Calcula grau do nó para tamanho
            in_degree = len([j for j in range(num_vertices)
                           if i in self.graph.get_successors(j)])
            out_degree = len(self.graph.get_successors(i))
            total_degree = in_degree + out_degree

            # Tamanho baseado no grau
            size = node_size + total_degree * 10

            # Cor baseada no grau
            if total_degree == 0:
                color = 'lightgray'
            elif total_degree < 3:
                color = 'lightblue'
            elif total_degree < 10:
                color = 'skyblue'
            else:
                color = 'royalblue'

            # Desenha nó
            circle = plt.Circle((x, y), 0.05, color=color,
                              ec='darkblue', linewidth=2, zorder=4)
            ax.add_patch(circle)

            # Desenha label
            if show_labels:
                label = self.graph.get_vertex_label(i)
                if label:
                    # Trunca labels longos
                    if len(label) > 15:
                        label = label[:12] + "..."

                    ax.text(x, y, label, fontsize=font_size,
                           ha='center', va='center', zorder=5,
                           fontweight='bold', color='white')

        # Configurações do plot
        ax.set_xlim(-2.2, 2.2)
        ax.set_ylim(-2.2, 2.2)
        ax.set_aspect('equal')
        ax.axis('off')

        # Título com estatísticas
        stats = f"Vértices: {num_vertices} | Arestas: {self.graph.num_edges()}"
        if self.graph.num_vertices() > 0:
            density = self.graph.density()
            stats += f" | Densidade: {density:.4f}"

        ax.set_title(stats, fontsize=12, pad=20)

        fig.tight_layout()

        return fig, ax

    def get_statistics(self) -> Dict:
        """
        Retorna estatísticas do grafo.

        Returns:
            Dicionário com estatísticas
        """
        num_vertices = self.graph.num_vertices()
        num_edges = self.graph.num_edges()

        stats = {
            'vertices': num_vertices,
            'edges': num_edges,
            'density': self.graph.density() if num_vertices > 0 else 0,
            'is_empty': self.graph.is_empty(),
            'is_complete': self.graph.is_complete()
        }

        # Calcula graus
        if num_vertices > 0:
            in_degrees = []
            out_degrees = []

            for i in range(num_vertices):
                out_degree = len(self.graph.get_successors(i))
                in_degree = len([j for j in range(num_vertices)
                               if i in self.graph.get_successors(j)])

                in_degrees.append(in_degree)
                out_degrees.append(out_degree)

            stats['avg_in_degree'] = sum(in_degrees) / num_vertices
            stats['avg_out_degree'] = sum(out_degrees) / num_vertices
            stats['max_in_degree'] = max(in_degrees)
            stats['max_out_degree'] = max(out_degrees)
            stats['min_in_degree'] = min(in_degrees)
            stats['min_out_degree'] = min(out_degrees)

        return stats
