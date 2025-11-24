"""
Painel de Configuração
"""

import customtkinter as ctk
import config as app_config


class ConfigPanel(ctk.CTkFrame):
    """
    Painel de configuração do repositório e opções.

    Responsabilidades:
    - Input de configurações
    - Validação básica
    - Opções de grafo
    """

    def __init__(self, parent):
        """
        Inicializa painel de configuração.

        Args:
            parent: Widget pai
        """
        super().__init__(parent)

        # Variáveis
        self.repo_owner = ctk.StringVar(value=app_config.REPO_OWNER)
        self.repo_name = ctk.StringVar(value=app_config.REPO_NAME)
        self.github_token = ctk.StringVar(value=app_config.GITHUB_TOKEN or "")
        self.use_matrix = ctk.BooleanVar(value=False)

        self._create_widgets()

    def _create_widgets(self):
        """Cria widgets do painel"""
        # Título
        title = ctk.CTkLabel(
            self,
            text="⚙️ Configurações e Opções",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=("#2563eb", "#60a5fa")
        )
        title.grid(row=0, column=0, padx=30, pady=(30, 15), sticky="w")

        # Tabview para organizar
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Tabs
        self.tabview.add("⚙️ Configuração")
        self.tabview.add("📊 Opções de Grafo")

        self._setup_config_tab()
        self._setup_graph_options_tab()

    def _setup_config_tab(self):
        """Configura tab de configuração"""
        config_tab = self.tabview.tab("⚙️ Configuração")

        input_frame = ctk.CTkFrame(
            config_tab,
            corner_radius=15,
            fg_color=("#f8fafc", "#1e293b")
        )
        input_frame.pack(fill="x", padx=15, pady=15)

        # Owner
        ctk.CTkLabel(
            input_frame,
            text="📁 Proprietário do Repositório:",
            font=ctk.CTkFont(weight="bold", size=13),
            text_color=("#475569", "#94a3b8")
        ).grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")

        self.owner_entry = ctk.CTkEntry(
            input_frame,
            textvariable=self.repo_owner,
            width=300,
            height=38,
            corner_radius=10,
            font=ctk.CTkFont(size=13)
        )
        self.owner_entry.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="ew")

        # Repo
        ctk.CTkLabel(
            input_frame,
            text="📦 Nome do Repositório:",
            font=ctk.CTkFont(weight="bold", size=13),
            text_color=("#475569", "#94a3b8")
        ).grid(row=2, column=0, padx=15, pady=(10, 5), sticky="w")

        self.repo_entry = ctk.CTkEntry(
            input_frame,
            textvariable=self.repo_name,
            width=300,
            height=38,
            corner_radius=10,
            font=ctk.CTkFont(size=13)
        )
        self.repo_entry.grid(row=3, column=0, padx=15, pady=(0, 15), sticky="ew")

        # Token
        ctk.CTkLabel(
            input_frame,
            text="🔑 GitHub Token (opcional):",
            font=ctk.CTkFont(weight="bold", size=13),
            text_color=("#475569", "#94a3b8")
        ).grid(row=4, column=0, padx=15, pady=(10, 5), sticky="w")

        self.token_entry = ctk.CTkEntry(
            input_frame,
            textvariable=self.github_token,
            width=300,
            height=38,
            corner_radius=10,
            show="*",
            font=ctk.CTkFont(size=13)
        )
        self.token_entry.grid(row=5, column=0, padx=15, pady=(0, 8), sticky="ew")

        ctk.CTkLabel(
            input_frame,
            text="💡 Token aumenta o rate limit da API (recomendado)",
            text_color=("#64748b", "#64748b"),
            font=ctk.CTkFont(size=11)
        ).grid(row=6, column=0, padx=15, pady=(0, 15), sticky="w")

        input_frame.grid_columnconfigure(0, weight=1)

    def _setup_graph_options_tab(self):
        """Configura tab de opções de grafo"""
        graph_tab = self.tabview.tab("📊 Opções de Grafo")

        options_frame = ctk.CTkFrame(
            graph_tab,
            corner_radius=15,
            fg_color=("#f8fafc", "#1e293b")
        )
        options_frame.pack(fill="x", padx=15, pady=15)

        ctk.CTkLabel(
            options_frame,
            text="🔧 Implementação do Grafo:",
            font=ctk.CTkFont(weight="bold", size=14),
            text_color=("#475569", "#94a3b8")
        ).pack(padx=15, pady=(15, 10), anchor="w")

        # Radio buttons
        ctk.CTkRadioButton(
            options_frame,
            text="📋 Lista de Adjacência (recomendado)",
            variable=self.use_matrix,
            value=False,
            font=ctk.CTkFont(size=13),
            fg_color=("#3b82f6", "#2563eb"),
            hover_color=("#2563eb", "#1d4ed8")
        ).pack(padx=25, pady=5, anchor="w")

        ctk.CTkRadioButton(
            options_frame,
            text="🔲 Matriz de Adjacência",
            variable=self.use_matrix,
            value=True,
            font=ctk.CTkFont(size=13),
            fg_color=("#3b82f6", "#2563eb"),
            hover_color=("#2563eb", "#1d4ed8")
        ).pack(padx=25, pady=(5, 15), anchor="w")

        # Informações
        info_frame = ctk.CTkFrame(
            graph_tab,
            corner_radius=15,
            fg_color=("#f1f5f9", "#0f172a")
        )
        info_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        ctk.CTkLabel(
            info_frame,
            text="📈 Grafos que serão gerados:",
            font=ctk.CTkFont(weight="bold", size=14),
            text_color=("#475569", "#94a3b8")
        ).pack(padx=15, pady=(15, 10), anchor="w")

        info_text = """
📝 Grafo 1: Comentários em issues/PRs
   └─ Aresta: comentador → autor

🔒 Grafo 2: Fechamento de Issues
   └─ Aresta: quem fechou → autor

✅ Grafo 3: Reviews e Merges
   └─ Aresta: revisor/merger → autor

🎯 Grafo 4: Integrado (com pesos)
   └─ Combina todas as interações
        """

        ctk.CTkLabel(
            info_frame,
            text=info_text,
            justify="left",
            font=ctk.CTkFont(family="Consolas", size=11)
        ).pack(padx=20, pady=(5, 10), anchor="w")

    def get_config(self) -> dict:
        """
        Retorna configuração atual.

        Returns:
            Dict com configurações
        """
        return {
            'owner': self.repo_owner.get().strip(),
            'repo': self.repo_name.get().strip(),
            'token': self.github_token.get().strip() or None,
            'use_matrix': self.use_matrix.get()
        }

    def validate_config(self) -> tuple[bool, str]:
        """
        Valida configuração.

        Returns:
            (is_valid, error_message)
        """
        config = self.get_config()

        if not config['owner']:
            return False, "Proprietário do repositório é obrigatório"

        if not config['repo']:
            return False, "Nome do repositório é obrigatório"

        return True, ""
