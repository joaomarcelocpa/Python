"""
Script para análise de métricas de grafos extraídos do GitHub

Uso:
    python analyze_github_metrics.py <arquivo_gexf> [--output <diretorio>]

Exemplo:
    python analyze_github_metrics.py output/gephi/grafo1.gexf
    python analyze_github_metrics.py output/gephi/grafo1.gexf --output results/
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime

# Adiciona diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from src.graph.adjacency_list_graph import AdjacencyListGraph
from src.utils.graph_metrics_analyzer import GraphMetricsAnalyzer


def load_graph_from_gexf(filepath: str) -> AdjacencyListGraph:
    """
    Carrega grafo de arquivo GEXF.

    Args:
        filepath: Caminho do arquivo GEXF

    Returns:
        Grafo carregado
    """
    from src.gexf_reader import GEXFReader

    print(f"\nCarregando grafo de: {filepath}")

    reader = GEXFReader(filepath)
    graph = reader.to_graph()

    print(f"[OK] Grafo carregado: {graph.num_vertices} vertices, {graph.num_edges} arestas")

    return graph


def analyze_and_report(graph: AdjacencyListGraph, output_dir: str = "output"):
    """
    Executa análise completa e gera relatórios.

    Args:
        graph: Grafo a ser analisado
        output_dir: Diretório de saída
    """
    # Cria diretório de saída
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Cria analisador
    print("\nIniciando analise de metricas...")
    analyzer = GraphMetricsAnalyzer(graph)

    # Executa análise completa
    results = analyzer.analyze_all()

    # Gera timestamp para arquivos
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 1. Salva JSON completo
    json_file = output_path / f"metrics_{timestamp}.json"
    analyzer.export_to_json(str(json_file), results)
    print(f"[OK] Resultados completos salvos em: {json_file}")

    # 2. Gera relatório textual
    report = analyzer.generate_report(results)
    report_file = output_path / f"report_{timestamp}.txt"

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"[OK] Relatorio textual salvo em: {report_file}")
    print("\n" + "=" * 80)
    print(report)

    # 3. Gera análises específicas
    print("\n" + "=" * 80)
    print("ANALISES DETALHADAS")
    print("=" * 80)

    # 3.1. Top colaboradores por diferentes métricas
    print("\n1. TOP COLABORADORES POR DIFERENTES METRICAS")
    print("-" * 80)

    metrics_to_analyze = [
        ('pagerank', 'PageRank (Influencia)'),
        ('betweenness', 'Betweenness (Pontes)'),
        ('degree_total', 'Degree (Atividade)'),
        ('closeness', 'Closeness (Proximidade)')
    ]

    top_file = output_path / f"top_collaborators_{timestamp}.txt"
    with open(top_file, 'w', encoding='utf-8') as f:
        f.write("TOP COLABORADORES POR METRICA\n")
        f.write("=" * 80 + "\n\n")

        for metric, metric_name in metrics_to_analyze:
            print(f"\n{metric_name}:")
            f.write(f"\n{metric_name}:\n")
            f.write("-" * 80 + "\n")

            top = analyzer.get_top_central_nodes(metric, 10)
            for i, (vertex, score, label) in enumerate(top, 1):
                line = f"  {i:2d}. {label:30s} {score:8.4f}"
                print(line)
                f.write(line + "\n")

    print(f"\n[OK] Top colaboradores salvos em: {top_file}")

    # 3.2. Análise de comunidades
    print("\n2. ANALISE DE COMUNIDADES")
    print("-" * 80)

    communities = results['community']['communities']
    comm_stats = results['community']['community_statistics']

    comm_file = output_path / f"communities_{timestamp}.txt"
    with open(comm_file, 'w', encoding='utf-8') as f:
        f.write("ANALISE DE COMUNIDADES\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Numero de comunidades detectadas: {results['community']['num_communities']}\n")
        f.write(f"Modularidade: {results['community']['modularity']:.4f}\n")
        f.write(f"Metodo: {results['community']['method']}\n\n")

        print(f"  Numero de comunidades: {results['community']['num_communities']}")
        print(f"  Modularidade: {results['community']['modularity']:.4f}")

        # Detalhes de cada comunidade
        for comm_id in sorted(comm_stats.keys()):
            stats = comm_stats[comm_id]
            members = analyzer.get_community_members(comm_id)

            f.write(f"\nComunidade {comm_id}:\n")
            f.write("-" * 80 + "\n")
            f.write(f"  Tamanho: {stats['size']} membros\n")
            f.write(f"  Arestas internas: {stats['internal_edges']}\n")
            f.write(f"  Arestas externas: {stats['external_edges']}\n")
            f.write(f"  Densidade interna: {stats['internal_edges'] / (stats['size'] * (stats['size'] - 1)) if stats['size'] > 1 else 0:.4f}\n")
            f.write(f"\n  Membros:\n")

            for vertex, label in sorted(members, key=lambda x: x[1]):
                f.write(f"    - {label}\n")

    print(f"[OK] Analise de comunidades salva em: {comm_file}")

    # 3.3. Bridging ties (conectores entre comunidades)
    print("\n3. BRIDGING TIES (Conectores entre Comunidades)")
    print("-" * 80)

    bridging_file = output_path / f"bridging_ties_{timestamp}.txt"
    with open(bridging_file, 'w', encoding='utf-8') as f:
        f.write("BRIDGING TIES - Conectores entre Comunidades\n")
        f.write("=" * 80 + "\n\n")
        f.write("Colaboradores que atuam como pontes entre diferentes grupos:\n\n")

        bridging = results['community']['bridging_ties']
        sorted_bridging = sorted(bridging.items(), key=lambda x: x[1], reverse=True)

        for i, (vertex, score) in enumerate(sorted_bridging[:20], 1):
            label = graph.get_vertex_label(vertex) or f"V{vertex}"
            comm = communities.get(vertex, -1)

            line = f"  {i:2d}. {label:30s} Score: {score:.4f} (Comunidade {comm})"
            print(line)
            f.write(line + "\n")

    print(f"[OK] Bridging ties salvos em: {bridging_file}")

    # 4. Resumo executivo
    print("\n4. GERANDO RESUMO EXECUTIVO")
    print("-" * 80)

    summary_file = output_path / f"executive_summary_{timestamp}.txt"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("RESUMO EXECUTIVO - ANALISE DE REDE DE COLABORACAO\n")
        f.write("=" * 80 + "\n\n")

        # Informações básicas
        f.write("1. VISAO GERAL DA REDE\n")
        f.write("-" * 80 + "\n")
        f.write(f"  Colaboradores: {graph.num_vertices}\n")
        f.write(f"  Interacoes: {graph.num_edges}\n")
        f.write(f"  Densidade: {results['structure']['density']:.4f}\n")
        f.write(f"  Reciprocidade: {results['structure']['reciprocity']:.4f}\n\n")

        # Estrutura
        f.write("2. ESTRUTURA DA REDE\n")
        f.write("-" * 80 + "\n")
        f.write(f"  Coeficiente de Aglomeracao: {results['structure']['clustering_average']:.4f}\n")
        f.write(f"  Assortatividade: {results['structure']['assortativity']:.4f}\n")
        f.write(f"  Caminho Medio: {results['structure']['average_path_length']:.2f}\n")
        f.write(f"  Diametro: {results['structure']['diameter']}\n\n")

        # Interpretação
        f.write("3. INTERPRETACAO\n")
        f.write("-" * 80 + "\n")

        density = results['structure']['density']
        if density > 0.5:
            f.write("  - Rede MUITO COLABORATIVA (densidade alta)\n")
        elif density > 0.3:
            f.write("  - Rede COLABORATIVA (densidade moderada)\n")
        else:
            f.write("  - Rede POUCO CONECTADA (densidade baixa)\n")

        clustering = results['structure']['clustering_average']
        if clustering > 0.6:
            f.write("  - FORTE formacao de grupos coesos\n")
        elif clustering > 0.4:
            f.write("  - MODERADA formacao de grupos\n")
        else:
            f.write("  - FRACA formacao de grupos\n")

        assortativity = results['structure']['assortativity']
        if assortativity > 0.1:
            f.write("  - Rede CENTRALIZADA (hubs conectados entre si)\n")
        elif assortativity < -0.1:
            f.write("  - Rede DESCENTRALIZADA (hubs conectam perifericos)\n")
        else:
            f.write("  - Rede com estrutura EQUILIBRADA\n")

        f.write(f"\n  - {results['community']['num_communities']} comunidades detectadas\n")

        modularity = results['community']['modularity']
        if modularity > 0.4:
            f.write("  - Comunidades MUITO BEM DEFINIDAS\n")
        elif modularity > 0.2:
            f.write("  - Comunidades MODERADAMENTE DEFINIDAS\n")
        else:
            f.write("  - Comunidades FRACAMENTE DEFINIDAS\n")

        # Top 3 colaboradores
        f.write("\n4. COLABORADORES CHAVE\n")
        f.write("-" * 80 + "\n")

        f.write("\n  Mais Influentes (PageRank):\n")
        for i, (v, score, label) in enumerate(analyzer.get_top_central_nodes('pagerank', 3), 1):
            f.write(f"    {i}. {label}: {score:.4f}\n")

        f.write("\n  Pontes entre Grupos (Betweenness):\n")
        for i, (v, score, label) in enumerate(analyzer.get_top_central_nodes('betweenness', 3), 1):
            f.write(f"    {i}. {label}: {score:.4f}\n")

        f.write("\n  Mais Ativos (Degree):\n")
        for i, (v, score, label) in enumerate(analyzer.get_top_central_nodes('degree_total', 3), 1):
            f.write(f"    {i}. {label}: {score:.4f}\n")

    print(f"[OK] Resumo executivo salvo em: {summary_file}")

    print("\n" + "=" * 80)
    print("[OK] ANALISE COMPLETA FINALIZADA!")
    print("=" * 80)
    print(f"\nArquivos gerados em: {output_path}")


def main():
    """Função principal."""
    parser = argparse.ArgumentParser(
        description='Analisa metricas de grafo extraido do GitHub',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python analyze_github_metrics.py output/gephi/grafo1.gexf
  python analyze_github_metrics.py output/gephi/grafo1.gexf --output results/
        """
    )

    parser.add_argument('gexf_file', help='Arquivo GEXF do grafo')
    parser.add_argument('--output', '-o', default='output/metrics',
                       help='Diretorio de saida (padrao: output/metrics)')

    args = parser.parse_args()

    # Verifica se arquivo existe
    if not Path(args.gexf_file).exists():
        print(f"[ERRO] Arquivo nao encontrado: {args.gexf_file}")
        return 1

    try:
        # Carrega grafo
        graph = load_graph_from_gexf(args.gexf_file)

        # Analisa e gera relatórios
        analyze_and_report(graph, args.output)

        return 0

    except Exception as e:
        print(f"\n[ERRO] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
