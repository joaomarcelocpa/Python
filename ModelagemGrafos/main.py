import sys
import os
import argparse
from datetime import datetime
import config
from src.github_api import GitHubAPIClient
from src.graph_data_extractor import GraphDataExtractor
from src.data_processor import DataProcessor
from src.graph_builder import GraphBuilder


def print_banner():
    banner = """
    ==================================================================

            GitHub Repository Graph Analyzer v2.0

        Analise de Interacoes e Colaboracao em Repositorios

    ==================================================================
    """
    print(banner)


def check_data_exists():
    """
    Verifica se os dados ja foram extraidos.

    Returns:
        tuple: (raw_data_exists, graph_data_exists)
    """
    raw_data_file = os.path.join(config.RAW_DATA_DIR, "raw_data.json")
    graph_data_file = os.path.join(config.OUTPUT_DIR, "graph_data.json")

    raw_exists = os.path.exists(raw_data_file)
    graph_exists = os.path.exists(graph_data_file)

    return raw_exists, graph_exists


def show_menu():
    """Mostra menu interativo e retorna opcao escolhida."""
    print("\n" + "="*70)
    print(" MENU PRINCIPAL")
    print("="*70)

    raw_exists, graph_exists = check_data_exists()

    print("\nStatus dos dados:")
    print(f"  Dados brutos (GitHub API): {'[OK] Encontrado' if raw_exists else '[X] Nao encontrado'}")
    print(f"  Dados dos grafos (nos/arestas): {'[OK] Encontrado' if graph_exists else '[X] Nao encontrado'}")

    print("\nOpcoes:")
    print("  1 - Extrair novos dados do GitHub")
    print("  2 - Usar dados existentes e gerar grafos" + (" (dados disponiveis)" if graph_exists else " (requer extracao primeiro)"))
    print("  3 - Apenas processar dados (sem gerar grafos)")
    print("  0 - Sair")

    print("\n" + "-"*70)
    choice = input("Escolha uma opcao: ").strip()
    return choice, raw_exists, graph_exists


def extract_github_data(owner, repo, token):
    """Extrai dados do GitHub."""
    print(f"\n{'#'*70}")
    print(f"# FASE 1: COLETA DE DADOS DA API DO GITHUB")
    print(f"{'#'*70}")

    client = GitHubAPIClient(owner, repo, token)
    client.fetch_all_data()

    if config.SAVE_RAW_DATA:
        client.save_raw_data()

    # Mostra resumo
    summary = client.get_summary()
    print(f"\n Resumo da coleta:")
    print(f"  * Estrelas: {summary['stars']:,}")
    print(f"   Issues: {summary['issues']:,}")
    print(f"   Pull Requests: {summary['pull_requests']:,}")
    print(f"   Comentarios em issues: {summary['issue_comments']:,}")
    print(f"   Comentarios em PRs: {summary['pr_comments']:,}")
    print(f"  [OK] Reviews: {summary['pr_reviews']:,}")

    return client.raw_data


def process_graph_data(raw_data):
    """Processa dados e extrai informacoes dos grafos."""
    print(f"\n{'#'*70}")
    print(f"# FASE 2: EXTRACAO DE DADOS DOS GRAFOS")
    print(f"{'#'*70}")

    extractor = GraphDataExtractor(raw_data)
    extractor.extract_all()
    extractor.print_summary()

    if config.SAVE_GRAPHS:
        extractor.save_graph_data()

    return extractor


def build_and_export_graphs(use_matrix=False):
    """Constroi e exporta os grafos em formato GEXF."""
    print(f"\n{'#'*70}")
    print(f"# FASE 3: CONSTRUCAO E EXPORTACAO DOS GRAFOS")
    print(f"{'#'*70}")

    print(f"\nImplementacao escolhida: {'Matriz de Adjacencia' if use_matrix else 'Lista de Adjacencia'}")

    try:
        # Cria builder e constroi grafos
        builder = GraphBuilder(config.OUTPUT_DIR)

        print(f"\nConstruindo grafos...")
        graphs = builder.build_all_graphs(use_matrix=use_matrix)

        print(f"\n[OK] {len(graphs)} grafos construidos")
        print(f"[OK] Total de usuarios: {builder.get_user_count()}")

        # Exporta para GEXF
        print(f"\nExportando grafos para formato GEXF (GEPHI)...")
        stats = builder.export_all_graphs(graphs)

        # Mostra estatisticas
        print(f"\n{'='*70}")
        print(f" ESTATISTICAS DOS GRAFOS")
        print(f"{'='*70}")

        for graph_name, graph_stats in stats.items():
            nome = graph_name.replace('graph_', 'Grafo ').replace('_', ' ').title()
            print(f"\n{nome}:")
            print(f"  Vertices: {graph_stats['vertices']:,}")
            print(f"  Arestas: {graph_stats['edges']:,}")
            print(f"  Densidade: {graph_stats['density']:.6f}")
            print(f"  Vazio: {'Sim' if graph_stats['is_empty'] else 'Nao'}")
            print(f"  Completo: {'Sim' if graph_stats['is_complete'] else 'Nao'}")
            print(f"  Arquivo: {os.path.basename(graph_stats['filename'])}")

        gephi_dir = os.path.join(config.OUTPUT_DIR, "gephi")
        print(f"\n[OK] Arquivos GEXF salvos em: {gephi_dir}")
        print(f"\nVoce pode abrir estes arquivos no GEPHI para visualizacao e analise.")

        return True

    except FileNotFoundError as e:
        print(f"\n[ERRO] {e}")
        print(f"\nVoce precisa extrair os dados primeiro (opcao 1 no menu).")
        return False
    except Exception as e:
        print(f"\n[ERRO] Erro ao construir grafos: {e}")
        import traceback
        traceback.print_exc()
        return False


def interactive_mode(args):
    """Modo interativo com menu."""
    while True:
        choice, raw_exists, graph_exists = show_menu()

        if choice == '0':
            print("\nEncerrando...")
            return 0

        elif choice == '1':
            # Extrair novos dados
            start_time = datetime.now()

            print(f"\n{'='*70}")
            print(f" Iniciando extracao de dados")
            print(f"{'='*70}")
            print(f" Repositorio: {args.owner}/{args.repo}")
            print(f" Token configurado: {'Sim' if args.token else 'Nao'}")
            print(f"{'='*70}\n")

            try:
                raw_data = extract_github_data(args.owner, args.repo, args.token)
                process_graph_data(raw_data)

                # Processar dados adicionais
                print(f"\n{'#'*70}")
                print(f"# FASE 3: PROCESSAMENTO E ANALISE DOS DADOS")
                print(f"{'#'*70}")

                processor = DataProcessor(raw_data)
                processor.process_all()
                processor.save_processed_data()

                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()

                print(f"\n{'='*70}")
                print(f"[OK] Extracao concluida com sucesso!")
                print(f"{'='*70}")
                print(f"Tempo total: {duration:.2f}s ({duration/60:.2f} minutos)")
                print(f"\nAgora voce pode gerar os grafos (opcao 2).")

            except Exception as e:
                print(f"\n[ERRO] {e}")
                import traceback
                traceback.print_exc()

            input("\nPressione Enter para continuar...")

        elif choice == '2':
            # Gerar grafos com dados existentes
            if not graph_exists:
                print("\n[ERRO] Dados nao encontrados!")
                print("Voce precisa extrair os dados primeiro (opcao 1).")
                input("\nPressione Enter para continuar...")
                continue

            print("\nEscolha a implementacao do grafo:")
            print("  1 - Lista de Adjacencia (recomendado para grafos esparsos)")
            print("  2 - Matriz de Adjacencia (melhor para grafos densos)")
            impl_choice = input("Opcao: ").strip()

            use_matrix = impl_choice == '2'

            build_and_export_graphs(use_matrix=use_matrix)
            input("\nPressione Enter para continuar...")

        elif choice == '3':
            # Apenas processar dados
            if not raw_exists:
                print("\n[ERRO] Dados brutos nao encontrados!")
                print("Voce precisa extrair os dados primeiro (opcao 1).")
                input("\nPressione Enter para continuar...")
                continue

            print("\nCarregando dados brutos...")
            # TODO: Implementar carregamento de dados salvos
            print("[INFO] Funcionalidade em desenvolvimento")
            input("\nPressione Enter para continuar...")

        else:
            print("\nOpcao invalida! Escolha 0, 1, 2 ou 3.")
            input("\nPressione Enter para continuar...")


def main():
    print_banner()

    parser = argparse.ArgumentParser(
        description='Analisa interacoes em repositorios GitHub atraves de grafos'
    )
    parser.add_argument(
        '--owner',
        type=str,
        default=config.REPO_OWNER,
        help=f'Proprietario do repositorio (padrao: {config.REPO_OWNER})'
    )
    parser.add_argument(
        '--repo',
        type=str,
        default=config.REPO_NAME,
        help=f'Nome do repositorio (padrao: {config.REPO_NAME})'
    )
    parser.add_argument(
        '--token',
        type=str,
        default=config.GITHUB_TOKEN,
        help='Token de acesso do GitHub (ou use variavel de ambiente GITHUB_TOKEN)'
    )
    parser.add_argument(
        '--non-interactive',
        action='store_true',
        help='Modo nao-interativo (extrai dados e gera grafos automaticamente)'
    )
    parser.add_argument(
        '--use-matrix',
        action='store_true',
        help='Usa matriz de adjacencia (padrao: lista de adjacencia)'
    )

    args = parser.parse_args()

    try:
        if args.non_interactive:
            # Modo automatico
            start_time = datetime.now()

            print(f"\n{'='*70}")
            print(f" Modo automatico")
            print(f"{'='*70}")
            print(f" Repositorio: {args.owner}/{args.repo}")
            print(f"{'='*70}\n")

            raw_data = extract_github_data(args.owner, args.repo, args.token)
            process_graph_data(raw_data)

            processor = DataProcessor(raw_data)
            processor.process_all()
            processor.save_processed_data()

            build_and_export_graphs(use_matrix=args.use_matrix)

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            print(f"\n{'='*70}")
            print(f"[OK] Processo completo!")
            print(f"{'='*70}")
            print(f"Tempo total: {duration:.2f}s ({duration/60:.2f} minutos)")

            return 0
        else:
            # Modo interativo
            return interactive_mode(args)

    except KeyboardInterrupt:
        print(f"\n\nProcesso interrompido pelo usuario")
        return 1

    except Exception as e:
        print(f"\n\n[ERRO] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
