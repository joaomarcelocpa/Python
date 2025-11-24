"""
Serviço de Geração de Grafos

Encapsula a lógica de construção e exportação de grafos.
"""

from typing import Dict, Optional, Callable
from datetime import datetime
import os
import config
from src.graph_builder import GraphBuilder


class GraphGenerationService:
    """
    Serviço responsável por gerar e exportar grafos.

    Coordena as operações de:
    - Carregamento de dados dos grafos
    - Construção dos grafos (Lista ou Matriz)
    - Exportação para formato GEXF

    Exemplo:
        service = GraphGenerationService()
        result = service.build_and_export_graphs(
            use_matrix=False,
            progress_callback=lambda p, m: print(f"{p:.0%}: {m}")
        )
    """

    def __init__(self):
        """Inicializa o serviço de geração de grafos"""
        self.builder: Optional[GraphBuilder] = None
        self.last_graphs: Optional[Dict] = None
        self.last_stats: Optional[Dict] = None

    def build_and_export_graphs(
        self,
        use_matrix: bool = False,
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> Dict:
        """
        Constrói e exporta grafos para formato GEXF.

        Args:
            use_matrix: Se True, usa Matriz de Adjacência; senão, Lista
            progress_callback: Callback para atualização de progresso (progress, message)

        Returns:
            Dict contendo:
                - success: bool
                - stats: Dict com estatísticas dos grafos
                - output_dir: str (diretório de saída)
                - graph_count: int (número de grafos gerados)
                - duration: float (segundos)

        Raises:
            FileNotFoundError: Se dados dos grafos não existirem
            Exception: Erros durante a geração
        """
        start_time = datetime.now()

        try:
            # Verifica se dados existem (0-10%)
            if progress_callback:
                progress_callback(0.0, "Verificando dados...")

            graph_data_file = os.path.join(config.OUTPUT_DIR, "graph_data.json")
            if not os.path.exists(graph_data_file):
                raise FileNotFoundError(
                    f"Arquivo {graph_data_file} não encontrado. "
                    "Execute a extração de dados primeiro."
                )

            # Inicializa builder (10-20%)
            if progress_callback:
                impl_type = "Matriz de Adjacência" if use_matrix else "Lista de Adjacência"
                progress_callback(0.1, f"Usando implementação: {impl_type}")

            self.builder = GraphBuilder(str(config.OUTPUT_DIR))

            # Constrói grafos (20-60%)
            if progress_callback:
                progress_callback(0.2, "Construindo grafos...")

            self.last_graphs = self.builder.build_all_graphs(use_matrix=use_matrix)

            graph_count = len(self.last_graphs)
            user_count = self.builder.get_user_count()

            if progress_callback:
                progress_callback(
                    0.6,
                    f"{graph_count} grafos construídos com {user_count} usuários"
                )

            # Exporta grafos (60-80%)
            if progress_callback:
                progress_callback(0.6, "Exportando grafos para formato GEXF...")

            self.last_stats = self.builder.export_all_graphs(self.last_graphs)

            gephi_dir = os.path.join(config.OUTPUT_DIR, "gephi")

            if progress_callback:
                progress_callback(0.8, f"Grafos GEXF exportados para {gephi_dir}")

            # Exporta matrizes de adjacência (80-100%)
            if progress_callback:
                progress_callback(0.8, "Exportando matrizes de adjacência...")

            matrices_files = self.builder.export_adjacency_matrices(self.last_graphs)
            matrices_dir = os.path.join(config.OUTPUT_DIR, "matrices")

            if progress_callback:
                progress_callback(1.0, f"Matrizes exportadas para {matrices_dir}")

            # Calcula duração
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            return {
                'success': True,
                'stats': self.last_stats,
                'output_dir': gephi_dir,
                'graph_count': graph_count,
                'user_count': user_count,
                'duration': duration
            }

        except FileNotFoundError as e:
            if progress_callback:
                progress_callback(0.0, f"Erro: {str(e)}")

            return {
                'success': False,
                'error': str(e),
                'error_type': 'FileNotFoundError',
                'duration': (datetime.now() - start_time).total_seconds()
            }

        except Exception as e:
            if progress_callback:
                progress_callback(0.0, f"Erro: {str(e)}")

            return {
                'success': False,
                'error': str(e),
                'duration': (datetime.now() - start_time).total_seconds()
            }

    def get_statistics(self) -> Optional[Dict]:
        """
        Retorna estatísticas dos grafos da última geração.

        Returns:
            Dict com estatísticas ou None se nenhuma geração foi feita
        """
        return self.last_stats

    def get_user_count(self) -> int:
        """
        Retorna número de usuários dos grafos.

        Returns:
            Número de usuários ou 0 se nenhum grafo foi gerado
        """
        if self.builder:
            return self.builder.get_user_count()
        return 0

    def has_graphs(self) -> bool:
        """
        Verifica se há grafos gerados.

        Returns:
            True se há grafos disponíveis
        """
        return self.last_graphs is not None and len(self.last_graphs) > 0

    def check_graph_data_exists(self) -> bool:
        """
        Verifica se existem arquivos GEXF de grafos salvos em disco.

        Returns:
            True se existem grafos salvos
        """
        gephi_dir = os.path.join(config.OUTPUT_DIR, "gephi")
        if not os.path.exists(gephi_dir):
            return False

        # Verifica se há arquivos GEXF no diretório
        gexf_files = [f for f in os.listdir(gephi_dir) if f.endswith('.gexf')]
        return len(gexf_files) > 0

    def build_graphs(
        self,
        use_matrix: bool = False,
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> Dict:
        """
        Alias para build_and_export_graphs() para compatibilidade.

        Args:
            use_matrix: Se True, usa Matriz de Adjacência; senão, Lista
            progress_callback: Callback para atualização de progresso (progress, message)

        Returns:
            Dict com resultado da geração
        """
        result = self.build_and_export_graphs(use_matrix, progress_callback)

        # Adiciona campos extras esperados pela GUI
        if result['success']:
            result['summary'] = f"✅ {result['graph_count']} grafos gerados com {result['user_count']} usuários"
            result['graph_stats'] = []

            # Converte estatísticas para formato esperado
            if self.last_stats:
                for graph_name, stats in self.last_stats.items():
                    result['graph_stats'].append({
                        'name': graph_name,
                        'vertices': stats['vertices'],
                        'edges': stats['edges'],
                        'density': stats['density'],
                        'is_empty': stats['is_empty'],
                        'is_complete': stats['is_complete'],
                        'filename': stats['filename']
                    })

        return result
