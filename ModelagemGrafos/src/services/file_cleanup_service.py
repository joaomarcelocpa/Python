"""
Serviço de Limpeza de Arquivos

Encapsula toda a lógica de limpeza de dados usando o padrão Command,
permitindo operações de limpeza reutilizáveis e testáveis.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Callable
import os
from pathlib import Path
import config


class CleanupCommand(ABC):
    """Comando abstrato para operações de limpeza"""

    @abstractmethod
    def execute(self) -> int:
        """
        Executa a limpeza.

        Returns:
            Número de arquivos deletados
        """
        pass

    @abstractmethod
    def get_description(self) -> str:
        """
        Retorna descrição do que será deletado.

        Returns:
            String descrevendo a operação
        """
        pass

    @abstractmethod
    def get_title(self) -> str:
        """
        Retorna título da operação.

        Returns:
            Título curto da operação
        """
        pass


class CleanRawDataCommand(CleanupCommand):
    """Comando para limpar dados brutos da API"""

    def get_title(self) -> str:
        return "Limpar Dados Brutos"

    def get_description(self) -> str:
        return (
            "Isso irá deletar:\n"
            "• data/raw/raw_data.json\n\n"
            "Esta ação não pode ser desfeita!"
        )

    def execute(self) -> int:
        deleted_count = 0
        raw_dir = config.RAW_DATA_DIR

        if os.path.exists(raw_dir):
            for file in os.listdir(raw_dir):
                file_path = os.path.join(raw_dir, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    deleted_count += 1

        return deleted_count


class CleanProcessedDataCommand(CleanupCommand):
    """Comando para limpar dados processados"""

    def get_title(self) -> str:
        return "Limpar Dados Processados"

    def get_description(self) -> str:
        return (
            "Isso irá deletar:\n"
            "• data/processed/*.csv\n"
            "• data/processed/*.xlsx\n"
            "• data/processed/*.json\n\n"
            "Esta ação não pode ser desfeita!"
        )

    def execute(self) -> int:
        deleted_count = 0
        processed_dir = config.PROCESSED_DATA_DIR

        if os.path.exists(processed_dir):
            for file in os.listdir(processed_dir):
                file_path = os.path.join(processed_dir, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    deleted_count += 1

        return deleted_count


class CleanGraphDataCommand(CleanupCommand):
    """Comando para limpar dados e arquivos dos grafos"""

    def get_title(self) -> str:
        return "Limpar Grafos"

    def get_description(self) -> str:
        return (
            "Isso irá deletar:\n"
            "• data/graphs/* (dados dos grafos)\n"
            "• output/gephi/*.gexf (arquivos Gephi)\n"
            "• output/graph_data.json\n\n"
            "Esta ação não pode ser desfeita!"
        )

    def execute(self) -> int:
        deleted_count = 0

        # Limpa diretório graphs
        graphs_dir = config.GRAPHS_DIR
        if os.path.exists(graphs_dir):
            for file in os.listdir(graphs_dir):
                file_path = os.path.join(graphs_dir, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    deleted_count += 1

        # Limpa diretório gephi
        gephi_dir = os.path.join(config.OUTPUT_DIR, "gephi")
        if os.path.exists(gephi_dir):
            for file in os.listdir(gephi_dir):
                if file.endswith('.gexf'):
                    file_path = os.path.join(gephi_dir, file)
                    os.remove(file_path)
                    deleted_count += 1

        # Limpa graph_data.json
        graph_data_file = os.path.join(config.OUTPUT_DIR, "graph_data.json")
        if os.path.exists(graph_data_file):
            os.remove(graph_data_file)
            deleted_count += 1

        return deleted_count


class CleanAllDataCommand(CleanupCommand):
    """Comando para limpar TODOS os dados"""

    def get_title(self) -> str:
        return "⚠️ LIMPAR TUDO"

    def get_description(self) -> str:
        return (
            "ATENÇÃO: Isso irá deletar TODOS os dados!\n\n"
            "Serão deletados:\n"
            "• Dados brutos (data/raw/)\n"
            "• Dados processados (data/processed/)\n"
            "• Dados dos grafos (data/graphs/)\n"
            "• Arquivos Gephi (output/gephi/)\n"
            "• Arquivo consolidado (output/graph_data.json)\n\n"
            "Esta ação NÃO PODE ser desfeita!"
        )

    def execute(self) -> int:
        deleted_count = 0

        # Executa todos os outros comandos
        commands = [
            CleanRawDataCommand(),
            CleanProcessedDataCommand(),
            CleanGraphDataCommand()
        ]

        for command in commands:
            deleted_count += command.execute()

        return deleted_count


class FileCleanupService:
    """
    Serviço de limpeza de arquivos.

    Coordena operações de limpeza usando o padrão Command,
    permitindo confirmações e callbacks customizados.

    Exemplo:
        service = FileCleanupService()

        command = CleanRawDataCommand()
        success = service.execute_cleanup(
            command,
            confirmation_callback=lambda desc: user_confirms(desc),
            progress_callback=lambda msg: print(msg)
        )
    """

    def __init__(self):
        """Inicializa o serviço de limpeza"""
        self.commands = {
            'raw': CleanRawDataCommand(),
            'processed': CleanProcessedDataCommand(),
            'graphs': CleanGraphDataCommand(),
            'all': CleanAllDataCommand()
        }

    def get_command(self, command_type: str) -> Optional[CleanupCommand]:
        """
        Retorna comando de limpeza por tipo.

        Args:
            command_type: Tipo do comando ('raw', 'processed', 'graphs', 'all')

        Returns:
            CleanupCommand ou None se tipo inválido
        """
        return self.commands.get(command_type)

    def execute_cleanup(
        self,
        command: CleanupCommand,
        confirmation_callback: Optional[Callable[[str], bool]] = None,
        progress_callback: Optional[Callable[[str], None]] = None,
        require_double_confirmation: bool = False
    ) -> dict:
        """
        Executa comando de limpeza com confirmação.

        Args:
            command: Comando de limpeza a executar
            confirmation_callback: Callback para confirmação do usuário
            progress_callback: Callback para mensagens de progresso
            require_double_confirmation: Se True, pede confirmação duas vezes

        Returns:
            Dict contendo:
                - success: bool
                - deleted_count: int
                - error: str (se houver)
        """
        try:
            # Confirmação
            if confirmation_callback:
                title = command.get_title()
                description = command.get_description()

                if not confirmation_callback(f"{title}\n\n{description}"):
                    return {
                        'success': False,
                        'deleted_count': 0,
                        'cancelled': True
                    }

                # Segunda confirmação se necessário
                if require_double_confirmation:
                    if not confirmation_callback(
                        "Tem CERTEZA ABSOLUTA?\n\n"
                        "Todos os dados serão PERMANENTEMENTE deletados!"
                    ):
                        return {
                            'success': False,
                            'deleted_count': 0,
                            'cancelled': True
                        }

            # Executa limpeza
            if progress_callback:
                progress_callback(f"Executando: {command.get_title()}...")

            deleted_count = command.execute()

            if progress_callback:
                progress_callback(
                    f"Limpeza concluída! {deleted_count} arquivo(s) deletado(s)."
                )

            return {
                'success': True,
                'deleted_count': deleted_count
            }

        except Exception as e:
            return {
                'success': False,
                'deleted_count': 0,
                'error': str(e)
            }

    def get_available_commands(self) -> List[str]:
        """
        Retorna lista de comandos disponíveis.

        Returns:
            Lista com nomes dos comandos disponíveis
        """
        return list(self.commands.keys())
