"""
Sistema de Logging Centralizado
Fornece logging para arquivo e console com rotação automática
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler
import traceback


class AppLogger:
    """
    Logger centralizado da aplicação.

    Features:
    - Log para arquivo com rotação automática
    - Log para console (opcional)
    - Níveis de log configuráveis
    - Formatação consistente
    - Captura de stack traces
    """

    _instance = None
    _initialized = False

    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Inicializa o logger (apenas uma vez)"""
        if AppLogger._initialized:
            return

        AppLogger._initialized = True

        # Cria diretório de logs
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)

        # Nome do arquivo de log
        log_filename = self.log_dir / "graph_analyzer.log"

        # Configura logger raiz
        self.logger = logging.getLogger("GraphAnalyzer")
        self.logger.setLevel(logging.DEBUG)

        # Remove handlers existentes
        self.logger.handlers.clear()

        # Handler para arquivo com rotação
        # Mantém 5 arquivos de 5MB cada
        file_handler = RotatingFileHandler(
            log_filename,
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)

        # Formato detalhado para arquivo
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

        # Handler para console (opcional, apenas warnings e erros)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        console_formatter = logging.Formatter(
            '%(levelname)s: %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        # Comentado por padrão para não poluir o console da GUI
        # self.logger.addHandler(console_handler)

        # Log inicial
        self.logger.info("="*70)
        self.logger.info("Sistema de Logging Iniciado")
        self.logger.info(f"Arquivo de log: {log_filename.absolute()}")
        self.logger.info("="*70)

    def debug(self, message: str, **kwargs):
        """Log de debug (detalhes de desenvolvimento)"""
        self.logger.debug(message, **kwargs)

    def info(self, message: str, **kwargs):
        """Log de informação (eventos normais)"""
        self.logger.info(message, **kwargs)

    def warning(self, message: str, **kwargs):
        """Log de aviso (situações inesperadas mas não críticas)"""
        self.logger.warning(message, **kwargs)

    def error(self, message: str, exc_info=None, **kwargs):
        """
        Log de erro.

        Args:
            message: Mensagem de erro
            exc_info: Exception ou True para capturar automaticamente
        """
        self.logger.error(message, exc_info=exc_info, **kwargs)

    def critical(self, message: str, exc_info=None, **kwargs):
        """
        Log crítico (erro grave que pode parar a aplicação).

        Args:
            message: Mensagem crítica
            exc_info: Exception ou True para capturar automaticamente
        """
        self.logger.critical(message, exc_info=exc_info, **kwargs)

    def exception(self, message: str, **kwargs):
        """
        Log de exceção (captura automaticamente o stack trace atual).
        Deve ser chamado dentro de um except block.
        """
        self.logger.exception(message, **kwargs)

    def log_function_call(self, func_name: str, **params):
        """Log de chamada de função com parâmetros"""
        params_str = ", ".join(f"{k}={v}" for k, v in params.items())
        self.logger.debug(f"Chamando {func_name}({params_str})")

    def log_performance(self, operation: str, duration: float):
        """Log de performance"""
        self.logger.info(f"Performance: {operation} levou {duration:.3f}s")

    def get_log_file_path(self) -> Path:
        """Retorna o caminho do arquivo de log atual"""
        return self.log_dir / "graph_analyzer.log"

    def get_recent_logs(self, num_lines: int = 100) -> str:
        """
        Retorna as últimas N linhas do log.

        Args:
            num_lines: Número de linhas a retornar

        Returns:
            String com as últimas linhas do log
        """
        log_file = self.get_log_file_path()

        if not log_file.exists():
            return "Arquivo de log não encontrado"

        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                return ''.join(lines[-num_lines:])
        except Exception as e:
            return f"Erro ao ler log: {e}"


# Instância global do logger
_logger_instance = None


def get_logger() -> AppLogger:
    """
    Retorna instância singleton do logger.

    Returns:
        Instância de AppLogger
    """
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = AppLogger()
    return _logger_instance


# Funções de conveniência
def debug(message: str, **kwargs):
    """Log de debug"""
    get_logger().debug(message, **kwargs)


def info(message: str, **kwargs):
    """Log de informação"""
    get_logger().info(message, **kwargs)


def warning(message: str, **kwargs):
    """Log de aviso"""
    get_logger().warning(message, **kwargs)


def error(message: str, exc_info=None, **kwargs):
    """Log de erro"""
    get_logger().error(message, exc_info=exc_info, **kwargs)


def critical(message: str, exc_info=None, **kwargs):
    """Log crítico"""
    get_logger().critical(message, exc_info=exc_info, **kwargs)


def exception(message: str, **kwargs):
    """Log de exceção (captura stack trace)"""
    get_logger().exception(message, **kwargs)


def log_function_call(func_name: str, **params):
    """Log de chamada de função"""
    get_logger().log_function_call(func_name, **params)


def log_performance(operation: str, duration: float):
    """Log de performance"""
    get_logger().log_performance(operation, duration)
