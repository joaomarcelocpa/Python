"""
Teste especifico para modularidade
"""

from src.graph.adjacency_list_graph import AdjacencyListGraph
from src.utils.community_metrics import CommunityMetrics


def test_strong_communities():
    """
    Grafo com 2 comunidades fortemente conectadas internamente:
    Comunidade 1: 0 <-> 1 <-> 2 (todos conectados entre si)
    Comunidade 2: 3 <-> 4 <-> 5 (todos conectados entre si)
    Ponte fraca: 2 -> 3
    """
    print("TESTE: Comunidades Fortemente Conectadas")
    print("Estrutura:")
    print("  Comunidade 1: 0 <-> 1 <-> 2 (triangulo completo)")
    print("  Comunidade 2: 3 <-> 4 <-> 5 (triangulo completo)")
    print("  Ponte: 2 -> 3")
    print()

    graph = AdjacencyListGraph(6)

    # Comunidade 1 (triangulo completo bidirecional)
    graph.add_edge(0, 1)
    graph.add_edge(1, 0)
    graph.add_edge(1, 2)
    graph.add_edge(2, 1)
    graph.add_edge(0, 2)
    graph.add_edge(2, 0)

    # Comunidade 2 (triangulo completo bidirecional)
    graph.add_edge(3, 4)
    graph.add_edge(4, 3)
    graph.add_edge(4, 5)
    graph.add_edge(5, 4)
    graph.add_edge(3, 5)
    graph.add_edge(5, 3)

    # Ponte fraca
    graph.add_edge(2, 3)

    comm = CommunityMetrics(graph)

    # Detecta comunidades
    communities = comm.detect_communities_label_propagation()
    print("Comunidades detectadas:")
    for v in range(6):
        print(f"  Vertice {v}: Comunidade {communities[v]}")

    num_communities = len(set(communities.values()))
    print(f"\nNumero de comunidades: {num_communities}")

    # Modularidade
    modularity = comm.modularity(communities)
    print(f"Modularidade: {modularity:.4f}")
    print(f"  Esperado: Valor POSITIVO (boa divisao)")
    print()

    # Estatisticas das comunidades
    stats = comm.community_statistics(communities)
    print("Estatisticas das comunidades:")
    for comm_id, stat in stats.items():
        print(f"\n  Comunidade {comm_id}:")
        print(f"    Tamanho: {stat['size']}")
        print(f"    Arestas internas: {stat['internal_edges']}")
        print(f"    Arestas externas: {stat['external_edges']}")
        print(f"    Membros: {stat['members']}")


def test_manual_communities():
    """
    Testa modularidade com divisao manual conhecida
    """
    print("\n" + "="*60)
    print("TESTE: Comunidades Definidas Manualmente")
    print("="*60)
    print()

    # Mesmo grafo do teste anterior
    graph = AdjacencyListGraph(6)

    # Comunidade 1 (triangulo completo)
    graph.add_edge(0, 1)
    graph.add_edge(1, 0)
    graph.add_edge(1, 2)
    graph.add_edge(2, 1)
    graph.add_edge(0, 2)
    graph.add_edge(2, 0)

    # Comunidade 2 (triangulo completo)
    graph.add_edge(3, 4)
    graph.add_edge(4, 3)
    graph.add_edge(4, 5)
    graph.add_edge(5, 4)
    graph.add_edge(3, 5)
    graph.add_edge(5, 3)

    # Ponte
    graph.add_edge(2, 3)

    comm = CommunityMetrics(graph)

    # Define divisao manual PERFEITA
    manual_communities = {
        0: 0, 1: 0, 2: 0,  # Comunidade 0
        3: 1, 4: 1, 5: 1   # Comunidade 1
    }

    print("Divisao manual (perfeita):")
    for v, c in manual_communities.items():
        print(f"  Vertice {v}: Comunidade {c}")

    modularity = comm.modularity(manual_communities)
    print(f"\nModularidade: {modularity:.4f}")
    print(f"  Esperado: POSITIVO e ALTO (divisao perfeita)")

    # Testa divisao RUIM (todos na mesma comunidade)
    print("\n" + "-"*60)
    bad_communities = {v: 0 for v in range(6)}
    print("Divisao ruim (todos na mesma comunidade):")

    modularity_bad = comm.modularity(bad_communities)
    print(f"Modularidade: {modularity_bad:.4f}")
    print(f"  Esperado: Proximo de 0 (sem divisao)")


if __name__ == "__main__":
    test_strong_communities()
    test_manual_communities()
