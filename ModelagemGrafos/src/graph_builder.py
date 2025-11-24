"""
Construtor de grafos a partir dos dados extraidos do GitHub.

Este modulo le os arquivos CSV/JSON gerados pelo GraphDataExtractor
e constroi os 4 grafos especificados:
1. Grafo de comentarios (issues/PRs)
2. Grafo de fechamento de issues
3. Grafo de reviews/merges de PRs
4. Grafo integrado com pesos
"""

import os
import json
import pandas as pd
from typing import Dict, List, Tuple, Optional
from src.graph.adjacency_list_graph import AdjacencyListGraph
from src.graph.adjacency_matrix_graph import AdjacencyMatrixGraph
from src.graph.exporters.gephi_exporter import GephiExporter


class GraphBuilder:
    """
    Constroi grafos a partir dos dados extraidos do GitHub.

    Le arquivos CSV e JSON do diretorio de saida e cria os grafos
    modelando as interacoes entre usuarios.
    """

    def __init__(self, output_dir: str = "output"):
        """
        Inicializa o construtor de grafos.

        Args:
            output_dir: Diretorio onde estao os dados extraidos
        """
        self.output_dir = output_dir
        self.user_to_id: Dict[str, int] = {}
        self.id_to_user: Dict[int, str] = {}
        self.next_id = 0

    def _get_or_create_user_id(self, username: str) -> int:
        """
        Obtem ou cria ID numerico para um usuario.

        Args:
            username: Nome do usuario

        Returns:
            ID numerico do usuario
        """
        if username not in self.user_to_id:
            self.user_to_id[username] = self.next_id
            self.id_to_user[self.next_id] = username
            self.next_id += 1
        return self.user_to_id[username]

    def _build_graph_from_edges(
        self,
        graph_key: str,
        data: Dict,
        use_matrix: bool = False,
        has_weights: bool = False
    ):
        """
        Metodo privado para construir grafo a partir de arestas.
        Elimina duplicacao entre build_graph_X methods.

        Args:
            graph_key: Chave do grafo no dicionario de dados
            data: Dados carregados do JSON
            use_matrix: Se True, usa matriz; senao, usa lista
            has_weights: Se True, processa pesos das arestas

        Returns:
            Grafo construido
        """
        # Obtem arestas
        edges = data.get(graph_key, {}).get('edges', [])

        # Mapeia todos os usuarios
        for edge in edges:
            self._get_or_create_user_id(edge['from'])
            self._get_or_create_user_id(edge['to'])

        # Cria grafo
        GraphClass = AdjacencyMatrixGraph if use_matrix else AdjacencyListGraph
        graph = GraphClass(self.next_id)

        # Define labels dos vertices
        for user_id, username in self.id_to_user.items():
            graph.set_vertex_label(user_id, username)

        # Adiciona arestas
        for edge in edges:
            u = self.user_to_id[edge['from']]
            v = self.user_to_id[edge['to']]
            graph.add_edge(u, v)

            # Se tem pesos, define o peso da aresta
            if has_weights:
                weight = edge.get('weight', 1.0)
                graph.set_edge_weight(u, v, weight)

        return graph

    def load_graph_data(self) -> Dict:
        """
        Carrega os dados dos grafos dos arquivos JSON.

        Returns:
            Dicionario com os dados dos grafos

        Raises:
            FileNotFoundError: Se arquivos nao existirem
        """
        json_file = os.path.join(self.output_dir, "graph_data.json")

        if not os.path.exists(json_file):
            raise FileNotFoundError(
                f"Arquivo {json_file} nao encontrado. "
                "Execute a extracao de dados primeiro."
            )

        with open(json_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def build_graph_1_comments(
        self,
        data: Dict,
        use_matrix: bool = False
    ) -> AdjacencyListGraph:
        """
        Constroi Grafo 1: Comentarios em issues/PRs.

        Aresta: comentador -> autor da issue/PR

        Args:
            data: Dados carregados do JSON
            use_matrix: Se True, usa matriz; senao, usa lista

        Returns:
            Grafo de comentarios
        """
        return self._build_graph_from_edges('graph_1_comments', data, use_matrix, has_weights=False)

    def build_graph_2_closures(
        self,
        data: Dict,
        use_matrix: bool = False
    ) -> AdjacencyListGraph:
        """
        Constroi Grafo 2: Fechamento de issues.

        Aresta: usuario que fechou -> autor da issue

        Args:
            data: Dados carregados do JSON
            use_matrix: Se True, usa matriz; senao, usa lista

        Returns:
            Grafo de fechamentos
        """
        return self._build_graph_from_edges('graph_2_closures', data, use_matrix, has_weights=False)

    def build_graph_3_reviews(
        self,
        data: Dict,
        use_matrix: bool = False
    ) -> AdjacencyListGraph:
        """
        Constroi Grafo 3: Reviews e merges de PRs.

        Aresta: revisor/merger -> autor do PR

        Args:
            data: Dados carregados do JSON
            use_matrix: Se True, usa matriz; senao, usa lista

        Returns:
            Grafo de reviews
        """
        return self._build_graph_from_edges('graph_3_reviews', data, use_matrix, has_weights=False)

    def build_graph_4_integrated(
        self,
        data: Dict,
        use_matrix: bool = False
    ) -> AdjacencyListGraph:
        """
        Constroi Grafo 4: Grafo integrado com pesos.

        Pesos das interacoes (conforme especificacao):
        - Comentario em issue ou PR: peso 2
        - Abertura de issue comentada por outro usuario: peso 3
        - Revisao/aprovacao de pull request: peso 4
        - Merge de pull request: peso 5

        Args:
            data: Dados carregados do JSON
            use_matrix: Se True, usa matriz; senao, usa lista

        Returns:
            Grafo integrado com pesos
        """
        return self._build_graph_from_edges('graph_integrated', data, use_matrix, has_weights=True)

    def build_all_graphs(
        self,
        use_matrix: bool = False
    ) -> Dict[str, AdjacencyListGraph]:
        """
        Constroi todos os 4 grafos.

        Args:
            use_matrix: Se True, usa matriz; senao, usa lista

        Returns:
            Dicionario com os 4 grafos
        """
        # Carrega dados
        data = self.load_graph_data()

        # Constroi grafos
        graphs = {
            'graph_1_comments': self.build_graph_1_comments(data, use_matrix),
            'graph_2_closures': self.build_graph_2_closures(data, use_matrix),
            'graph_3_reviews': self.build_graph_3_reviews(data, use_matrix),
            'graph_4_integrated': self.build_graph_4_integrated(data, use_matrix)
        }

        return graphs

    def export_all_graphs(
        self,
        graphs: Dict[str, AdjacencyListGraph],
        output_dir: Optional[str] = None
    ) -> Dict[str, dict]:
        """
        Exporta todos os grafos para formato GEXF.

        Args:
            graphs: Dicionario com os grafos
            output_dir: Diretorio de saida (padrao: output/gephi)

        Returns:
            Dicionario com estatisticas de cada grafo
        """
        if output_dir is None:
            output_dir = os.path.join(self.output_dir, "gephi")

        # Cria diretorio se nao existir
        os.makedirs(output_dir, exist_ok=True)

        stats = {}

        # Grafo 1: Comentarios
        if 'graph_1_comments' in graphs:
            filename = os.path.join(output_dir, "graph_1_comments.gexf")
            s = GephiExporter.export_with_stats(
                graphs['graph_1_comments'],
                filename,
                "Grafo 1: Comentarios",
                "Interacoes atraves de comentarios em issues e pull requests"
            )
            stats['graph_1_comments'] = s

        # Grafo 2: Fechamentos
        if 'graph_2_closures' in graphs:
            filename = os.path.join(output_dir, "graph_2_closures.gexf")
            s = GephiExporter.export_with_stats(
                graphs['graph_2_closures'],
                filename,
                "Grafo 2: Fechamento de Issues",
                "Interacoes atraves de fechamento de issues"
            )
            stats['graph_2_closures'] = s

        # Grafo 3: Reviews
        if 'graph_3_reviews' in graphs:
            filename = os.path.join(output_dir, "graph_3_reviews.gexf")
            s = GephiExporter.export_with_stats(
                graphs['graph_3_reviews'],
                filename,
                "Grafo 3: Reviews e Merges",
                "Interacoes atraves de reviews e merges de pull requests"
            )
            stats['graph_3_reviews'] = s

        # Grafo 4: Integrado
        if 'graph_4_integrated' in graphs:
            filename = os.path.join(output_dir, "graph_4_integrated.gexf")
            s = GephiExporter.export_with_stats(
                graphs['graph_4_integrated'],
                filename,
                "Grafo 4: Integrado com Pesos",
                "Grafo integrado com todas as interacoes e pesos (Comentario=2, Issue=3, Review=4, Merge=5)"
            )
            stats['graph_4_integrated'] = s

        return stats

    def get_user_mapping(self) -> Dict[str, int]:
        """Retorna mapeamento usuario -> ID."""
        return self.user_to_id.copy()

    def get_user_count(self) -> int:
        """Retorna numero total de usuarios."""
        return self.next_id

    def export_adjacency_matrices(
        self,
        graphs: Dict[str, AdjacencyListGraph],
        output_dir: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Exporta as matrizes de adjacencia dos grafos em formato CSV e JSON.

        Args:
            graphs: Dicionario com os grafos
            output_dir: Diretorio de saida (padrao: output/matrices)

        Returns:
            Dicionario com os caminhos dos arquivos gerados
        """
        import numpy as np

        if output_dir is None:
            output_dir = os.path.join(self.output_dir, "matrices")

        # Cria diretorio se nao existir
        os.makedirs(output_dir, exist_ok=True)

        exported_files = {}

        for graph_name, graph in graphs.items():
            print(f"\nExportando matriz de: {graph_name}")

            # Obtem matriz de adjacencia (num_vertices e num_edges sao PROPRIEDADES, nao metodos)
            num_vertices = graph.num_vertices
            matrix = np.zeros((num_vertices, num_vertices))

            # Preenche matriz
            for u in range(num_vertices):
                for v in range(num_vertices):
                    if graph.has_edge(u, v):
                        weight = graph.get_edge_weight(u, v)
                        matrix[u][v] = weight

            # Cria mapeamento de indices para nomes
            index_to_user = {i: self.id_to_user.get(i, f"user_{i}")
                           for i in range(num_vertices)}

            # 1. Salva matriz em CSV com headers
            csv_file = os.path.join(output_dir, f"{graph_name}_matrix.csv")

            # Cria DataFrame com labels
            import pandas as pd
            df = pd.DataFrame(
                matrix,
                index=[index_to_user[i] for i in range(num_vertices)],
                columns=[index_to_user[i] for i in range(num_vertices)]
            )
            df.to_csv(csv_file, encoding='utf-8')
            print(f"  CSV: {os.path.basename(csv_file)}")

            # 2. Salva matriz em formato numpy (binario, mais eficiente)
            npy_file = os.path.join(output_dir, f"{graph_name}_matrix.npy")
            np.save(npy_file, matrix)
            print(f"  NumPy: {os.path.basename(npy_file)}")

            # 3. Salva metadados em JSON
            # Calcula densidade manualmente: edges / (vertices * (vertices - 1))
            num_edges_val = graph.num_edges
            density = num_edges_val / (num_vertices * (num_vertices - 1)) if num_vertices > 1 else 0.0

            metadata = {
                "graph_name": graph_name,
                "num_vertices": num_vertices,
                "num_edges": num_edges_val,
                "density": density,
                "is_directed": True,
                "has_weights": True,
                "index_to_user": index_to_user,
                "matrix_shape": [num_vertices, num_vertices],
                "matrix_sum": float(matrix.sum()),
                "matrix_max": float(matrix.max()),
                "matrix_min": float(matrix.min()),
                "non_zero_count": int(np.count_nonzero(matrix))
            }

            json_file = os.path.join(output_dir, f"{graph_name}_metadata.json")
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            print(f"  Metadata: {os.path.basename(json_file)}")

            # 4. Salva lista de arestas (formato edge list) para facil importacao
            edgelist_file = os.path.join(output_dir, f"{graph_name}_edgelist.csv")
            edges_data = []
            for u in range(num_vertices):
                for v in range(num_vertices):
                    if graph.has_edge(u, v):
                        edges_data.append({
                            'source_id': u,
                            'target_id': v,
                            'source_label': index_to_user[u],
                            'target_label': index_to_user[v],
                            'weight': graph.get_edge_weight(u, v)
                        })

            if edges_data:
                edges_df = pd.DataFrame(edges_data)
                edges_df.to_csv(edgelist_file, index=False, encoding='utf-8')
                print(f"  Edge List: {os.path.basename(edgelist_file)}")

            exported_files[graph_name] = {
                'csv': csv_file,
                'npy': npy_file,
                'metadata': json_file,
                'edgelist': edgelist_file
            }

        # Cria README explicativo
        readme_file = os.path.join(output_dir, "README_MATRICES.txt")
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(self._generate_matrices_readme())
        print(f"\nREADME criado: {os.path.basename(readme_file)}")

        return exported_files

    def _generate_matrices_readme(self) -> str:
        """Gera README explicativo sobre as matrizes"""
        return """
================================================================================
MATRIZES DE ADJACENCIA DOS GRAFOS
================================================================================

Este diretorio contem as matrizes de adjacencia dos grafos em varios formatos.

ARQUIVOS GERADOS:
-----------------

Para cada grafo, foram gerados 4 arquivos:

1. *_matrix.csv
   - Matriz de adjacencia completa em formato CSV
   - Linhas e colunas representam usuarios (com labels)
   - Valores representam pesos das arestas
   - Pode ser aberto em Excel/LibreOffice
   - Formato: matrix[i][j] = peso da aresta de i para j

2. *_matrix.npy
   - Matriz em formato binario NumPy
   - Mais eficiente para processamento em Python
   - Carregue com: np.load('arquivo.npy')

3. *_metadata.json
   - Metadados da matriz e do grafo
   - Inclui: dimensoes, numero de arestas, densidade, etc.
   - Mapeamento indice -> nome de usuario

4. *_edgelist.csv
   - Lista de arestas (edge list)
   - Formato: source, target, weight
   - Mais compacto que a matriz
   - Ideal para algoritmos de grafos

INTERPRETACAO:
--------------

Matriz[i][j] representa a aresta do usuario i para o usuario j:
- Valor 0: Nao ha aresta
- Valor > 0: Existe aresta com o peso indicado

GRAFOS:
-------

- graph_1_comments_matrix.csv: Comentarios em issues/PRs
- graph_2_closures_matrix.csv: Fechamento de issues
- graph_3_reviews_matrix.csv: Reviews e merges de PRs
- graph_4_integrated_matrix.csv: Grafo integrado com pesos

PESOS NO GRAFO INTEGRADO:
--------------------------

- Comentario: peso 2
- Issue aberta comentada: peso 3
- Review: peso 4
- Merge: peso 5

COMO USAR:
----------

### Python (NumPy):
```python
import numpy as np
import json

# Carrega matriz
matrix = np.load('graph_1_comments_matrix.npy')

# Carrega metadados
with open('graph_1_comments_metadata.json') as f:
    metadata = json.load(f)

# Acessa usuarios
index_to_user = metadata['index_to_user']
print(f"Usuario 0: {index_to_user['0']}")
```

### Python (Pandas):
```python
import pandas as pd

# Carrega matriz com labels
df = pd.read_csv('graph_1_comments_matrix.csv', index_col=0)

# Acessa peso da aresta user1 -> user2
weight = df.loc['user1', 'user2']

# Carrega edge list
edges = pd.read_csv('graph_1_comments_edgelist.csv')
```

### Excel/LibreOffice:
- Abra o arquivo *_matrix.csv
- Cada celula [linha][coluna] mostra o peso da aresta
- Use filtros e formulas para analisar

### R:
```r
# Carrega matriz
matrix <- read.csv('graph_1_comments_matrix.csv', row.names=1)

# Carrega edge list
edges <- read.csv('graph_1_comments_edgelist.csv')
```

ANALISES POSSIVEIS:
-------------------

1. Grau de saida de um usuario: soma da linha
2. Grau de entrada de um usuario: soma da coluna
3. Usuarios mais ativos: usuarios com maior grau de saida
4. Usuarios mais populares: usuarios com maior grau de entrada
5. Densidade do grafo: razao entre arestas existentes e possiveis
6. Componentes conexos: analise de conectividade
7. Caminhos entre usuarios: algoritmos de caminho minimo

================================================================================
"""
