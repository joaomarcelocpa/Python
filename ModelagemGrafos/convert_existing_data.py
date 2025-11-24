"""
Script para converter dados existentes para o formato esperado pelo GraphBuilder
"""
import json
import os
from pathlib import Path
import config

def find_latest_graph_files():
    """Encontra os arquivos de dados mais recentes"""
    graphs_dir = config.GRAPHS_DIR

    # Procura arquivos de dados
    files = {
        'graph_1_comments': None,
        'graph_2_closures': None,
        'graph_3_reviews': None,
        'graph_integrated': None
    }

    for graph_name in files.keys():
        pattern = f"{graph_name}_data_*.json"
        matching_files = list(graphs_dir.glob(pattern))

        if matching_files:
            # Pega o mais recente
            files[graph_name] = max(matching_files, key=lambda p: p.stat().st_mtime)

    return files

def convert_to_consolidated_format(files):
    """Converte os arquivos individuais para o formato consolidado"""
    consolidated_data = {}

    for graph_name, file_path in files.items():
        if file_path is None or not file_path.exists():
            print(f"[AVISO] Arquivo não encontrado para {graph_name}")
            continue

        print(f"Lendo {file_path.name}...")

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Converte edges de source/target para from/to
        edges_converted = []
        for edge in data.get('edges', []):
            edge_converted = edge.copy()
            if 'source' in edge_converted:
                edge_converted['from'] = edge_converted.pop('source')
            if 'target' in edge_converted:
                edge_converted['to'] = edge_converted.pop('target')
            edges_converted.append(edge_converted)

        consolidated_data[graph_name] = {
            "nodes": data.get('nodes', []),
            "edges": edges_converted
        }

    return consolidated_data

def main():
    print("="*70)
    print(" Convertendo dados existentes para formato consolidado")
    print("="*70)

    # Encontra arquivos mais recentes
    files = find_latest_graph_files()

    # Verifica se encontrou algum arquivo
    if not any(files.values()):
        print("\n[ERRO] Nenhum arquivo de dados encontrado em:")
        print(f"       {config.GRAPHS_DIR}")
        print("\nVocê precisa executar a extração de dados primeiro (opção 1).")
        return 1

    # Converte para formato consolidado
    consolidated_data = convert_to_consolidated_format(files)

    # Salva arquivo consolidado
    output_file = config.OUTPUT_DIR / "graph_data.json"

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(consolidated_data, f, indent=2, ensure_ascii=False)

    print(f"\n[OK] Arquivo consolidado criado com sucesso!")
    print(f"     {output_file}")
    print(f"\nAgora você pode executar a opção 2 para gerar os grafos.")

    return 0

if __name__ == "__main__":
    exit(main())
