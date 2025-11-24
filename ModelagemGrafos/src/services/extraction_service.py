"""
Serviço de Extração de Dados do GitHub

Encapsula toda a lógica de extração de dados, permitindo reutilização
em diferentes interfaces (GUI, CLI, API).
"""

from typing import Dict, Callable, Optional
from datetime import datetime
import config
from src.github_api import GitHubAPIClient
from src.graph_data_extractor import GraphDataExtractor
from src.data_processor import DataProcessor


class ExtractionService:
    """
    Serviço responsável por extrair dados do GitHub e processar informações.

    Este serviço coordena as operações de:
    - Coleta de dados da API do GitHub
    - Extração de dados para grafos
    - Processamento de estatísticas

    Exemplo:
        service = ExtractionService()
        result = service.extract_repository_data(
            owner="facebook",
            repo="react",
            progress_callback=lambda p, m: print(f"{p:.0%}: {m}")
        )
    """

    def __init__(self):
        """Inicializa o serviço de extração"""
        self.api_client: Optional[GitHubAPIClient] = None
        self.extractor: Optional[GraphDataExtractor] = None
        self.processor: Optional[DataProcessor] = None
        self._last_extraction_time: Optional[float] = None

    def extract_repository_data(
        self,
        owner: str,
        repo: str,
        token: Optional[str] = None,
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> Dict:
        """
        Extrai dados completos do repositório GitHub.

        Args:
            owner: Proprietário do repositório
            repo: Nome do repositório
            token: Token de acesso do GitHub (opcional)
            progress_callback: Callback para atualização de progresso (progress, message)

        Returns:
            Dict contendo:
                - success: bool
                - summary: Dict com resumo da coleta
                - stats: Dict com estatísticas dos grafos
                - duration: float (segundos)

        Raises:
            ValueError: Se owner ou repo forem inválidos
            Exception: Erros durante a extração
        """
        # Validação
        if not owner or not repo:
            raise ValueError("Owner e repo são obrigatórios")

        start_time = datetime.now()

        try:
            # Fase 1: Coleta de dados da API (0-40%)
            if progress_callback:
                progress_callback(0.0, "Iniciando coleta de dados da API...")

            self.api_client = GitHubAPIClient(owner, repo, token)
            self.api_client.fetch_all_data()

            if config.SAVE_RAW_DATA:
                self.api_client.save_raw_data()

            summary = self.api_client.get_summary()

            if progress_callback:
                progress_callback(0.4, "Dados da API coletados com sucesso")

            # Fase 2: Extração de dados dos grafos (40-70%)
            if progress_callback:
                progress_callback(0.4, "Extraindo dados dos grafos...")

            self.extractor = GraphDataExtractor(self.api_client.raw_data)
            self.extractor.extract_all()

            if config.SAVE_GRAPHS:
                self.extractor.save_graph_data()

            stats = self.extractor.statistics

            if progress_callback:
                progress_callback(0.7, "Dados dos grafos extraídos")

            # Fase 3: Processamento de dados (70-100%)
            if progress_callback:
                progress_callback(0.7, "Processando dados e gerando relatórios...")

            self.processor = DataProcessor(self.api_client.raw_data)
            self.processor.process_all()
            self.processor.save_processed_data()

            if progress_callback:
                progress_callback(1.0, "Processamento concluído!")

            # Calcula duração
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            self._last_extraction_time = duration

            return {
                'success': True,
                'summary': summary,
                'stats': stats,
                'duration': duration
            }

        except Exception as e:
            if progress_callback:
                progress_callback(0.0, f"Erro: {str(e)}")

            return {
                'success': False,
                'error': str(e),
                'duration': (datetime.now() - start_time).total_seconds()
            }

    def get_summary(self) -> Optional[Dict]:
        """
        Retorna resumo da última extração.

        Returns:
            Dict com resumo ou None se nenhuma extração foi feita
        """
        if self.api_client:
            return self.api_client.get_summary()
        return None

    def get_statistics(self) -> Optional[Dict]:
        """
        Retorna estatísticas dos grafos da última extração.

        Returns:
            Dict com estatísticas ou None se nenhuma extração foi feita
        """
        if self.extractor:
            return self.extractor.statistics
        return None

    def get_last_extraction_time(self) -> Optional[float]:
        """
        Retorna tempo da última extração em segundos.

        Returns:
            float com segundos ou None se nenhuma extração foi feita
        """
        return self._last_extraction_time

    def has_data(self) -> bool:
        """
        Verifica se há dados extraídos.

        Returns:
            True se há dados disponíveis
        """
        return self.api_client is not None and self.extractor is not None

    def check_raw_data_exists(self) -> bool:
        """
        Verifica se existem dados brutos salvos em disco.

        Returns:
            True se existem dados brutos salvos
        """
        import os
        raw_data_dir = config.DATA_DIR / "raw"
        if not raw_data_dir.exists():
            return False

        # Verifica se há arquivos JSON no diretório
        json_files = list(raw_data_dir.glob("*.json"))
        return len(json_files) > 0
