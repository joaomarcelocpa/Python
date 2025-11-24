"""
Script para validar as métricas calculadas
Testa com grafos pequenos conhecidos para verificar se os valores fazem sentido
"""

from src.graph.adjacency_list_graph import AdjacencyListGraph
from src.utils.centrality_metrics import CentralityMetrics
from src.utils.structure_metrics import StructureMetrics
from src.utils.community_metrics import CommunityMetrics


def test_simple_star_graph():
    """
    Testa um grafo em estrela simples:
        0 -> 1
        0 -> 2
        0 -> 3

    Vértice 0 deve ter:
    - Maior out-degree centrality
    - Maior PageRank
    - Maior betweenness (é ponte)
    """
    print("="*60)
    print("TESTE 1: GRAFO EM ESTRELA (Star Graph)")
    print("="*60)
    print("Estrutura: 0 -> 1, 0 -> 2, 0 -> 3")
    print()

    graph = AdjacencyListGraph(4)
    graph.add_edge(0, 1)
    graph.add_edge(0, 2)
    graph.add_edge(0, 3)

    # Labels
    graph.set_vertex_label(0, "Center")
    graph.set_vertex_label(1, "Node1")
    graph.set_vertex_label(2, "Node2")
    graph.set_vertex_label(3, "Node3")

    # Centralidade
    cent = CentralityMetrics(graph)

    # Degree
    degree = cent.degree_centrality()
    print("Degree Centrality:")
    print(f"  Vertice 0 (Center): out={degree['out_degree'][0]:.3f}, in={degree['in_degree'][0]:.3f}")
    print(f"  Vertice 1 (Node1):  out={degree['out_degree'][1]:.3f}, in={degree['in_degree'][1]:.3f}")
    print(f"  [OK] Esperado: Center tem out-degree=1.0 (3/3), outros tem in-degree=0.33 (1/3)")
    print()

    # PageRank
    pagerank = cent.pagerank()
    print("PageRank:")
    for v in range(4):
        print(f"  Vértice {v}: {pagerank[v]:.4f}")
    print(f"  [OK]Esperado: Todos relativamente iguais (sem links de entrada ao center)")
    print()

    # Betweenness
    betweenness = cent.betweenness_centrality()
    print("Betweenness Centrality:")
    for v in range(4):
        print(f"  Vértice {v}: {betweenness[v]:.4f}")
    print(f"  [OK]Esperado: Todos zero (sem caminhos passando por vértices)")
    print()

    # Estrutura
    struct = StructureMetrics(graph)

    density = struct.network_density()
    print(f"Densidade: {density:.4f}")
    print(f"  [OK]Esperado: 3/(4*3) = 0.25")
    print()

    reciprocity = struct.reciprocity()
    print(f"Reciprocidade: {reciprocity:.4f}")
    print(f"  [OK]Esperado: 0.0 (nenhuma aresta bidirecional)")
    print()


def test_bidirectional_graph():
    """
    Testa um grafo bidirecional:
        0 <-> 1
        0 <-> 2
    """
    print("\n" + "="*60)
    print("TESTE 2: GRAFO BIDIRECIONAL")
    print("="*60)
    print("Estrutura: 0 <-> 1, 0 <-> 2")
    print()

    graph = AdjacencyListGraph(3)
    graph.add_edge(0, 1)
    graph.add_edge(1, 0)
    graph.add_edge(0, 2)
    graph.add_edge(2, 0)

    graph.set_vertex_label(0, "Center")
    graph.set_vertex_label(1, "Node1")
    graph.set_vertex_label(2, "Node2")

    # Estrutura
    struct = StructureMetrics(graph)

    density = struct.network_density()
    print(f"Densidade: {density:.4f}")
    print(f"  [OK]Esperado: 4/(3*2) = 0.6667")
    print()

    reciprocity = struct.reciprocity()
    print(f"Reciprocidade: {reciprocity:.4f}")
    print(f"  [OK]Esperado: 1.0 (todas as arestas são bidirecionais)")
    print()

    # Clustering
    clustering = struct.clustering_coefficient()
    print(f"Clustering médio: {clustering['average']:.4f}")
    print(f"  Vértice 0: {clustering['local'][0]:.4f}")
    print(f"  Vértice 1: {clustering['local'][1]:.4f}")
    print(f"  Vértice 2: {clustering['local'][2]:.4f}")
    print(f"  [OK]Esperado: Vértices 1 e 2 têm clustering 0 (não conectados)")
    print()


def test_triangle_graph():
    """
    Testa um triângulo completo:
        0 -> 1 -> 2 -> 0
    """
    print("\n" + "="*60)
    print("TESTE 3: TRIÂNGULO DIRECIONADO")
    print("="*60)
    print("Estrutura: 0 -> 1 -> 2 -> 0 (ciclo)")
    print()

    graph = AdjacencyListGraph(3)
    graph.add_edge(0, 1)
    graph.add_edge(1, 2)
    graph.add_edge(2, 0)

    # Centralidade
    cent = CentralityMetrics(graph)

    # Degree (todos devem ser iguais)
    degree = cent.degree_centrality()
    print("Degree Centrality:")
    for v in range(3):
        print(f"  Vértice {v}: in={degree['in_degree'][v]:.3f}, out={degree['out_degree'][v]:.3f}")
    print(f"  [OK]Esperado: Todos iguais (in=0.5, out=0.5)")
    print()

    # PageRank (todos devem ser iguais)
    pagerank = cent.pagerank()
    print("PageRank:")
    for v in range(3):
        print(f"  Vértice {v}: {pagerank[v]:.4f}")
    print(f"  [OK]Esperado: Todos iguais (~0.333)")
    print()

    # Estrutura
    struct = StructureMetrics(graph)

    density = struct.network_density()
    print(f"Densidade: {density:.4f}")
    print(f"  [OK]Esperado: 3/(3*2) = 0.5")
    print()

    reciprocity = struct.reciprocity()
    print(f"Reciprocidade: {reciprocity:.4f}")
    print(f"  [OK]Esperado: 0.0 (nenhuma aresta bidirecional direta)")
    print()

    avg_path = struct.average_path_length()
    print(f"Caminho médio: {avg_path:.4f}")
    print(f"  [OK]Esperado: (1+2+1+2+1+2)/6 = 1.5")
    print()

    diameter = struct.diameter()
    print(f"Diâmetro: {diameter}")
    print(f"  [OK]Esperado: 2 (maior distância no ciclo)")
    print()


def test_two_communities():
    """
    Testa detecção de comunidades em grafo com 2 comunidades óbvias:
        Comunidade 1: 0 <-> 1
        Comunidade 2: 2 <-> 3
        Ponte: 1 -> 2
    """
    print("\n" + "="*60)
    print("TESTE 4: DUAS COMUNIDADES COM PONTE")
    print("="*60)
    print("Estrutura: [0 <-> 1] -> [2 <-> 3]")
    print()

    graph = AdjacencyListGraph(4)
    # Comunidade 1
    graph.add_edge(0, 1)
    graph.add_edge(1, 0)
    # Ponte
    graph.add_edge(1, 2)
    # Comunidade 2
    graph.add_edge(2, 3)
    graph.add_edge(3, 2)

    # Comunidades
    comm = CommunityMetrics(graph)

    communities = comm.detect_communities_label_propagation()
    print("Comunidades detectadas (Label Propagation):")
    for v, c in communities.items():
        print(f"  Vértice {v}: Comunidade {c}")

    num_communities = len(set(communities.values()))
    print(f"\n  Total de comunidades: {num_communities}")
    print(f"  [OK]Esperado: 2 comunidades")
    print()

    modularity = comm.modularity(communities)
    print(f"Modularidade: {modularity:.4f}")
    print(f"  [OK]Esperado: > 0 (boa divisão em comunidades)")
    print()

    # Bridging
    bridging = comm.bridging_ties(communities)
    print("Bridging Ties:")
    for v in range(4):
        print(f"  Vértice {v}: {bridging[v]:.4f}")
    print(f"  [OK]Esperado: Vértice 1 deve ter alto bridging (conecta 2 comunidades)")
    print()


def main():
    """Executa todos os testes"""
    print("\n" + "#"*60)
    print("# VALIDAÇÃO DAS MÉTRICAS DE GRAFOS")
    print("#"*60)
    print()

    test_simple_star_graph()
    test_bidirectional_graph()
    test_triangle_graph()
    test_two_communities()

    print("\n" + "#"*60)
    print("# TESTES CONCLUÍDOS")
    print("#"*60)
    print()
    print("Compare os valores calculados com os esperados.")
    print("Pequenas diferenças são normais devido a arredondamentos.")
    print()


if __name__ == "__main__":
    main()
