"""
Barra Lateral da Aplicação
"""

import customtkinter as ctk
import os
from typing import Callable, Optional
import config as app_config


class Sidebar(ctk.CTkScrollableFrame):
    """
    Barra lateral com controles principais.

    Responsabilidades:
    - Exibir status dos dados
    - Botões de ação principais
    - Gerenciamento de dados
    - Seleção de tema
    """

    def __init__(
        self,
        parent,
        on_refresh: Optional[Callable] = None,
        on_extract: Optional[Callable] = None,
        on_build: Optional[Callable] = None,
        on_visualize: Optional[Callable] = None,
        on_metrics: Optional[Callable] = None,
        on_clean_console: Optional[Callable] = None,
        on_view_logs: Optional[Callable] = None,
        on_cleanup: Optional[Callable[[str], None]] = None,
        on_theme_change: Optional[Callable[[str], None]] = None
    ):
        """
        Inicializa sidebar.

        Args:
            parent: Widget pai
            on_refresh: Callback para atualizar status
            on_extract: Callback para extração
            on_build: Callback para construir grafos
            on_visualize: Callback para visualização
            on_metrics: Callback para análise de métricas
            on_clean_console: Callback para limpar console
            on_view_logs: Callback para visualizar logs
            on_cleanup: Callback para limpeza de dados
            on_theme_change: Callback para mudança de tema
        """
        super().__init__(parent, width=280, corner_radius=0, fg_color=("#f0f0f0", "#1a1a1a"))

        # Callbacks
        self.on_refresh = on_refresh
        self.on_extract = on_extract
        self.on_build = on_build
        self.on_visualize = on_visualize
        self.on_metrics = on_metrics
        self.on_clean_console = on_clean_console
        self.on_view_logs = on_view_logs
        self.on_cleanup = on_cleanup
        self.on_theme_change = on_theme_change

        # Status
        self.raw_data_status = None
        self.graph_data_status = None

        self._create_widgets()

    def _create_widgets(self):
        """Cria widgets da sidebar"""
        self._create_header()
        self._create_status_section()
        self._create_action_buttons()
        self._create_management_section()
        self._create_theme_section()

    def _create_header(self):
        """Cria cabeçalho"""
        # Frame para header com fundo destacado
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 20))

        logo = ctk.CTkLabel(
            header_frame,
            text="🔷 GitHub Graph\nAnalyzer",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=("#2563eb", "#60a5fa")
        )
        logo.pack(pady=(40, 5))

        version = ctk.CTkLabel(
            header_frame,
            text="v2.0 • Modern Edition",
            font=ctk.CTkFont(size=11),
            text_color=("gray50", "gray60")
        )
        version.pack(pady=(0, 40))

    def _create_status_section(self):
        """Cria seção de status"""
        status_frame = ctk.CTkFrame(
            self,
            corner_radius=15,
            fg_color=("#e0e7ff", "#1e293b")
        )
        status_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        ctk.CTkLabel(
            status_frame,
            text="📊 Status dos Dados",
            font=ctk.CTkFont(weight="bold", size=13),
            text_color=("#2563eb", "#60a5fa")
        ).pack(pady=(15, 10))

        self.raw_data_status = ctk.CTkLabel(
            status_frame,
            text="❌ Dados brutos",
            text_color=("#dc2626", "#ef4444"),
            font=ctk.CTkFont(size=12)
        )
        self.raw_data_status.pack(pady=3)

        self.graph_data_status = ctk.CTkLabel(
            status_frame,
            text="❌ Dados dos grafos",
            text_color=("#dc2626", "#ef4444"),
            font=ctk.CTkFont(size=12)
        )
        self.graph_data_status.pack(pady=(3, 15))

        # Botão refresh
        refresh_btn = ctk.CTkButton(
            self,
            text="🔄 Atualizar Status",
            command=self._on_refresh_click,
            corner_radius=10,
            height=36,
            fg_color=("#6366f1", "#6366f1"),
            hover_color=("#4f46e5", "#4f46e5"),
            font=ctk.CTkFont(size=12)
        )
        refresh_btn.grid(row=3, column=0, padx=20, pady=10)

    def _create_action_buttons(self):
        """Cria botões de ação"""
        # Separador
        ctk.CTkLabel(self, text="").grid(row=4, column=0, pady=5)

        # Extrair
        extract_btn = ctk.CTkButton(
            self,
            text="📥 Extrair Dados",
            command=self._on_extract_click,
            height=44,
            corner_radius=12,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("#3b82f6", "#2563eb"),
            hover_color=("#2563eb", "#1d4ed8")
        )
        extract_btn.grid(row=5, column=0, padx=20, pady=8)

        # Gerar
        build_btn = ctk.CTkButton(
            self,
            text="🔨 Gerar Grafos",
            command=self._on_build_click,
            height=44,
            corner_radius=12,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("#8b5cf6", "#7c3aed"),
            hover_color=("#7c3aed", "#6d28d9")
        )
        build_btn.grid(row=6, column=0, padx=20, pady=8)

        # Visualizar
        viz_btn = ctk.CTkButton(
            self,
            text="📊 Visualizar Grafos",
            command=self._on_visualize_click,
            height=44,
            corner_radius=12,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("#10b981", "#059669"),
            hover_color=("#059669", "#047857")
        )
        viz_btn.grid(row=7, column=0, padx=20, pady=8)

        # Analisar Métricas
        metrics_btn = ctk.CTkButton(
            self,
            text="📈 Analisar Métricas",
            command=self._on_metrics_click,
            height=44,
            corner_radius=12,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("#f59e0b", "#d97706"),
            hover_color=("#d97706", "#b45309")
        )
        metrics_btn.grid(row=8, column=0, padx=20, pady=8)

        # Limpar console
        clear_btn = ctk.CTkButton(
            self,
            text="🗑️ Limpar Console",
            command=self._on_clean_console_click,
            height=36,
            corner_radius=10,
            fg_color=("#64748b", "#475569"),
            hover_color=("#475569", "#334155"),
            font=ctk.CTkFont(size=12)
        )
        clear_btn.grid(row=9, column=0, padx=20, pady=8)

        # Ver logs
        logs_btn = ctk.CTkButton(
            self,
            text="📋 Ver Logs",
            command=self._on_view_logs_click,
            height=36,
            corner_radius=10,
            fg_color=("#6366f1", "#4f46e5"),
            hover_color=("#4f46e5", "#4338ca"),
            font=ctk.CTkFont(size=12)
        )
        logs_btn.grid(row=10, column=0, padx=20, pady=8)

    def _create_management_section(self):
        """Cria seção de gerenciamento"""
        # Separador
        ctk.CTkLabel(self, text="").grid(row=11, column=0, pady=10)

        # Label
        ctk.CTkLabel(
            self,
            text="⚙️ Gerenciar Dados",
            font=ctk.CTkFont(weight="bold", size=13),
            text_color=("#64748b", "#94a3b8")
        ).grid(row=12, column=0, padx=20, pady=(10, 8))

        # Menu dropdown
        self.clean_menu = ctk.CTkOptionMenu(
            self,
            values=[
                "Selecione...",
                "Limpar Dados Brutos",
                "Limpar Dados Processados",
                "Limpar Grafos",
                "⚠️ Limpar TUDO"
            ],
            command=self._on_cleanup_select,
            corner_radius=10,
            fg_color=("#dc2626", "#991b1b"),
            button_color=("#dc2626", "#991b1b"),
            button_hover_color=("#b91c1c", "#7f1d1d"),
            font=ctk.CTkFont(size=12)
        )
        self.clean_menu.set("Selecione...")
        self.clean_menu.grid(row=13, column=0, padx=20, pady=(0, 10))

    def _create_theme_section(self):
        """Cria seção de tema"""
        ctk.CTkLabel(
            self,
            text="🎨 Aparência",
            font=ctk.CTkFont(weight="bold", size=13),
            text_color=("#64748b", "#94a3b8")
        ).grid(row=14, column=0, padx=20, pady=(20, 8))

        self.appearance_menu = ctk.CTkOptionMenu(
            self,
            values=["Dark", "Light", "System"],
            command=self._on_theme_select,
            corner_radius=10,
            fg_color=("#6366f1", "#4f46e5"),
            button_color=("#6366f1", "#4f46e5"),
            button_hover_color=("#4f46e5", "#4338ca"),
            font=ctk.CTkFont(size=12)
        )
        self.appearance_menu.set("Dark")
        self.appearance_menu.grid(row=15, column=0, padx=20, pady=(0, 30))

    # Handlers de eventos
    def _on_refresh_click(self):
        """Handler para refresh"""
        if self.on_refresh:
            self.on_refresh()

    def _on_extract_click(self):
        """Handler para extração"""
        if self.on_extract:
            self.on_extract()

    def _on_build_click(self):
        """Handler para construção"""
        if self.on_build:
            self.on_build()

    def _on_visualize_click(self):
        """Handler para visualização"""
        if self.on_visualize:
            self.on_visualize()

    def _on_metrics_click(self):
        """Handler para análise de métricas"""
        if self.on_metrics:
            self.on_metrics()

    def _on_clean_console_click(self):
        """Handler para limpar console"""
        if self.on_clean_console:
            self.on_clean_console()

    def _on_view_logs_click(self):
        """Handler para ver logs"""
        if self.on_view_logs:
            self.on_view_logs()

    def _on_cleanup_select(self, choice: str):
        """Handler para limpeza de dados"""
        self.clean_menu.set("Selecione...")

        if choice != "Selecione..." and self.on_cleanup:
            self.on_cleanup(choice)

    def _on_theme_select(self, theme: str):
        """Handler para mudança de tema"""
        if self.on_theme_change:
            self.on_theme_change(theme)

    # Métodos públicos
    def update_status(self, raw_exists: bool, graph_exists: bool):
        """
        Atualiza status dos dados.

        Args:
            raw_exists: Se dados brutos existem
            graph_exists: Se dados dos grafos existem
        """
        if raw_exists:
            self.raw_data_status.configure(
                text="✅ Dados brutos",
                text_color=("#059669", "#10b981")
            )
        else:
            self.raw_data_status.configure(
                text="❌ Dados brutos",
                text_color=("#dc2626", "#ef4444")
            )

        if graph_exists:
            self.graph_data_status.configure(
                text="✅ Dados dos grafos",
                text_color=("#059669", "#10b981")
            )
        else:
            self.graph_data_status.configure(
                text="❌ Dados dos grafos",
                text_color=("#dc2626", "#ef4444")
            )
