"""
Script de Teste para Sistema de Logging
Testa se o sistema de logging está funcionando corretamente
"""

from src.utils.logger import get_logger


def test_logging():
    """Testa todas as funcionalidades do sistema de logging"""

    print("="*70)
    print("TESTE DO SISTEMA DE LOGGING")
    print("="*70)

    # Obtém logger
    logger = get_logger()

    print("\n1. Testando níveis de log...")
    logger.debug("Mensagem de DEBUG - detalhes técnicos")
    logger.info("Mensagem de INFO - informação geral")
    logger.warning("Mensagem de WARNING - aviso")
    logger.error("Mensagem de ERROR - erro não crítico")
    logger.critical("Mensagem de CRITICAL - erro crítico")

    print("\n2. Testando logging com parâmetros...")
    logger.log_function_call("test_function", param1="valor1", param2="valor2")

    print("\n3. Testando logging de performance...")
    logger.log_performance("operação_teste", 1.234)

    print("\n4. Testando captura de exceção...")
    try:
        # Força um erro
        resultado = 10 / 0
    except Exception as e:
        logger.exception("Erro ao dividir por zero (teste)")

    print("\n5. Obtendo caminho do arquivo de log...")
    log_file = logger.get_log_file_path()
    print(f"   Arquivo de log: {log_file}")
    print(f"   Existe: {log_file.exists()}")

    if log_file.exists():
        print(f"   Tamanho: {log_file.stat().st_size} bytes")

    print("\n6. Lendo últimas 10 linhas do log...")
    recent_logs = logger.get_recent_logs(10)
    print("\n" + "-"*70)
    print(recent_logs)
    print("-"*70)

    print("\n[OK] Teste concluído!")
    print(f"\n[INFO] Para visualizar os logs completos:")
    print(f"   - Abra o arquivo: {log_file}")
    print(f"   - Ou use o botão 'Ver Logs' na interface gráfica")
    print()


if __name__ == "__main__":
    test_logging()
