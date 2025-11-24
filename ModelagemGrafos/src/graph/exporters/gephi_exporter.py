"""
Exportador de grafos para o formato GEXF (GEPHI).

O formato GEXF (Graph Exchange XML Format) e usado pelo software GEPHI
para visualizacao e analise de grafos.
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime
from typing import Optional
from ..abstract_graph import AbstractGraph


class GephiExporter:
    """
    Exporta grafos para o formato GEXF compativel com GEPHI.

    O formato GEXF suporta:
    - Grafos direcionados e nao-direcionados
    - Pesos de vertices e arestas
    - Rotulos de vertices
    - Metadados do grafo
    """

    @staticmethod
    def export(
        graph: AbstractGraph,
        filename: str,
        graph_label: str = "Graph",
        description: str = ""
    ) -> None:
        """
        Exporta um grafo para arquivo GEXF.

        Args:
            graph: Grafo a ser exportado
            filename: Caminho do arquivo de saida (.gexf)
            graph_label: Rotulo/nome do grafo
            description: Descricao do grafo

        Example:
            >>> g = AdjacencyMatrixGraph(3)
            >>> g.add_edge(0, 1)
            >>> GephiExporter.export(g, "meu_grafo.gexf", "Meu Grafo")
        """
        # Cria estrutura XML
        gexf = ET.Element('gexf', {
            'xmlns': 'http://www.gexf.net/1.3',
            'version': '1.3'
        })

        # Metadados
        meta = ET.SubElement(gexf, 'meta', {
            'lastmodifieddate': datetime.now().strftime('%Y-%m-%d')
        })
        ET.SubElement(meta, 'creator').text = 'Graph Library - Python'
        ET.SubElement(meta, 'description').text = description

        # Grafo
        graph_elem = ET.SubElement(gexf, 'graph', {
            'defaultedgetype': 'directed',
            'mode': 'static'
        })

        # Atributos de vertices (pesos)
        attributes_nodes = ET.SubElement(graph_elem, 'attributes', {
            'class': 'node'
        })
        ET.SubElement(attributes_nodes, 'attribute', {
            'id': '0',
            'title': 'weight',
            'type': 'float'
        })

        # Atributos de arestas (pesos)
        attributes_edges = ET.SubElement(graph_elem, 'attributes', {
            'class': 'edge'
        })
        ET.SubElement(attributes_edges, 'attribute', {
            'id': '0',
            'title': 'weight',
            'type': 'float'
        })

        # Nos (vertices)
        nodes = ET.SubElement(graph_elem, 'nodes')
        for v in range(graph.num_vertices):
            # Label do vertice
            label = graph.get_vertex_label(v)
            if label is None:
                label = f"v{v}"

            node = ET.SubElement(nodes, 'node', {
                'id': str(v),
                'label': label
            })

            # Peso do vertice
            attvalues = ET.SubElement(node, 'attvalues')
            ET.SubElement(attvalues, 'attvalue', {
                'for': '0',
                'value': str(graph.get_vertex_weight(v))
            })

        # Arestas
        edges = ET.SubElement(graph_elem, 'edges')
        edge_id = 0

        for u in range(graph.num_vertices):
            successors = graph.get_successors(u)
            for v in successors:
                edge = ET.SubElement(edges, 'edge', {
                    'id': str(edge_id),
                    'source': str(u),
                    'target': str(v),
                    'weight': str(graph.get_edge_weight(u, v))
                })

                # Peso da aresta como atributo tambem
                attvalues = ET.SubElement(edge, 'attvalues')
                ET.SubElement(attvalues, 'attvalue', {
                    'for': '0',
                    'value': str(graph.get_edge_weight(u, v))
                })

                edge_id += 1

        # Formata XML com indentacao
        xml_str = minidom.parseString(
            ET.tostring(gexf, encoding='unicode')
        ).toprettyxml(indent='  ')

        # Remove linhas vazias extras
        xml_str = '\n'.join([line for line in xml_str.split('\n') if line.strip()])

        # Salva arquivo
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(xml_str)

    @staticmethod
    def export_with_stats(
        graph: AbstractGraph,
        filename: str,
        graph_label: str = "Graph",
        description: str = ""
    ) -> dict:
        """
        Exporta grafo e retorna estatisticas.

        Args:
            graph: Grafo a ser exportado
            filename: Caminho do arquivo de saida
            graph_label: Rotulo do grafo
            description: Descricao

        Returns:
            Dicionario com estatisticas do grafo exportado
        """
        # Exporta
        GephiExporter.export(graph, filename, graph_label, description)

        # Calcula estatisticas
        stats = {
            'vertices': graph.num_vertices,
            'edges': graph.num_edges,
            'density': 0.0,
            'is_complete': graph.is_complete_graph(),
            'is_empty': graph.is_empty_graph(),
            'filename': filename
        }

        # Densidade do grafo
        if graph.num_vertices > 1:
            max_edges = graph.num_vertices * (graph.num_vertices - 1)
            stats['density'] = graph.num_edges / max_edges if max_edges > 0 else 0.0

        return stats
