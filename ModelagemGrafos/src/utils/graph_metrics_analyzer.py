"""
Analisador Completo de Métricas de Grafos
Une todas as métricas em uma interface única
"""

from typing import Dict, Any
import json
from datetime import datetime
from src.graph.abstract_graph import AbstractGraph
from src.utils.centrality_metrics import CentralityMetrics
from src.utils.structure_metrics import StructureMetrics
from src.utils.community_metrics import CommunityMetrics


class GraphMetricsAnalyzer:
    """
    Classe principal para análise completa de métricas de grafos.

    Une métricas de:
    - Centralidade (degree, betweenness, closeness, PageRank, eigenvector)
    - Estrutura (densidade, clustering, assortatividade)
    - Comunidade (detecção de comunidades, modularidade, bridging ties)
    """

    def __init__(self, graph: AbstractGraph):
        """
        Inicializa o analisador de métricas.

        Args:
            graph: Grafo a ser analisado
        """
        self.graph = graph
        self.centrality = CentralityMetrics(graph)
        self.structure = StructureMetrics(graph)
        self.community = CommunityMetrics(graph)

    def analyze_all(self) -> Dict[str, Any]:
        """
        Executa análise completa de todas as métricas.

        Returns:
            Dicionário com todas as métricas organizadas por categoria
        """
        print("Iniciando análise completa do grafo...")
        print(f"Vértices: {self.graph.num_vertices}, Arestas: {self.graph.num_edges}")

        results = {
            'metadata': self._get_metadata(),
            'basic_info': self._get_basic_info(),
            'centrality': {},
            'structure': {},
            'community': {}
        }

        # Métricas de centralidade
        print("\nCalculando metricas de centralidade...")
        results['centrality'] = self.centrality.get_all_centralities()
        print("  [OK] Centralidades calculadas")

        # Métricas de estrutura
        print("\nCalculando metricas de estrutura...")
        results['structure'] = self.structure.get_all_structure_metrics()
        print("  [OK] Estrutura analisada")

        # Métricas de comunidade
        print("\nDetectando comunidades...")
        results['community'] = self.community.get_all_community_metrics()
        print(f"  [OK] {results['community']['num_communities']} comunidades detectadas")

        # Rankings
        print("\nCalculando rankings...")
        results['rankings'] = self._calculate_rankings(results)
        print("  [OK] Rankings calculados")

        print("\n[OK] Analise completa finalizada!")

        return results

    def analyze_centrality_only(self) -> Dict[str, Any]:
        """
        Analisa apenas métricas de centralidade.

        Returns:
            Dicionário com métricas de centralidade
        """
        return self.centrality.get_all_centralities()

    def analyze_structure_only(self) -> Dict[str, Any]:
        """
        Analisa apenas métricas de estrutura.

        Returns:
            Dicionário com métricas de estrutura
        """
        return self.structure.get_all_structure_metrics()

    def analyze_community_only(self) -> Dict[str, Any]:
        """
        Analisa apenas métricas de comunidade.

        Returns:
            Dicionário com métricas de comunidade
        """
        return self.community.get_all_community_metrics()

    def get_top_central_nodes(self, metric: str = 'pagerank', n: int = 10) -> list:
        """
        Retorna os N vértices mais centrais segundo uma métrica.

        Args:
            metric: Nome da métrica ('degree_in', 'degree_out', 'degree_total',
                   'betweenness', 'closeness', 'pagerank', 'eigenvector')
            n: Número de vértices a retornar

        Returns:
            Lista de tuplas (vértice, score, label)
        """
        centralities = self.centrality.get_all_centralities()

        if metric not in centralities:
            raise ValueError(f"Métrica '{metric}' não reconhecida")

        scores = centralities[metric]

        # Ordena por score (decrescente)
        sorted_nodes = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        # Adiciona labels
        result = []
        for vertex, score in sorted_nodes[:n]:
            label = self.graph.get_vertex_label(vertex) or f"V{vertex}"
            result.append((vertex, score, label))

        return result

    def get_community_members(self, community_id: int) -> list:
        """
        Retorna membros de uma comunidade específica.

        Args:
            community_id: ID da comunidade

        Returns:
            Lista de vértices na comunidade
        """
        communities = self.community.detect_communities_louvain()

        members = [v for v, c in communities.items() if c == community_id]

        # Adiciona labels
        result = []
        for vertex in members:
            label = self.graph.get_vertex_label(vertex) or f"V{vertex}"
            result.append((vertex, label))

        return result

    def export_to_json(self, filepath: str, results: Dict[str, Any] = None):
        """
        Exporta resultados da análise para JSON.

        Args:
            filepath: Caminho do arquivo de saída
            results: Resultados a exportar (se None, executa análise completa)
        """
        if results is None:
            results = self.analyze_all()

        # Converte para formato serializável
        serializable_results = self._make_serializable(results)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(serializable_results, f, indent=2, ensure_ascii=False)

        print(f"\n[OK] Resultados exportados para: {filepath}")

    def generate_report(self, results: Dict[str, Any] = None) -> str:
        """
        Gera relatório textual das métricas.

        Args:
            results: Resultados da análise (se None, executa análise completa)

        Returns:
            String com relatório formatado
        """
        if results is None:
            results = self.analyze_all()

        report = []
        report.append("=" * 80)
        report.append("RELATÓRIO DE ANÁLISE DE GRAFO")
        report.append("=" * 80)

        # Informações básicas
        report.append("\n1. INFORMAÇÕES BÁSICAS")
        report.append("-" * 80)
        basic = results['basic_info']
        report.append(f"  Vértices: {basic['num_vertices']}")
        report.append(f"  Arestas: {basic['num_edges']}")
        report.append(f"  Densidade: {basic['density']:.4f}")

        # Estrutura
        report.append("\n2. MÉTRICAS DE ESTRUTURA E COESÃO")
        report.append("-" * 80)
        struct = results['structure']
        report.append(f"  Densidade: {struct['density']:.4f}")
        report.append(f"  Coeficiente de Aglomeração (Médio): {struct['clustering_average']:.4f}")
        report.append(f"  Coeficiente de Aglomeração (Global): {struct['clustering_global']:.4f}")
        report.append(f"  Assortatividade: {struct['assortativity']:.4f}")
        report.append(f"  Reciprocidade: {struct['reciprocity']:.4f}")
        report.append(f"  Caminho Médio: {struct['average_path_length']:.2f}")
        report.append(f"  Diâmetro: {struct['diameter']}")

        # Comunidades
        report.append("\n3. DETECÇÃO DE COMUNIDADES")
        report.append("-" * 80)
        comm = results['community']
        report.append(f"  Número de Comunidades: {comm['num_communities']}")
        report.append(f"  Modularidade: {comm['modularity']:.4f}")
        report.append(f"  Método Usado: {comm['method']}")

        # Top nodes por centralidade
        report.append("\n4. TOP 10 VÉRTICES POR CENTRALIDADE")
        report.append("-" * 80)

        if 'rankings' in results:
            rankings = results['rankings']

            report.append("\n  4.1. PageRank")
            for i, (vertex, score, label) in enumerate(rankings['top_pagerank'][:10], 1):
                report.append(f"    {i}. {label} (V{vertex}): {score:.4f}")

            report.append("\n  4.2. Betweenness Centrality")
            for i, (vertex, score, label) in enumerate(rankings['top_betweenness'][:10], 1):
                report.append(f"    {i}. {label} (V{vertex}): {score:.4f}")

            report.append("\n  4.3. Degree Centrality (Total)")
            for i, (vertex, score, label) in enumerate(rankings['top_degree'][:10], 1):
                report.append(f"    {i}. {label} (V{vertex}): {score:.4f}")

        # Bridging ties
        report.append("\n5. BRIDGING TIES (Top 10)")
        report.append("-" * 80)
        if 'rankings' in results and 'top_bridging' in rankings:
            for i, (vertex, score, label) in enumerate(rankings['top_bridging'][:10], 1):
                report.append(f"  {i}. {label} (V{vertex}): {score:.4f}")

        report.append("\n" + "=" * 80)

        return "\n".join(report)

    def _get_metadata(self) -> Dict[str, str]:
        """Retorna metadados da análise."""
        return {
            'timestamp': datetime.now().isoformat(),
            'graph_type': self.graph.__class__.__name__
        }

    def _get_basic_info(self) -> Dict[str, Any]:
        """Retorna informações básicas do grafo."""
        return {
            'num_vertices': self.graph.num_vertices,
            'num_edges': self.graph.num_edges,
            'density': self.structure.network_density()
        }

    def _calculate_rankings(self, results: Dict[str, Any]) -> Dict[str, list]:
        """
        Calcula rankings dos vértices por diferentes métricas.

        Args:
            results: Resultados da análise

        Returns:
            Dicionário com rankings
        """
        rankings = {}

        # Top PageRank
        pagerank = results['centrality']['pagerank']
        rankings['top_pagerank'] = self._rank_vertices(pagerank)

        # Top Betweenness
        betweenness = results['centrality']['betweenness']
        rankings['top_betweenness'] = self._rank_vertices(betweenness)

        # Top Degree
        degree = results['centrality']['degree_total']
        rankings['top_degree'] = self._rank_vertices(degree)

        # Top Closeness
        closeness = results['centrality']['closeness']
        rankings['top_closeness'] = self._rank_vertices(closeness)

        # Top Bridging
        bridging = results['community']['bridging_ties']
        rankings['top_bridging'] = self._rank_vertices(bridging)

        return rankings

    def _rank_vertices(self, scores: Dict[int, float], n: int = 10) -> list:
        """
        Rankeia vértices por score.

        Args:
            scores: Dicionário {vértice: score}
            n: Número de resultados

        Returns:
            Lista de tuplas (vértice, score, label)
        """
        sorted_items = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        result = []
        for vertex, score in sorted_items[:n]:
            label = self.graph.get_vertex_label(vertex) or f"V{vertex}"
            result.append((vertex, score, label))

        return result

    def _make_serializable(self, obj):
        """Converte objeto para formato serializável em JSON."""
        if isinstance(obj, dict):
            return {str(k): self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._make_serializable(item) for item in obj]
        elif isinstance(obj, (int, float, str, bool, type(None))):
            return obj
        else:
            return str(obj)
