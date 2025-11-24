"""
Painel de Console para output de logs
"""

import customtkinter as ctk
from datetime import datetime


class ConsolePanel(ctk.CTkFrame):
    """
    Painel de console para exibir logs da aplicação.

    Responsabilidades:
    - Exibir mensagens de log
    - Scroll automático
    - Timestamps
    - Limpeza de console
    """

    def __init__(self, parent):
        """
        Inicializa painel de console.

        Args:
            parent: Widget pai
        """
        super().__init__(parent)

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._create_widgets()

    def _create_widgets(self):
        """Cria widgets do painel"""
        # Header com fundo
        header_frame = ctk.CTkFrame(
            self,
            corner_radius=10,
            fg_color=("#e0e7ff", "#1e293b"),
            height=50
        )
        header_frame.grid(row=0, column=0, padx=10, pady=(10, 10), sticky="ew")
        header_frame.grid_propagate(False)

        header = ctk.CTkLabel(
            header_frame,
            text="📋 Console de Saída",
            font=ctk.CTkFont(weight="bold", size=15),
            text_color=("#2563eb", "#60a5fa")
        )
        header.pack(pady=12)

        # Textbox com cantos arredondados
        self.textbox = ctk.CTkTextbox(
            self,
            wrap="word",
            font=ctk.CTkFont(family="Consolas", size=11),
            corner_radius=10,
            fg_color=("#f8fafc", "#0f172a"),
            border_width=2,
            border_color=("#e2e8f0", "#1e293b")
        )
        self.textbox.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.textbox.configure(state="disabled")

    def log(self, message: str, add_timestamp: bool = True):
        """
        Adiciona mensagem ao console.

        Args:
            message: Mensagem a adicionar
            add_timestamp: Se True, adiciona timestamp
        """
        self.textbox.configure(state="normal")

        if add_timestamp:
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.textbox.insert("end", f"[{timestamp}] ")

        self.textbox.insert("end", f"{message}\n")
        self.textbox.see("end")
        self.textbox.configure(state="disabled")

    def clear(self):
        """Limpa o console"""
        self.textbox.configure(state="normal")
        self.textbox.delete("1.0", "end")
        self.textbox.configure(state="disabled")

    def get_textbox(self):
        """Retorna widget textbox para redirecionamento"""
        return self.textbox
