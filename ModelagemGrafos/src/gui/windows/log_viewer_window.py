"""
Janela de Visualização de Logs
Permite consultar e filtrar logs da aplicação
"""

import os
import customtkinter as ctk
from tkinter import messagebox, filedialog
from pathlib import Path
from src.utils.logger import get_logger


class LogViewerWindow(ctk.CTkToplevel):
    """
    Janela para visualização de logs.

    Responsabilidades:
    - Exibir logs em tempo real
    - Filtrar logs por nível
    - Buscar texto nos logs
    - Exportar logs
    - Auto-refresh
    """

    def __init__(self, parent):
        """
        Inicializa janela de logs.

        Args:
            parent: Widget pai
        """
        super().__init__(parent)

        self.title("📋 Visualizador de Logs • Graph Analyzer")
        self.geometry("1200x700")

        # Logger
        self.logger = get_logger()
        self.logger.info("Janela de logs aberta")

        # Variáveis de controle
        self.auto_refresh_var = ctk.BooleanVar(value=False)
        self.filter_var = ctk.StringVar(value="ALL")
        self.num_lines_var = ctk.IntVar(value=500)

        # ID do timer de auto-refresh
        self.refresh_timer = None

        # Configura grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._create_widgets()
        self._load_logs()

    def _create_widgets(self):
        """Cria widgets da janela"""
        self._create_toolbar()
        self._create_log_area()
        self._create_status_bar()

    def _create_toolbar(self):
        """Cria barra de ferramentas"""
        toolbar = ctk.CTkFrame(self)
        toolbar.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        # Título
        ctk.CTkLabel(
            toolbar,
            text="📋 Logs da Aplicação",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left", padx=(10, 20))

        # Filtro por nível
        ctk.CTkLabel(
            toolbar,
            text="Nível:",
            font=ctk.CTkFont(weight="bold")
        ).pack(side="left", padx=(0, 5))

        filter_menu = ctk.CTkOptionMenu(
            toolbar,
            values=["ALL", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            variable=self.filter_var,
            command=self._on_filter_change,
            width=120
        )
        filter_menu.pack(side="left", padx=5)

        # Número de linhas
        ctk.CTkLabel(
            toolbar,
            text="Linhas:",
            font=ctk.CTkFont(weight="bold")
        ).pack(side="left", padx=(20, 5))

        lines_menu = ctk.CTkOptionMenu(
            toolbar,
            values=["100", "500", "1000", "5000", "Todas"],
            command=self._on_lines_change,
            width=100
        )
        lines_menu.set("500")
        lines_menu.pack(side="left", padx=5)

        # Botão de refresh
        refresh_btn = ctk.CTkButton(
            toolbar,
            text="🔄 Atualizar",
            command=self._load_logs,
            width=100,
            fg_color=("#3b82f6", "#2563eb"),
            hover_color=("#2563eb", "#1d4ed8")
        )
        refresh_btn.pack(side="left", padx=(20, 5))

        # Auto-refresh
        auto_refresh_cb = ctk.CTkCheckBox(
            toolbar,
            text="Auto-refresh (5s)",
            variable=self.auto_refresh_var,
            command=self._toggle_auto_refresh
        )
        auto_refresh_cb.pack(side="left", padx=10)

        # Botão de limpar
        clear_btn = ctk.CTkButton(
            toolbar,
            text="🗑️ Limpar",
            command=self._clear_display,
            width=100,
            fg_color="gray40",
            hover_color="gray30"
        )
        clear_btn.pack(side="left", padx=5)

        # Botão de exportar
        export_btn = ctk.CTkButton(
            toolbar,
            text="💾 Exportar",
            command=self._export_logs,
            width=100,
            fg_color=("#10b981", "#059669"),
            hover_color=("#059669", "#047857")
        )
        export_btn.pack(side="left", padx=5)

        # Botão de abrir arquivo
        open_btn = ctk.CTkButton(
            toolbar,
            text="📂 Abrir Arquivo",
            command=self._open_log_file,
            width=120
        )
        open_btn.pack(side="left", padx=5)

    def _create_log_area(self):
        """Cria área de exibição de logs"""
        log_frame = ctk.CTkFrame(self)
        log_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        log_frame.grid_rowconfigure(0, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)

        # Textbox para logs
        self.log_text = ctk.CTkTextbox(
            log_frame,
            wrap="none",
            font=ctk.CTkFont(family="Consolas", size=10)
        )
        self.log_text.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Configurar tags de cores para níveis
        self.log_text.tag_config("DEBUG", foreground="#888888")
        self.log_text.tag_config("INFO", foreground="#3b82f6")
        self.log_text.tag_config("WARNING", foreground="#f59e0b")
        self.log_text.tag_config("ERROR", foreground="#ef4444")
        self.log_text.tag_config("CRITICAL", foreground="#dc2626", background="#fee2e2")

    def _create_status_bar(self):
        """Cria barra de status"""
        status_frame = ctk.CTkFrame(self)
        status_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))

        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Pronto",
            font=ctk.CTkFont(size=10)
        )
        self.status_label.pack(side="left", padx=10, pady=5)

        self.line_count_label = ctk.CTkLabel(
            status_frame,
            text="0 linhas",
            font=ctk.CTkFont(size=10)
        )
        self.line_count_label.pack(side="right", padx=10, pady=5)

    def _load_logs(self):
        """Carrega e exibe logs"""
        try:
            self.status_label.configure(text="Carregando logs...")
            self.update()

            log_file = self.logger.get_log_file_path()

            if not log_file.exists():
                self.log_text.delete("1.0", "end")
                self.log_text.insert("1.0", "Nenhum log encontrado.\n\nO arquivo de log será criado quando a aplicação gerar eventos.")
                self.status_label.configure(text="Nenhum log encontrado")
                self.line_count_label.configure(text="0 linhas")
                return

            # Lê arquivo de log
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Limita número de linhas se necessário
            num_lines = self.num_lines_var.get()
            if num_lines > 0 and len(lines) > num_lines:
                lines = lines[-num_lines:]

            # Filtra por nível se necessário
            filter_level = self.filter_var.get()
            if filter_level != "ALL":
                lines = [line for line in lines if f"| {filter_level} " in line]

            # Limpa e exibe
            self.log_text.delete("1.0", "end")

            for line in lines:
                # Detecta nível do log para colorir
                level = self._detect_log_level(line)
                if level:
                    self.log_text.insert("end", line, level)
                else:
                    self.log_text.insert("end", line)

            # Scroll para o final
            self.log_text.see("end")

            # Atualiza status
            self.status_label.configure(text=f"Logs carregados de: {log_file.name}")
            self.line_count_label.configure(text=f"{len(lines)} linhas")

            self.logger.debug(f"Logs carregados: {len(lines)} linhas")

        except Exception as e:
            self.logger.exception("Erro ao carregar logs")
            messagebox.showerror("Erro", f"Erro ao carregar logs:\n{e}")
            self.status_label.configure(text="Erro ao carregar logs")

    def _detect_log_level(self, line: str) -> str:
        """Detecta o nível de log de uma linha"""
        if "| DEBUG " in line:
            return "DEBUG"
        elif "| INFO " in line:
            return "INFO"
        elif "| WARNING " in line:
            return "WARNING"
        elif "| ERROR " in line:
            return "ERROR"
        elif "| CRITICAL " in line:
            return "CRITICAL"
        return None

    def _on_filter_change(self, value):
        """Handler para mudança de filtro"""
        self._load_logs()

    def _on_lines_change(self, value):
        """Handler para mudança de número de linhas"""
        if value == "Todas":
            self.num_lines_var.set(-1)
        else:
            self.num_lines_var.set(int(value))
        self._load_logs()

    def _toggle_auto_refresh(self):
        """Ativa/desativa auto-refresh"""
        if self.auto_refresh_var.get():
            self._schedule_refresh()
            self.logger.debug("Auto-refresh ativado")
        else:
            if self.refresh_timer:
                self.after_cancel(self.refresh_timer)
                self.refresh_timer = None
            self.logger.debug("Auto-refresh desativado")

    def _schedule_refresh(self):
        """Agenda próximo refresh"""
        if self.auto_refresh_var.get():
            self._load_logs()
            self.refresh_timer = self.after(5000, self._schedule_refresh)  # 5 segundos

    def _clear_display(self):
        """Limpa a exibição (não deleta o arquivo)"""
        self.log_text.delete("1.0", "end")
        self.status_label.configure(text="Exibição limpa")
        self.line_count_label.configure(text="0 linhas")

    def _export_logs(self):
        """Exporta logs para arquivo"""
        try:
            filepath = filedialog.asksaveasfilename(
                defaultextension=".log",
                filetypes=[("Log files", "*.log"), ("Text files", "*.txt"), ("All files", "*.*")],
                initialfile=f"graph_analyzer_logs_{Path(self.logger.get_log_file_path()).stem}.log"
            )

            if filepath:
                content = self.log_text.get("1.0", "end-1c")
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)

                messagebox.showinfo("Sucesso", f"Logs exportados para:\n{filepath}")
                self.logger.info(f"Logs exportados para: {filepath}")

        except Exception as e:
            self.logger.exception("Erro ao exportar logs")
            messagebox.showerror("Erro", f"Erro ao exportar logs:\n{e}")

    def _open_log_file(self):
        """Abre o arquivo de log no editor padrão do sistema"""
        try:
            log_file = self.logger.get_log_file_path()

            if not log_file.exists():
                messagebox.showwarning(
                    "Aviso",
                    "Arquivo de log ainda não foi criado.\n\n"
                    "O arquivo será criado quando a aplicação gerar eventos."
                )
                return

            # Abre arquivo no sistema operacional
            import subprocess
            import platform

            system = platform.system()
            if system == "Windows":
                os.startfile(log_file)
            elif system == "Darwin":  # macOS
                subprocess.run(["open", log_file])
            else:  # Linux
                subprocess.run(["xdg-open", log_file])

            self.logger.info(f"Arquivo de log aberto: {log_file}")

        except Exception as e:
            self.logger.exception("Erro ao abrir arquivo de log")
            messagebox.showerror("Erro", f"Erro ao abrir arquivo:\n{e}")

    def destroy(self):
        """Cleanup ao fechar a janela"""
        # Cancela auto-refresh se ativo
        if self.refresh_timer:
            self.after_cancel(self.refresh_timer)

        self.logger.info("Janela de logs fechada")
        super().destroy()
