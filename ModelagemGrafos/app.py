"""
Entry Point da Aplicação
GitHub Repository Graph Analyzer v2.0
"""

import customtkinter as ctk
import config
from src.gui.main_window import MainWindow


def init_directories():
    """Cria diretórios necessários para a aplicação."""
    for directory in config.REQUIRED_DIRECTORIES:
        directory.mkdir(parents=True, exist_ok=True)


def main():
    """
    Função principal da aplicação.

    Configura CustomTkinter e inicia a janela principal.
    """
    # Inicializa diretórios necessários
    init_directories()

    # Valida configuração
    if not config.GITHUB_TOKEN:
        print("WARNING: GITHUB_TOKEN não configurado. Rate limits serão mais restritivos.")
        print("   Configure o token no arquivo .env para melhor performance.")

    print(f"Configuração carregada")
    print(f"  Repositório: {config.REPO_OWNER}/{config.REPO_NAME}")
    print(f"  Token configurado: {'Sim' if config.GITHUB_TOKEN else 'Não'}")
    print(f"  Diretório de dados: {config.DATA_DIR}")
    print(f"  Diretório de output: {config.OUTPUT_DIR}")

    # Configurações do CustomTkinter
    ctk.set_appearance_mode("dark")  # Modes: "System", "Dark", "Light"
    ctk.set_default_color_theme("blue")  # Themes: "blue", "green", "dark-blue"

    # Cria e executa janela principal
    app = MainWindow()
    app.run()


if __name__ == "__main__":
    main()
