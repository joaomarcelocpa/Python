"""
Extrator de dados para construo manual de grafos
Este mdulo identifica e salva ns (usurios) e arestas (interaes)
sem construir os grafos usando bibliotecas.
"""
import json
from datetime import datetime
from typing import Dict, List
from collections import defaultdict
import pandas as pd
import config


class GraphDataExtractor:
    """
    Extrator de dados de grafos - identifica ns e arestas
    sem construir os grafos
    """

    def __init__(self, raw_data: Dict):
        """
        Inicializa o extrator

        Args:
            raw_data: Dados raw coletados da API do GitHub
        """
        self.raw_data = raw_data

        self.graph_data = {
            "graph_1_comments": {"nodes": set(), "edges": []},
            "graph_2_closures": {"nodes": set(), "edges": []},
            "graph_3_reviews": {"nodes": set(), "edges": []},
            "graph_integrated": {"nodes": set(), "edges": []}
        }

        self.statistics = {}

    def extract_graph_1_comments(self):
        """
        Extrai dados para Grafo 1: Comentrios em issues ou pull requests

        Modelagem:
        - N: cada usurio
        - Aresta direcionada: autor do comentrio -> autor da issue/PR
        - Peso: nmero de comentrios
        """
        print(f"\n{'='*70}")
        print(f" Extraindo dados do Grafo 1: Comentrios")
        print(f"{'='*70}")

        edges_dict = defaultdict(int)

        for comment in self.raw_data.get("issue_comments", []):
            if not comment.get("user") or not comment.get("issue_user"):
                continue

            commenter = comment["user"].get("login", "unknown")
            issue_author = comment.get("issue_user", "unknown")

            # Adiciona ns
            self.graph_data["graph_1_comments"]["nodes"].add(commenter)
            self.graph_data["graph_1_comments"]["nodes"].add(issue_author)

            # Ignora autocomentrios
            if commenter != issue_author:
                key = (commenter, issue_author)
                edges_dict[key] += 1

        # Comentrios em pull requests
        for comment in self.raw_data.get("pr_comments", []):
            if not comment.get("user") or not comment.get("pr_user"):
                continue

            commenter = comment["user"].get("login", "unknown")
            pr_author = comment.get("pr_user", "unknown")

            # Adiciona ns
            self.graph_data["graph_1_comments"]["nodes"].add(commenter)
            self.graph_data["graph_1_comments"]["nodes"].add(pr_author)

            if commenter != pr_author:
                key = (commenter, pr_author)
                edges_dict[key] += 1

        # Converte para lista de arestas
        for (source, target), weight in edges_dict.items():
            self.graph_data["graph_1_comments"]["edges"].append({
                "source": source,
                "target": target,
                "weight": weight,
                "type": "comment"
            })

        # Estatsticas
        self.statistics["graph_1_comments"] = {
            "total_nodes": len(self.graph_data["graph_1_comments"]["nodes"]),
            "total_edges": len(self.graph_data["graph_1_comments"]["edges"]),
            "total_interactions": sum(e["weight"] for e in self.graph_data["graph_1_comments"]["edges"])
        }

        print(f" Ns identificados: {self.statistics['graph_1_comments']['total_nodes']:,}")
        print(f" Arestas identificadas: {self.statistics['graph_1_comments']['total_edges']:,}")
        print(f" Total de interaes: {self.statistics['graph_1_comments']['total_interactions']:,}")

    def extract_graph_2_closures(self):
        """
        Extrai dados para Grafo 2: Fechamento de issues por outro usurio

        Modelagem:
        - N: cada usurio
        - Aresta direcionada: quem fechou -> autor da issue
        - Peso: nmero de fechamentos
        """
        print(f"\n{'='*70}")
        print(f" Extraindo dados do Grafo 2: Fechamentos de Issues")
        print(f"{'='*70}")

        edges_dict = defaultdict(int)

        for issue in self.raw_data.get("issues", []):
            if issue.get("state") == "closed" and issue.get("closed_by") and issue.get("user"):
                closer = issue["closed_by"].get("login", "unknown")
                author = issue["user"].get("login", "unknown")

                # Adiciona ns
                self.graph_data["graph_2_closures"]["nodes"].add(closer)
                self.graph_data["graph_2_closures"]["nodes"].add(author)

                # Apenas se foi fechado por outro usurio
                if closer != author:
                    key = (closer, author)
                    edges_dict[key] += 1

        # Converte para lista de arestas
        for (source, target), weight in edges_dict.items():
            self.graph_data["graph_2_closures"]["edges"].append({
                "source": source,
                "target": target,
                "weight": weight,
                "type": "closure"
            })

        # Estatsticas
        self.statistics["graph_2_closures"] = {
            "total_nodes": len(self.graph_data["graph_2_closures"]["nodes"]),
            "total_edges": len(self.graph_data["graph_2_closures"]["edges"]),
            "total_interactions": sum(e["weight"] for e in self.graph_data["graph_2_closures"]["edges"])
        }

        print(f" Ns identificados: {self.statistics['graph_2_closures']['total_nodes']:,}")
        print(f" Arestas identificadas: {self.statistics['graph_2_closures']['total_edges']:,}")
        print(f" Total de interaes: {self.statistics['graph_2_closures']['total_interactions']:,}")

    def extract_graph_3_reviews(self):
        """
        Extrai dados para Grafo 3: Reviews, aprovaes e merges de pull requests

        Modelagem:
        - N: cada usurio
        - Aresta direcionada: reviewer/merger -> autor do PR
        - Peso: nmero de reviews/merges
        """
        print(f"\n{'='*70}")
        print(f" Extraindo dados do Grafo 3: Reviews e Merges")
        print(f"{'='*70}")

        edges_dict = defaultdict(lambda: {"weight": 0, "has_review": False, "has_merge": False})

        # Reviews
        for review in self.raw_data.get("pr_reviews", []):
            if not review.get("user") or not review.get("pr_user"):
                continue

            reviewer = review["user"].get("login", "unknown")
            pr_author = review.get("pr_user", "unknown")

            # Adiciona ns
            self.graph_data["graph_3_reviews"]["nodes"].add(reviewer)
            self.graph_data["graph_3_reviews"]["nodes"].add(pr_author)

            if reviewer != pr_author:
                key = (reviewer, pr_author)
                edges_dict[key]["weight"] += 1
                edges_dict[key]["has_review"] = True

        # Merges
        for pr in self.raw_data.get("pull_requests", []):
            if pr.get("merged_at") and pr.get("merged_by") and pr.get("user"):
                merger = pr["merged_by"].get("login", "unknown")
                pr_author = pr["user"].get("login", "unknown")

                # Adiciona ns
                self.graph_data["graph_3_reviews"]["nodes"].add(merger)
                self.graph_data["graph_3_reviews"]["nodes"].add(pr_author)

                if merger != pr_author:
                    key = (merger, pr_author)
                    edges_dict[key]["weight"] += 1
                    edges_dict[key]["has_merge"] = True

        # Converte para lista de arestas
        for (source, target), data in edges_dict.items():
            self.graph_data["graph_3_reviews"]["edges"].append({
                "source": source,
                "target": target,
                "weight": data["weight"],
                "type": "review_merge",
                "has_review": data["has_review"],
                "has_merge": data["has_merge"]
            })

        # Estatsticas
        self.statistics["graph_3_reviews"] = {
            "total_nodes": len(self.graph_data["graph_3_reviews"]["nodes"]),
            "total_edges": len(self.graph_data["graph_3_reviews"]["edges"]),
            "total_interactions": sum(e["weight"] for e in self.graph_data["graph_3_reviews"]["edges"])
        }

        print(f" Ns identificados: {self.statistics['graph_3_reviews']['total_nodes']:,}")
        print(f" Arestas identificadas: {self.statistics['graph_3_reviews']['total_edges']:,}")
        print(f" Total de interaes: {self.statistics['graph_3_reviews']['total_interactions']:,}")

    def extract_integrated_graph(self, weights: Dict[str, int] = None):
        """
        Extrai dados para o Grafo Integrado com pesos

        Pesos padro (conforme especificao):
        - Comentrio em issue ou pull request: peso 2
        - Abertura de issue comentada por outro usurio: peso 3
        - Reviso/aprovao de pull request: peso 4
        - Merge de pull request: peso 5

        Args:
            weights: Dicionrio personalizado de pesos (opcional)
        """
        if weights is None:
            weights = config.INTERACTION_WEIGHTS

        print(f"\n{'='*70}")
        print(f" Extraindo dados do Grafo Integrado")
        print(f"{'='*70}")
        print(f"Pesos utilizados:")
        for interaction, weight in weights.items():
            print(f"   {interaction}: {weight}")

        # Dicionrio para acumular pesos e tipos de interao
        edges_dict = defaultdict(lambda: {
            "weight": 0,
            "interactions": []
        })

        # 1. Comentrios em issues (peso padro: 2)
        for comment in self.raw_data.get("issue_comments", []):
            # Proteo contra dados ausentes
            if not comment.get("user") or not comment.get("issue_user"):
                continue

            commenter = comment["user"].get("login", "unknown")
            issue_author = comment.get("issue_user", "unknown")

            self.graph_data["graph_integrated"]["nodes"].add(commenter)
            self.graph_data["graph_integrated"]["nodes"].add(issue_author)

            if commenter != issue_author:
                key = (commenter, issue_author)
                edges_dict[key]["weight"] += weights["comment"]
                edges_dict[key]["interactions"].append({
                    "type": "issue_comment",
                    "weight": weights["comment"]
                })

        # 2. Comentrios em PRs (peso padro: 2)
        for comment in self.raw_data.get("pr_comments", []):
            # Proteo contra dados ausentes
            if not comment.get("user") or not comment.get("pr_user"):
                continue

            commenter = comment["user"].get("login", "unknown")
            pr_author = comment.get("pr_user", "unknown")

            self.graph_data["graph_integrated"]["nodes"].add(commenter)
            self.graph_data["graph_integrated"]["nodes"].add(pr_author)

            if commenter != pr_author:
                key = (commenter, pr_author)
                edges_dict[key]["weight"] += weights["comment"]
                edges_dict[key]["interactions"].append({
                    "type": "pr_comment",
                    "weight": weights["comment"]
                })

        # 3. Issues abertas que receberam comentrios (peso padro: 3)
        # Aresta: autor da issue -> comentarista
        issues_with_comments = {}
        for comment in self.raw_data.get("issue_comments", []):
            # Proteo contra dados ausentes
            if not comment.get("user") or not comment.get("issue_user") or not comment.get("issue_number"):
                continue

            issue_number = comment["issue_number"]
            if issue_number not in issues_with_comments:
                issues_with_comments[issue_number] = {
                    "author": comment.get("issue_user", "unknown"),
                    "commenters": set()
                }
            issues_with_comments[issue_number]["commenters"].add(comment["user"].get("login", "unknown"))

        for issue_info in issues_with_comments.values():
            author = issue_info["author"]
            for commenter in issue_info["commenters"]:
                if commenter != author:
                    key = (author, commenter)
                    edges_dict[key]["weight"] += weights["issue_opened"]
                    edges_dict[key]["interactions"].append({
                        "type": "issue_opened_commented",
                        "weight": weights["issue_opened"]
                    })

        # 4. Reviews (peso padro: 4)
        for review in self.raw_data.get("pr_reviews", []):
            # Proteo contra dados ausentes
            if not review.get("user") or not review.get("pr_user"):
                continue

            reviewer = review["user"].get("login", "unknown")
            pr_author = review.get("pr_user", "unknown")

            self.graph_data["graph_integrated"]["nodes"].add(reviewer)
            self.graph_data["graph_integrated"]["nodes"].add(pr_author)

            if reviewer != pr_author:
                key = (reviewer, pr_author)
                edges_dict[key]["weight"] += weights["review"]
                edges_dict[key]["interactions"].append({
                    "type": "review",
                    "weight": weights["review"]
                })

        # 5. Merges (peso padro: 5)
        for pr in self.raw_data.get("pull_requests", []):
            if pr.get("merged_at") and pr.get("merged_by") and pr.get("user"):
                merger = pr["merged_by"].get("login", "unknown")
                pr_author = pr["user"].get("login", "unknown")

                self.graph_data["graph_integrated"]["nodes"].add(merger)
                self.graph_data["graph_integrated"]["nodes"].add(pr_author)

                if merger != pr_author:
                    key = (merger, pr_author)
                    edges_dict[key]["weight"] += weights["merge"]
                    edges_dict[key]["interactions"].append({
                        "type": "merge",
                        "weight": weights["merge"]
                    })

        # Converte para lista de arestas
        for (source, target), data in edges_dict.items():
            # Conta tipos unicos de interação
            interaction_types = list(set(i["type"] for i in data["interactions"]))

            self.graph_data["graph_integrated"]["edges"].append({
                "source": source,
                "target": target,
                "weight": data["weight"],
                "interaction_types": interaction_types,
                "interaction_count": len(data["interactions"]),
                "interactions": data["interactions"]
            })

        # Estatsticas
        total_weight = sum(e["weight"] for e in self.graph_data["graph_integrated"]["edges"])
        total_edges = len(self.graph_data["graph_integrated"]["edges"])

        self.statistics["graph_integrated"] = {
            "total_nodes": len(self.graph_data["graph_integrated"]["nodes"]),
            "total_edges": total_edges,
            "total_weight": total_weight,
            "average_weight": total_weight / total_edges if total_edges > 0 else 0
        }

        print(f"\n Ns identificados: {self.statistics['graph_integrated']['total_nodes']:,}")
        print(f" Arestas identificadas: {self.statistics['graph_integrated']['total_edges']:,}")
        print(f" Peso total: {self.statistics['graph_integrated']['total_weight']:,}")
        print(f" Peso mdio por aresta: {self.statistics['graph_integrated']['average_weight']:.2f}")

    def extract_all(self):
        """Extrai dados de todos os grafos"""
        print(f"\n{'#'*70}")
        print(f"#  EXTRAINDO DADOS DOS GRAFOS")
        print(f"# (No construindo os grafos, apenas identificando ns e arestas)")
        print(f"{'#'*70}")

        self.extract_graph_1_comments()
        self.extract_graph_2_closures()
        self.extract_graph_3_reviews()
        self.extract_integrated_graph()

        print(f"\n{'='*70}")
        print(f" EXTRAO DE DADOS CONCLUDA")
        print(f"{'='*70}")

    def save_graph_data(self, output_dir: str = None):
        """
        Salva os dados extrados em mltiplos formatos

        Args:
            output_dir: Diretrio de sada (usa config.GRAPHS_DIR se None)
        """
        if output_dir is None:
            output_dir = config.GRAPHS_DIR

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        print(f"\n{'='*70}")
        print(f" Salvando dados dos grafos")
        print(f"{'='*70}")

        # Prepara dados consolidados para o GraphBuilder
        consolidated_data = {}

        for graph_name, data in self.graph_data.items():
            # Converte set de ns para lista
            nodes_list = sorted(list(data["nodes"]))

            # Prepara dados para salvar (formato individual com timestamp)
            graph_data_to_save = {
                "metadata": {
                    "graph_name": graph_name,
                    "description": self._get_graph_description(graph_name),
                    "extraction_date": datetime.now().isoformat(),
                    "total_nodes": len(nodes_list),
                    "total_edges": len(data["edges"])
                },
                "nodes": [{"id": node, "label": node} for node in nodes_list],
                "edges": data["edges"],
                "statistics": self.statistics.get(graph_name, {})
            }

            # Salva em JSON
            json_file = output_dir / f"{graph_name}_data_{timestamp}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(graph_data_to_save, f, indent=2, ensure_ascii=False)
            print(f" {json_file.name}")

            # Salva arestas em CSV (mais fcil de manipular)
            if data["edges"]:
                edges_df = pd.DataFrame(data["edges"])
                csv_file = output_dir / f"{graph_name}_edges_{timestamp}.csv"
                edges_df.to_csv(csv_file, index=False, encoding='utf-8')
                print(f" {csv_file.name}")

            # Salva ns em CSV
            nodes_df = pd.DataFrame([{"node_id": node} for node in nodes_list])
            nodes_csv = output_dir / f"{graph_name}_nodes_{timestamp}.csv"
            nodes_df.to_csv(nodes_csv, index=False, encoding='utf-8')
            print(f" {nodes_csv.name}")

            # Prepara dados consolidados (converte source/target para from/to)
            edges_converted = []
            for edge in data["edges"]:
                edge_converted = edge.copy()
                edge_converted['from'] = edge_converted.pop('source')
                edge_converted['to'] = edge_converted.pop('target')
                edges_converted.append(edge_converted)

            consolidated_data[graph_name] = {
                "nodes": [{"id": node, "label": node} for node in nodes_list],
                "edges": edges_converted
            }

        # Salva estatsticas gerais
        stats_file = output_dir / f"extraction_statistics_{timestamp}.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.statistics, f, indent=2, ensure_ascii=False)
        print(f" {stats_file.name}")

        # Cria README explicativo
        readme_file = output_dir / f"README_{timestamp}.txt"
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(self._generate_readme())
        print(f" {readme_file.name}")

        print(f"\n Dados salvos em: {output_dir}")

        # Salva arquivo consolidado para o GraphBuilder (no OUTPUT_DIR)
        graph_data_file = config.OUTPUT_DIR / "graph_data.json"
        with open(graph_data_file, 'w', encoding='utf-8') as f:
            json.dump(consolidated_data, f, indent=2, ensure_ascii=False)
        print(f"\n[OK] Arquivo consolidado para construo de grafos salvo em:")
        print(f"     {graph_data_file}")

    def _get_graph_description(self, graph_name: str) -> str:
        """Retorna descrio do grafo"""
        descriptions = {
            "graph_1_comments": "Comentrios em issues ou pull requests",
            "graph_2_closures": "Fechamento de issues por outro usurio",
            "graph_3_reviews": "Reviews, aprovaes e merges de pull requests",
            "graph_integrated": "Grafo integrado com combinao ponderada de todas as interaes"
        }
        return descriptions.get(graph_name, "")

    def _generate_readme(self) -> str:
        """Gera README explicativo dos dados"""
        readme = """
================================================================================
DADOS EXTRADOS PARA CONSTRUO MANUAL DE GRAFOS
================================================================================

Este diretrio contm os dados extrados do repositrio GitHub para construo
manual de grafos de colaborao.

ESTRUTURA DOS DADOS:
-------------------

Para cada grafo, foram gerados 3 arquivos:

1. *_data_*.json
   - Arquivo completo com metadados, ns e arestas
   - Formato estruturado para anlise programtica

2. *_edges_*.csv
   - Lista de arestas (interaes) em formato CSV
   - Colunas: source, target, weight, type, etc.
   - Fcil de importar em planilhas ou programas

3. *_nodes_*.csv
   - Lista de ns (usurios) em formato CSV
   - Coluna: node_id

GRAFOS EXTRADOS:
----------------

1. GRAFO 1 - COMENTRIOS (graph_1_comments)
   Ns: Usurios
   Arestas: autor_comentrio -> autor_issue/PR
   Peso: Nmero de comentrios

2. GRAFO 2 - FECHAMENTOS (graph_2_closures)
   Ns: Usurios
   Arestas: quem_fechou -> autor_issue
   Peso: Nmero de fechamentos

3. GRAFO 3 - REVIEWS E MERGES (graph_3_reviews)
   Ns: Usurios
   Arestas: reviewer/merger -> autor_PR
   Peso: Nmero de reviews/merges

4. GRAFO INTEGRADO (graph_integrated)
   Ns: Usurios
   Arestas: Todas as interaes combinadas com pesos
   Pesos:
     - Comentrio: 2
     - Issue aberta comentada: 3
     - Review: 4
     - Merge: 5

MODELAGEM:
---------

- Os grafos são DIRECIONADOS
- Para relaes bidirecionais, use arestas anti-paralelas
- Os grafos são SIMPLES (sem multi-arestas, pesos acumulados)
- Autoloops foram removidos (usuário interage consigo mesmo)

COMO USAR:
---------

1. Para construir o grafo manualmente:
   - Leia o arquivo *_nodes_*.csv para criar os ns
   - Leia o arquivo *_edges_*.csv para criar as arestas
   - Use o campo 'weight' para o peso das arestas

2. Para anlise em planilhas:
   - Abra os arquivos CSV no Excel/LibreOffice
   - Use os pesos para anlises

3. Para programao:
   - Use os arquivos JSON para acesso programtico
   - Os dados esto completamente estruturados

ESTATSTICAS:
------------

Veja o arquivo extraction_statistics_*.json para estatísticas detalhadas
sobre cada grafo (nmero de ns, arestas, pesos totais, etc.)

================================================================================
"""
        return readme

    def print_summary(self):
        """Imprime resumo dos dados extrados"""
        print(f"\n{'='*70}")
        print(f" RESUMO DOS DADOS EXTRADOS")
        print(f"{'='*70}")

        for graph_name, stats in self.statistics.items():
            display_name = graph_name.replace("graph_", "").replace("_", " ").title()
            print(f"\n{display_name}:")
            for key, value in stats.items():
                if isinstance(value, float):
                    print(f"   {key}: {value:.2f}")
                else:
                    print(f"   {key}: {value:,}")
