"""
Visualizador de grafos GEXF usando matplotlib
"""

import math
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import numpy as np
import time
from typing import Dict, Tuple
from src.gexf_reader import GEXFReader
from src.utils.logger import get_logger


class GEXFVisualizer:
    """
    Visualiza grafos a partir de arquivos GEXF.
    """

    def __init__(self, gexf_file: str):
        """
        Inicializa o visualizador.

        Args:
            gexf_file: Caminho para o arquivo GEXF
        """
        self.logger = get_logger()
        self.logger.info(f"Inicializando visualizador para: {gexf_file}")

        try:
            self.reader = GEXFReader(gexf_file)
            self.logger.debug("GEXFReader criado com sucesso")

            self.reader.parse()
            self.logger.debug("Arquivo GEXF parseado com sucesso")

            stats = self.reader.get_statistics()
            self.logger.info(f"Grafo carregado: {stats['num_nodes']} nós, {stats['num_edges']} arestas")

            self.positions = {}
        except Exception as e:
            self.logger.exception(f"Erro ao inicializar visualizador para {gexf_file}")
            raise

    def _circular_layout(self) -> Dict[str, Tuple[float, float]]:
        """Gera layout circular."""
        nodes = list(self.reader.get_nodes().keys())
        num_nodes = len(nodes)
        positions = {}
        radius = 1.0

        for i, node_id in enumerate(nodes):
            angle = 2 * math.pi * i / num_nodes
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            positions[node_id] = (x, y)

        return positions

    def _spring_layout(self, iterations: int = 50) -> Dict[str, Tuple[float, float]]:
        """
        Gera layout usando algoritmo de força simplificado.
        Ajusta automaticamente as iterações baseado no tamanho do grafo.
        """
        start_time = time.time()
        nodes = list(self.reader.get_nodes().keys())
        num_nodes = len(nodes)

        if num_nodes > 1000:
            iterations = 10
            self.logger.warning(f"Grafo muito grande ({num_nodes} nós), reduzindo para {iterations} iterações")
        elif num_nodes > 500:
            iterations = 20 
            self.logger.info(f"Grafo grande ({num_nodes} nós), usando {iterations} iterações")
        elif num_nodes > 200:
            iterations = 30 
            self.logger.debug(f"Grafo médio ({num_nodes} nós), usando {iterations} iterações")

        self.logger.info(f"Calculando spring layout para {num_nodes} nós com {iterations} iterações")

        np.random.seed(42)
        positions = {node_id: (np.random.rand() * 2 - 1, np.random.rand() * 2 - 1)
                    for node_id in nodes}

        node_index = {node_id: i for i, node_id in enumerate(nodes)}

        area = 4.0
        k = math.sqrt(area / max(num_nodes, 1))
        temp = 1.0
        cooling_factor = 0.95

        for iteration in range(iterations):
            forces = {node_id: np.array([0.0, 0.0]) for node_id in nodes}

            for i, node_i in enumerate(nodes):
                for j in range(i + 1, num_nodes):
                    node_j = nodes[j]
                    pos_i = np.array(positions[node_i])
                    pos_j = np.array(positions[node_j])
                    delta = pos_i - pos_j
                    distance = max(np.linalg.norm(delta), 0.01)

                    repulsion = (k * k) / distance
                    force = (delta / distance) * repulsion

                    forces[node_i] += force
                    forces[node_j] -= force

            for edge in self.reader.get_edges():
                source = edge['source']
                target = edge['target']

                if source in positions and target in positions:
                    pos_source = np.array(positions[source])
                    pos_target = np.array(positions[target])
                    delta = pos_source - pos_target
                    distance = max(np.linalg.norm(delta), 0.01)

                    attraction = (distance * distance) / k
                    force = (delta / distance) * attraction

                    forces[source] -= force
                    forces[target] += force

            for node_id in nodes:
                force = forces[node_id]
                force_magnitude = np.linalg.norm(force)

                if force_magnitude > 0:
                    displacement = (force / force_magnitude) * min(force_magnitude, temp)
                    new_pos = np.array(positions[node_id]) + displacement
                    new_pos = np.clip(new_pos, -2, 2)
                    positions[node_id] = tuple(new_pos)

            temp *= cooling_factor

        elapsed = time.time() - start_time
        self.logger.debug(f"Spring layout calculado em {elapsed:.3f}s")

        return positions

    def _random_layout(self) -> Dict[str, Tuple[float, float]]:
        """Gera layout aleatório."""
        nodes = list(self.reader.get_nodes().keys())
        np.random.seed(42)
        positions = {}

        for node_id in nodes:
            x = np.random.rand() * 2 - 1
            y = np.random.rand() * 2 - 1
            positions[node_id] = (x, y)

        return positions

    def draw(
        self,
        fig: Figure = None,
        ax: plt.Axes = None,
        layout: str = "spring",
        show_labels: bool = True,
        show_weights: bool = False,
        node_size: int = 300,
        font_size: int = 8,
        max_label_length: int = 15
    ) -> Tuple[Figure, plt.Axes]:
        """
        Desenha o grafo.

        Args:
            fig: Figura matplotlib
            ax: Eixo matplotlib
            layout: Tipo de layout ("circular", "spring", "random")
            show_labels: Mostrar labels dos nós
            show_weights: Mostrar pesos das arestas
            node_size: Tamanho base dos nós
            font_size: Tamanho da fonte
            max_label_length: Comprimento máximo do label

        Returns:
            Tuple (Figure, Axes)
        """
        start_time = time.time()
        self.logger.info(f"Iniciando desenho do grafo (layout={layout}, show_labels={show_labels}, show_weights={show_weights})")

        try:
            if fig is None or ax is None:
                fig, ax = plt.subplots(figsize=(12, 10))
                self.logger.debug("Criada nova figura matplotlib")

            ax.clear()

            nodes = self.reader.get_nodes()
            edges = self.reader.get_edges()

            self.logger.debug(f"Obtidos {len(nodes)} nós e {len(edges)} arestas")

            if not nodes:
                self.logger.warning("Grafo vazio, nada a desenhar")
                ax.text(0.5, 0.5, "Grafo vazio", ha='center', va='center',
                       transform=ax.transAxes, fontsize=14)
                ax.set_xlim(-1, 1)
                ax.set_ylim(-1, 1)
                ax.axis('off')
                return fig, ax

            self.logger.info(f"Gerando layout: {layout}")
            layout_start = time.time()

            if layout == "circular":
                self.positions = self._circular_layout()
            elif layout == "spring":
                self.positions = self._spring_layout()
            elif layout == "random":
                self.positions = self._random_layout()
            else:
                self.positions = self._spring_layout()

            layout_elapsed = time.time() - layout_start
            self.logger.info(f"Layout gerado em {layout_elapsed:.3f}s")

            # Calcula graus para dimensionar nós
            self.logger.debug("Calculando graus dos nós")
            node_degrees = {node_id: 0 for node_id in nodes}
            for edge in edges:
                if edge['source'] in node_degrees:
                    node_degrees[edge['source']] += 1
                if edge['target'] in node_degrees:
                    node_degrees[edge['target']] += 1

            # Desenha arestas
            self.logger.debug(f"Desenhando {len(edges)} arestas")
            draw_start = time.time()

            for edge in edges:
                source = edge['source']
                target = edge['target']

                if source in self.positions and target in self.positions:
                    x1, y1 = self.positions[source]
                    x2, y2 = self.positions[target]

                    weight = edge.get('weight', 1.0)
                    line_width = 1.5
                    alpha = 0.6 

                    ax.plot([x1, x2], [y1, y2], 'darkgray', linewidth=line_width,
                           alpha=alpha, zorder=1)

                    # Desenha seta
                    dx = x2 - x1
                    dy = y2 - y1
                    length = math.sqrt(dx**2 + dy**2)

                    if length > 0:
                        arrow_pos = 0.8
                        arrow_x = x1 + dx * arrow_pos
                        arrow_y = y1 + dy * arrow_pos
                        arrow_size = 0.03 

                        ax.arrow(arrow_x, arrow_y, dx * 0.001, dy * 0.001,
                                head_width=arrow_size, head_length=arrow_size,
                                fc='darkgray', ec='darkgray', alpha=0.7, zorder=2)

                    # Mostra peso
                    if show_weights and weight > 1:
                        mid_x = (x1 + x2) / 2
                        mid_y = (y1 + y2) / 2
                        ax.text(mid_x, mid_y, f'{weight:.0f}',
                               fontsize=max(font_size - 2, 6),
                               ha='center', va='center',
                               bbox=dict(boxstyle='round,pad=0.2', facecolor='white',
                                       edgecolor='none', alpha=0.7),
                               zorder=3)

            edges_elapsed = time.time() - draw_start
            self.logger.debug(f"Arestas desenhadas em {edges_elapsed:.3f}s")

            # Desenha nós
            self.logger.debug(f"Desenhando {len(nodes)} nós")
            nodes_start = time.time()

            # Tamanho fixo para todos os nós
            node_size = 0.03  
            max_degree = max(node_degrees.values()) if node_degrees else 1

            for node_id, node_data in nodes.items():
                if node_id in self.positions:
                    x, y = self.positions[node_id]
                    degree = node_degrees.get(node_id, 0)

                    size = node_size

                    # Cor baseada no grau RELATIVO (não absoluto)
                    relative_degree = degree / max_degree if max_degree > 0 else 0
                    if degree == 0:
                        color = 'lightgray'
                    elif relative_degree < 0.2:
                        color = 'lightblue'
                    elif relative_degree < 0.5:
                        color = 'skyblue'
                    elif relative_degree < 0.8:
                        color = 'steelblue'
                    else:
                        color = 'darkblue' 

                    # Desenha círculo 
                    circle = plt.Circle((x, y), size, color=color,
                                      ec='black', linewidth=1.0, zorder=4, alpha=0.95)
                    ax.add_patch(circle)

                    # Desenha label
                    if show_labels:
                        label = node_data['label']

                        if len(label) > max_label_length:
                            label = label[:max_label_length-3] + "..."

                        # Mostra labels apenas para nós importantes em grafos grandes
                        show_this_label = False
                        if len(nodes) < 50:
                            show_this_label = degree > 0 
                        elif len(nodes) < 200:
                            show_this_label = relative_degree > 0.2  # Top 20%
                        else:
                            show_this_label = relative_degree > 0.5  # Top 50%

                        if show_this_label:
                            label_size = max(font_size - 2, 5)
                            ax.text(x, y, label, fontsize=label_size,
                                   ha='center', va='center', zorder=5,
                                   fontweight='bold', color='white',
                                   bbox=dict(boxstyle='round,pad=0.2',
                                           facecolor='black',
                                           alpha=0.3,
                                           edgecolor='none'))

            nodes_elapsed = time.time() - nodes_start
            self.logger.debug(f"Nós desenhados em {nodes_elapsed:.3f}s")

            # Configurações
            self.logger.debug("Aplicando configurações finais")
            ax.set_xlim(-2.2, 2.2)
            ax.set_ylim(-2.2, 2.2)
            ax.set_aspect('equal')
            ax.axis('off')

            # Título com estatísticas
            stats = self.reader.get_statistics()
            title = f"Nós: {stats['num_nodes']} | Arestas: {stats['num_edges']}"
            if 'density' in stats:
                title += f" | Densidade: {stats['density']:.4f}"

            metadata = self.reader.get_metadata()
            if 'description' in metadata and metadata['description']:
                title = metadata['description'] + "\n" + title

            ax.set_title(title, fontsize=11, pad=20, fontweight='bold')

            fig.tight_layout()

            total_elapsed = time.time() - start_time
            self.logger.info(f"Grafo desenhado com sucesso em {total_elapsed:.3f}s")

            return fig, ax

        except Exception as e:
            self.logger.exception("Erro ao desenhar grafo")
            raise

    def get_statistics(self) -> Dict:
        """Retorna estatísticas do grafo."""
        return self.reader.get_statistics()
