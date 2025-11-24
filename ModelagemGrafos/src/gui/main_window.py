"""
Janela Principal da Aplicação - Versão Refatorada
Utiliza service layer e componentes modulares
"""

import customtkinter as ctk
import sys
import threading
from typing import Optional

import config
from src.gui.components.sidebar import Sidebar
from src.gui.components.config_panel import ConfigPanel
from src.gui.components.console_panel import ConsolePanel
from src.gui.windows.visualization_window import VisualizationWindow
from src.gui.windows.log_viewer_window import LogViewerWindow
from src.gui.windows.metrics_window import MetricsWindow
from src.gui.utils.text_redirector import TextRedirector
from src.gui.utils.dialog_helper import DialogHelper

from src.services.extraction_service import ExtractionService
from src.services.graph_generation_service import GraphGenerationService
from src.services.file_cleanup_service import (
    FileCleanupService,
    CleanRawDataCommand,
    CleanProcessedDataCommand,
    CleanGraphDataCommand,
    CleanAllDataCommand
)


class MainWindow:
    """
    Janela principal da aplicação.

    Responsabilidades:
    - Coordenar componentes da GUI
    - Gerenciar serviços
    - Orquestrar fluxo de trabalho
    """

    def __init__(self):
        """Inicializa janela principal"""
        # Criar janela
        self.window = ctk.CTk()
        self.window.title("🔷 GitHub Graph Analyzer v2.0 • Modern Edition")
        self.window.geometry("1024x700")
        self.window.minsize(900, 600)  # Tamanho mínimo para manter usabilidade

        # Estado
        self.is_processing = False
        self.visualization_window: Optional[VisualizationWindow] = None
        self.log_viewer_window: Optional[LogViewerWindow] = None
        self.metrics_window: Optional[MetricsWindow] = None

        # Serviços
        self._init_services()

        # Layout
        self._setup_layout()

        # Componentes
        self._create_components()

        # Redirecionamento de output
        self._setup_output_redirect()

        # Status inicial
        self._refresh_status()

    def _init_services(self):
        """Inicializa serviços"""
        self.extraction_service = ExtractionService()
        self.graph_service = GraphGenerationService()
        self.cleanup_service = FileCleanupService()

    def _setup_layout(self):
        """Configura layout da janela"""
        self.window.grid_columnconfigure(1, weight=1)
        self.window.grid_rowconfigure(0, weight=1)

    def _create_components(self):
        """Cria componentes da GUI"""
        # Sidebar
        self.sidebar = Sidebar(
            self.window,
            on_refresh=self._handle_refresh,
            on_extract=self._handle_extract,
            on_build=self._handle_build,
            on_visualize=self._handle_visualize,
            on_metrics=self._handle_metrics,
            on_clean_console=self._handle_clean_console,
            on_view_logs=self._handle_view_logs,
            on_cleanup=self._handle_cleanup,
            on_theme_change=self._handle_theme_change
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        # Área principal
        main_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)

        # Painel de configuração
        self.config_panel = ConfigPanel(main_frame)
        self.config_panel.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        # Console
        self.console = ConsolePanel(main_frame)
        self.console.grid(row=1, column=0, sticky="nsew")

    def _setup_output_redirect(self):
        """Configura redirecionamento de stdout"""
        textbox = self.console.get_textbox()
        sys.stdout = TextRedirector(textbox)

    # ==================== Handlers ====================

    def _handle_refresh(self):
        """Handler para atualizar status"""
        self._refresh_status()
        self.console.log("✅ Status atualizado")

    def _handle_extract(self):
        """Handler para extração de dados"""
        if self.is_processing:
            DialogHelper.show_warning("Aviso", "Aguarde a operação atual terminar")
            return

        # Valida configuração
        is_valid, error_msg = self.config_panel.validate_config()
        if not is_valid:
            DialogHelper.show_error("Erro de Validação", error_msg)
            return

        # Inicia extração em thread separada
        thread = threading.Thread(target=self._run_extraction, daemon=True)
        thread.start()

    def _handle_build(self):
        """Handler para construção de grafos"""
        if self.is_processing:
            DialogHelper.show_warning("Aviso", "Aguarde a operação atual terminar")
            return

        # Inicia construção em thread separada
        thread = threading.Thread(target=self._run_graph_build, daemon=True)
        thread.start()

    def _handle_visualize(self):
        """Handler para visualização"""
        # Cria ou traz à frente a janela de visualização
        if self.visualization_window is None or not self.visualization_window.winfo_exists():
            self.visualization_window = VisualizationWindow(self.window)
        else:
            self.visualization_window.focus()

    def _handle_metrics(self):
        """Handler para análise de métricas"""
        # Cria ou traz à frente a janela de métricas
        if self.metrics_window is None or not self.metrics_window.winfo_exists():
            self.metrics_window = MetricsWindow(self.window)
        else:
            self.metrics_window.focus()

    def _handle_clean_console(self):
        """Handler para limpar console"""
        self.console.clear()

    def _handle_view_logs(self):
        """Handler para visualização de logs"""
        # Cria ou traz à frente a janela de logs
        if self.log_viewer_window is None or not self.log_viewer_window.winfo_exists():
            self.log_viewer_window = LogViewerWindow(self.window)
        else:
            self.log_viewer_window.focus()

    def _handle_cleanup(self, choice: str):
        """Handler para limpeza de dados"""
        # Mapeia escolha para comando
        command_map = {
            "Limpar Dados Brutos": CleanRawDataCommand(),
            "Limpar Dados Processados": CleanProcessedDataCommand(),
            "Limpar Grafos": CleanGraphDataCommand(),
            "⚠️ Limpar TUDO": CleanAllDataCommand()
        }

        if choice not in command_map:
            return

        command = command_map[choice]

        # Confirmação
        if not DialogHelper.confirm(
            "Confirmar Limpeza",
            f"Tem certeza que deseja executar:\n\n{command.get_description()}?\n\n"
            "Esta ação não pode ser desfeita!"
        ):
            return

        # Confirmação adicional para limpar tudo
        if choice == "⚠️ Limpar TUDO":
            if not DialogHelper.confirm(
                "⚠️ ÚLTIMA CONFIRMAÇÃO ⚠️",
                "Você está prestes a APAGAR TODOS OS DADOS!\n\n"
                "Continuar?"
            ):
                return

        # Executa limpeza
        try:
            deleted_count = self.cleanup_service.execute_cleanup(command)
            self.console.log(f"✅ Limpeza concluída: {deleted_count} arquivo(s) removido(s)")
            DialogHelper.show_success(
                "Limpeza Concluída",
                f"Limpeza concluída!\n\n{deleted_count} arquivo(s) removido(s)"
            )
            self._refresh_status()
        except Exception as e:
            error_msg = f"Erro ao limpar dados: {e}"
            self.console.log(f"❌ {error_msg}")
            DialogHelper.show_error("Erro na Limpeza", error_msg)

    def _handle_theme_change(self, theme: str):
        """Handler para mudança de tema"""
        ctk.set_appearance_mode(theme)
        self.console.log(f"🎨 Tema alterado para: {theme}")

    # ==================== Operações Assíncronas ====================

    def _run_extraction(self):
        """Executa extração de dados em background"""
        try:
            self._set_processing(True)
            self.console.log("📥 Iniciando extração de dados...")

            # Obtém configuração
            cfg = self.config_panel.get_config()

            # Executa extração com callback de progresso
            result = self.extraction_service.extract_repository_data(
                owner=cfg['owner'],
                repo=cfg['repo'],
                token=cfg['token'],
                progress_callback=self._on_extraction_progress
            )

            if result['success']:
                self.console.log(f"\n✅ Extração concluída em {result['duration']:.2f}s")

                # Exibe resumo se disponível
                if 'summary' in result:
                    self.console.log(str(result['summary']))

                # Monta mensagem de sucesso
                success_msg = f"Dados extraídos com sucesso!\n\nTempo: {result['duration']:.2f}s"

                # Adiciona estatísticas se disponíveis
                if 'stats' in result and result['stats']:
                    stats = result['stats']
                    if 'total_users' in stats:
                        success_msg += f"\nUsuários: {stats['total_users']}"
                    if 'total_edges' in stats:
                        success_msg += f"\nInterações: {stats['total_edges']}"

                DialogHelper.show_success("Sucesso", success_msg)
                self._refresh_status()
            else:
                raise Exception(result.get('error', 'Erro desconhecido'))

        except Exception as e:
            error_msg = f"Erro na extração: {e}"
            self.console.log(f"\n❌ {error_msg}")
            DialogHelper.show_error("Erro na Extração", error_msg)
            import traceback
            traceback.print_exc()
        finally:
            self._set_processing(False)

    def _run_graph_build(self):
        """Executa construção de grafos em background"""
        try:
            self._set_processing(True)
            self.console.log("🔨 Iniciando construção de grafos...")

            # Obtém configuração
            cfg = self.config_panel.get_config()

            # Executa construção com callback de progresso
            result = self.graph_service.build_graphs(
                use_matrix=cfg['use_matrix'],
                progress_callback=self._on_build_progress
            )

            if result['success']:
                self.console.log(f"\n✅ Grafos gerados em {result['duration']:.2f}s")

                if 'summary' in result:
                    self.console.log(result['summary'])

                # Exibe estatísticas
                if 'graph_stats' in result and result['graph_stats']:
                    self.console.log("\n📊 Estatísticas dos grafos:")
                    for stats in result['graph_stats']:
                        self.console.log(f"\n{stats['name']}:")
                        self.console.log(f"  Vértices: {stats['vertices']:,}")
                        self.console.log(f"  Arestas: {stats['edges']:,}")
                        self.console.log(f"  Densidade: {stats['density']:.6f}")

                success_msg = f"Grafos gerados com sucesso!\n\nTempo: {result['duration']:.2f}s"
                if 'output_dir' in result:
                    success_msg += f"\n\nArquivos GEXF salvos em:\n{result['output_dir']}"

                DialogHelper.show_success("Sucesso", success_msg)
                self._refresh_status()
            else:
                raise Exception(result.get('error', 'Erro desconhecido'))

        except FileNotFoundError as e:
            error_msg = "Dados não encontrados!\n\nExecute a extração de dados primeiro."
            self.console.log(f"\n❌ {error_msg}")
            DialogHelper.show_error("Dados Não Encontrados", error_msg)
        except Exception as e:
            error_msg = f"Erro ao construir grafos: {e}"
            self.console.log(f"\n❌ {error_msg}")
            DialogHelper.show_error("Erro na Construção", error_msg)
            import traceback
            traceback.print_exc()
        finally:
            self._set_processing(False)

    # ==================== Callbacks ====================

    def _on_extraction_progress(self, progress: float, message: str):
        """Callback de progresso da extração"""
        self.console.log(f"[{progress*100:.0f}%] {message}")

    def _on_build_progress(self, progress: float, message: str):
        """Callback de progresso da construção"""
        self.console.log(f"[{progress*100:.0f}%] {message}")

    # ==================== Utilitários ====================

    def _set_processing(self, processing: bool):
        """Define estado de processamento"""
        self.is_processing = processing

    def _refresh_status(self):
        """Atualiza status dos dados"""
        raw_exists = self.extraction_service.check_raw_data_exists()
        graph_exists = self.graph_service.check_graph_data_exists()
        self.sidebar.update_status(raw_exists, graph_exists)

    # ==================== Main Loop ====================

    def run(self):
        """Inicia aplicação"""
        self.console.log("🚀 GitHub Repository Graph Analyzer v2.0")
        self.console.log("=" * 50)
        self.console.log("Aplicação iniciada com sucesso!")
        self.console.log("Configure o repositório e clique em 'Extrair Dados' para começar.\n")

        self.window.mainloop()
