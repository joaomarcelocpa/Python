"""
Script de teste para as métricas de análise de grafos
"""

import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from src.graph.adjacency_list_graph import AdjacencyListGraph
from src.utils.graph_metrics_analyzer import GraphMetricsAnalyzer


def create_sample_graph():
    """
    Cria um grafo de exemplo para testar as métricas.

    Estrutura:
    - 10 vértices representando colaboradores
    - Arestas representando colaborações
    """
    graph = AdjacencyListGraph(10)

    # Define labels para os vértices
    labels = [
        "Alice", "Bob", "Carol", "Dave", "Eve",
        "Frank", "Grace", "Heidi", "Ivan", "Judy"
    ]

    for i, label in enumerate(labels):
        graph.set_vertex_label(i, label)

    # Adiciona arestas (colaborações)
    # Grupo 1: Alice, Bob, Carol (comunidade 1)
    edges = [
        (0, 1), (1, 0),  # Alice <-> Bob
        (0, 2), (2, 0),  # Alice <-> Carol
        (1, 2), (2, 1),  # Bob <-> Carol

        # Grupo 2: Dave, Eve, Frank (comunidade 2)
        (3, 4), (4, 3),  # Dave <-> Eve
        (3, 5), (5, 3),  # Dave <-> Frank
        (4, 5), (5, 4),  # Eve <-> Frank

        # Grupo 3: Grace, Heidi, Ivan (comunidade 3)
        (6, 7), (7, 6),  # Grace <-> Heidi
        (6, 8), (8, 6),  # Grace <-> Ivan
        (7, 8), (8, 7),  # Heidi <-> Ivan

        # Pontes entre comunidades
        (2, 3),  # Carol -> Dave (ponte entre grupo 1 e 2)
        (5, 6),  # Frank -> Grace (ponte entre grupo 2 e 3)

        # Judy conectada a vários grupos (hub)
        (9, 0), (9, 3), (9, 6),  # Judy -> Alice, Dave, Grace
        (0, 9), (3, 9), (6, 9),  # Retorno
    ]

    for u, v in edges:
        graph.add_edge(u, v)

    # Define alguns pesos nas arestas
    for u, v in edges:
        graph.set_edge_weight(u, v, 1.0)

    return graph


def test_basic_metrics():
    """Testa métricas básicas."""
    print("\n" + "=" * 80)
    print("TESTE 1: MÉTRICAS BÁSICAS")
    print("=" * 80)

    graph = create_sample_graph()
    analyzer = GraphMetricsAnalyzer(graph)

    print(f"\nGrafo criado: {graph.num_vertices} vértices, {graph.num_edges} arestas")

    # Densidade
    density = analyzer.structure.network_density()
    print(f"Densidade da rede: {density:.4f}")

    # Reciprocidade
    reciprocity = analyzer.structure.reciprocity()
    print(f"Reciprocidade: {reciprocity:.4f}")

    print("\n[OK] Teste de metricas basicas concluido")


def test_centrality():
    """Testa métricas de centralidade."""
    print("\n" + "=" * 80)
    print("TESTE 2: MÉTRICAS DE CENTRALIDADE")
    print("=" * 80)

    graph = create_sample_graph()
    analyzer = GraphMetricsAnalyzer(graph)

    # PageRank
    print("\nTop 5 por PageRank:")
    top_pagerank = analyzer.get_top_central_nodes('pagerank', 5)
    for i, (vertex, score, label) in enumerate(top_pagerank, 1):
        print(f"  {i}. {label}: {score:.4f}")

    # Betweenness
    print("\nTop 5 por Betweenness Centrality:")
    top_betweenness = analyzer.get_top_central_nodes('betweenness', 5)
    for i, (vertex, score, label) in enumerate(top_betweenness, 1):
        print(f"  {i}. {label}: {score:.4f}")

    # Degree
    print("\nTop 5 por Degree Centrality:")
    top_degree = analyzer.get_top_central_nodes('degree_total', 5)
    for i, (vertex, score, label) in enumerate(top_degree, 1):
        print(f"  {i}. {label}: {score:.4f}")

    print("\n[OK] Teste de centralidade concluido")


def test_communities():
    """Testa detecção de comunidades."""
    print("\n" + "=" * 80)
    print("TESTE 3: DETECÇÃO DE COMUNIDADES")
    print("=" * 80)

    graph = create_sample_graph()
    analyzer = GraphMetricsAnalyzer(graph)

    # Detecta comunidades
    results = analyzer.analyze_community_only()

    print(f"\nNúmero de comunidades detectadas: {results['num_communities']}")
    print(f"Modularidade: {results['modularity']:.4f}")
    print(f"Método: {results['method']}")

    # Mostra estatísticas das comunidades
    print("\nEstatísticas por comunidade:")
    for comm_id, stats in results['community_statistics'].items():
        print(f"\n  Comunidade {comm_id}:")
        print(f"    Tamanho: {stats['size']} membros")
        print(f"    Arestas internas: {stats['internal_edges']}")
        print(f"    Arestas externas: {stats['external_edges']}")

        # Mostra membros
        members = analyzer.get_community_members(comm_id)
        member_labels = [label for _, label in members]
        print(f"    Membros: {', '.join(member_labels)}")

    # Bridging ties
    print("\nTop 5 Bridging Ties:")
    bridging = results['bridging_ties']
    sorted_bridging = sorted(bridging.items(), key=lambda x: x[1], reverse=True)
    for i, (vertex, score) in enumerate(sorted_bridging[:5], 1):
        label = graph.get_vertex_label(vertex) or f"V{vertex}"
        print(f"  {i}. {label}: {score:.4f}")

    print("\n[OK] Teste de comunidades concluido")


def test_full_analysis():
    """Testa análise completa."""
    print("\n" + "=" * 80)
    print("TESTE 4: ANÁLISE COMPLETA")
    print("=" * 80)

    graph = create_sample_graph()
    analyzer = GraphMetricsAnalyzer(graph)

    # Executa análise completa
    results = analyzer.analyze_all()

    # Gera relatório
    print("\n" + analyzer.generate_report(results))

    # Exporta para JSON
    output_file = "output/metrics_analysis.json"
    Path("output").mkdir(exist_ok=True)
    analyzer.export_to_json(output_file, results)
    print(f"\n[OK] Resultados exportados para: {output_file}")

    print("\n[OK] Teste de analise completa concluido")


def main():
    """Executa todos os testes."""
    print("\n" + "=" * 80)
    print("INICIANDO TESTES DAS MÉTRICAS DE ANÁLISE DE GRAFOS")
    print("=" * 80)

    try:
        test_basic_metrics()
        test_centrality()
        test_communities()
        test_full_analysis()

        print("\n" + "=" * 80)
        print("[OK] TODOS OS TESTES CONCLUIDOS COM SUCESSO!")
        print("=" * 80 + "\n")

    except Exception as e:
        print(f"\n[ERRO] {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
