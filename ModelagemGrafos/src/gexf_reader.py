"""
Leitor de arquivos GEXF para visualização
"""

import xml.etree.ElementTree as ET
from typing import Dict, List
from src.graph.adjacency_list_graph import AdjacencyListGraph


class GEXFReader:
    """
    Leitor simples de arquivos GEXF gerados pelo projeto.
    """

    def __init__(self, filepath: str):
        """
        Inicializa o leitor.

        Args:
            filepath: Caminho para o arquivo GEXF
        """
        self.filepath = filepath
        self.nodes = {} 
        self.edges = [] 
        self.graph_type = "directed"
        self.metadata = {}

    def parse(self):
        """
        Faz parse do arquivo GEXF.
        """
        tree = ET.parse(self.filepath)
        root = tree.getroot()


        ns = {'gexf': 'http://www.gexf.net/1.3'}

        # Pega metadados
        meta = root.find('.//gexf:meta', ns)
        if meta is not None:
            self.metadata['creator'] = meta.find('gexf:creator', ns).text if meta.find('gexf:creator', ns) is not None else ''
            self.metadata['description'] = meta.find('gexf:description', ns).text if meta.find('gexf:description', ns) is not None else ''

        # Pega tipo do grafo
        graph = root.find('.//gexf:graph', ns)
        if graph is not None:
            self.graph_type = graph.get('defaultedgetype', 'directed')

        # Lê nós
        nodes_elem = root.find('.//gexf:nodes', ns)
        if nodes_elem is not None:
            for node in nodes_elem.findall('gexf:node', ns):
                node_id = node.get('id')
                node_label = node.get('label', node_id)

                self.nodes[node_id] = {
                    'label': node_label,
                    'attributes': {}
                }

        # Lê arestas
        edges_elem = root.find('.//gexf:edges', ns)
        if edges_elem is not None:
            for edge in edges_elem.findall('gexf:edge', ns):
                source = edge.get('source')
                target = edge.get('target')
                weight = float(edge.get('weight', 1.0))

                self.edges.append({
                    'source': source,
                    'target': target,
                    'weight': weight
                })

    def get_nodes(self) -> Dict:
        """Retorna dicionário de nós."""
        return self.nodes

    def get_edges(self) -> List[Dict]:
        """Retorna lista de arestas."""
        return self.edges

    def get_metadata(self) -> Dict:
        """Retorna metadados do grafo."""
        return self.metadata

    def is_directed(self) -> bool:
        """Retorna se o grafo é direcionado."""
        return self.graph_type == 'directed'

    def get_statistics(self) -> Dict:
        """
        Retorna estatísticas do grafo.

        Returns:
            Dicionário com estatísticas
        """
        num_nodes = len(self.nodes)
        num_edges = len(self.edges)

        # Calcula densidade
        if num_nodes > 1:
            max_edges = num_nodes * (num_nodes - 1) if self.is_directed() else num_nodes * (num_nodes - 1) / 2
            density = num_edges / max_edges if max_edges > 0 else 0
        else:
            density = 0

        # Calcula graus
        in_degree = {node_id: 0 for node_id in self.nodes}
        out_degree = {node_id: 0 for node_id in self.nodes}

        for edge in self.edges:
            source = edge['source']
            target = edge['target']

            if source in out_degree:
                out_degree[source] += 1
            if target in in_degree:
                in_degree[target] += 1

        total_degrees = [in_degree[n] + out_degree[n] for n in self.nodes]

        stats = {
            'num_nodes': num_nodes,
            'num_edges': num_edges,
            'density': density,
            'is_directed': self.is_directed(),
        }

        if total_degrees:
            stats['avg_degree'] = sum(total_degrees) / len(total_degrees)
            stats['max_degree'] = max(total_degrees)
            stats['min_degree'] = min(total_degrees)

        return stats

    def to_graph(self):
        """
        Converte o GEXF carregado para um AdjacencyListGraph.

        Returns:
            AdjacencyListGraph com os dados do GEXF
        """
        # Parse se ainda não foi feito
        if not self.nodes:
            self.parse()

        # Cria mapeamento de IDs do GEXF para índices numéricos
        node_ids = list(self.nodes.keys())
        id_to_index = {node_id: idx for idx, node_id in enumerate(node_ids)}

        # Cria grafo
        num_vertices = len(self.nodes)
        graph = AdjacencyListGraph(num_vertices)

        # Adiciona labels
        for node_id, idx in id_to_index.items():
            label = self.nodes[node_id]['label']
            graph.set_vertex_label(idx, label)

        # Adiciona arestas
        for edge in self.edges:
            source = edge['source']
            target = edge['target']
            weight = edge['weight']

            if source in id_to_index and target in id_to_index:
                source_idx = id_to_index[source]
                target_idx = id_to_index[target]

                graph.add_edge(source_idx, target_idx)
                graph.set_edge_weight(source_idx, target_idx, weight)

        return graph
