"""
Janela de Visualização de Grafos
"""

import os
import time
import threading
import customtkinter as ctk
from tkinter import messagebox, filedialog
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

import config
from src.gexf_visualizer import GEXFVisualizer
from src.utils.logger import get_logger


class VisualizationWindow(ctk.CTkToplevel):
    """
    Janela para visualização de grafos GEXF.

    Responsabilidades:
    - Seleção de grafo
    - Configuração de layout
    - Renderização com matplotlib
    - Exportação de imagens
    - Exibição de estatísticas
    """

    def __init__(self, parent):
        """
        Inicializa janela de visualização.

        Args:
            parent: Widget pai
        """
        super().__init__(parent)

        self.title("📊 Visualização de Grafos • Graph Analyzer")
        self.geometry("1200x700")
        self.minsize(1000, 600)  # Tamanho mínimo para manter usabilidade

        # Logger
        self.logger = get_logger()
        self.logger.info("Janela de visualização aberta")

        # Configura grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Variáveis matplotlib
        self.current_fig = None
        self.current_canvas = None
        self.current_toolbar = None

        # Variáveis de controle
        self.graph_var = ctk.StringVar(value="graph_1_comments")
        self.layout_var = ctk.StringVar(value="random")
        self.show_labels_var = ctk.BooleanVar(value=True)
        self.show_weights_var = ctk.BooleanVar(value=False)

        # Estado de processamento
        self.is_drawing = False
        self.cancel_drawing = False

        self._create_widgets()
        self._create_progress_indicator()

    def _create_widgets(self):
        """Cria widgets da janela"""
        self._create_control_panel()
        self._create_canvas_area()

    def _create_control_panel(self):
        """Cria painel lateral de controles"""
        self.control_panel = ctk.CTkScrollableFrame(
            self,
            width=320,
            fg_color=("#f0f0f0", "#1a1a1a")
        )
        self.control_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Título
        ctk.CTkLabel(
            self.control_panel,
            text="🎨 Controles de Visualização",
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color=("#2563eb", "#60a5fa")
        ).pack(pady=(20, 25))

        # Seleção de grafo
        self._create_graph_selection()

        # Layout
        self._create_layout_selection()

        # Opções de visualização
        self._create_visualization_options()

        # Estatísticas
        self._create_stats_area()

        # Botões de ação
        self._create_action_buttons()

    def _create_graph_selection(self):
        """Cria seção de seleção de grafo"""
        ctk.CTkLabel(
            self.control_panel,
            text="Selecione o Grafo:",
            font=ctk.CTkFont(weight="bold")
        ).pack(pady=(10, 5))

        graphs = [
            ("Grafo 1: Comentários", "graph_1_comments"),
            ("Grafo 2: Fechamentos", "graph_2_closures"),
            ("Grafo 3: Reviews/Merges", "graph_3_reviews"),
            ("Grafo 4: Integrado", "graph_4_integrated")
        ]

        for label, value in graphs:
            ctk.CTkRadioButton(
                self.control_panel,
                text=label,
                variable=self.graph_var,
                value=value
            ).pack(pady=5, padx=20, anchor="w")

        # Separador
        ctk.CTkLabel(self.control_panel, text="").pack(pady=5)

    def _create_layout_selection(self):
        """Cria seção de seleção de layout"""
        ctk.CTkLabel(
            self.control_panel,
            text="Layout:",
            font=ctk.CTkFont(weight="bold")
        ).pack(pady=(10, 5))

        # Apenas layout aleatório disponível
        ctk.CTkLabel(
            self.control_panel,
            text="✓ Aleatório (com zoom e navegação)",
            font=ctk.CTkFont(size=12),
            text_color=("gray20", "gray80")
        ).pack(pady=5, padx=20, anchor="w")

        # Separador
        ctk.CTkLabel(self.control_panel, text="").pack(pady=5)

    def _create_visualization_options(self):
        """Cria seção de opções de visualização"""
        ctk.CTkLabel(
            self.control_panel,
            text="Opções:",
            font=ctk.CTkFont(weight="bold")
        ).pack(pady=(10, 5))

        ctk.CTkCheckBox(
            self.control_panel,
            text="Mostrar labels dos nós",
            variable=self.show_labels_var
        ).pack(pady=5, padx=20, anchor="w")

        ctk.CTkCheckBox(
            self.control_panel,
            text="Mostrar pesos das arestas",
            variable=self.show_weights_var
        ).pack(pady=5, padx=20, anchor="w")

    def _create_stats_area(self):
        """Cria área de estatísticas"""
        stats_frame = ctk.CTkFrame(self.control_panel)
        stats_frame.pack(fill="x", padx=10, pady=20)

        ctk.CTkLabel(
            stats_frame,
            text="Estatísticas",
            font=ctk.CTkFont(weight="bold")
        ).pack(pady=5)

        self.stats_text = ctk.CTkTextbox(
            stats_frame,
            height=150,
            font=ctk.CTkFont(family="Consolas", size=10)
        )
        self.stats_text.pack(fill="both", expand=True, padx=5, pady=5)
        self.stats_text.configure(state="disabled")

    def _create_action_buttons(self):
        """Cria botões de ação"""
        # Botão de visualizar
        visualize_btn = ctk.CTkButton(
            self.control_panel,
            text="🎨 Visualizar Grafo",
            command=self.draw_graph,
            height=46,
            corner_radius=12,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color=("#3b82f6", "#2563eb"),
            hover_color=("#2563eb", "#1d4ed8")
        )
        visualize_btn.pack(pady=25, padx=20, fill="x")

        # Botão de exportar
        export_btn = ctk.CTkButton(
            self.control_panel,
            text="💾 Exportar Imagem",
            command=self.export_image,
            height=38,
            corner_radius=10,
            font=ctk.CTkFont(size=13),
            fg_color=("#10b981", "#059669"),
            hover_color=("#059669", "#047857")
        )
        export_btn.pack(pady=10, padx=20, fill="x")

    def _create_canvas_area(self):
        """Cria área de canvas para matplotlib"""
        self.canvas_frame = ctk.CTkFrame(self)
        self.canvas_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.canvas_frame.grid_rowconfigure(0, weight=1)
        self.canvas_frame.grid_columnconfigure(0, weight=1)

        # Instrução inicial
        self.initial_label = ctk.CTkLabel(
            self.canvas_frame,
            text="Selecione um grafo e clique em 'Visualizar'",
            font=ctk.CTkFont(size=16)
        )
        self.initial_label.place(relx=0.5, rely=0.5, anchor="center")

    def _create_progress_indicator(self):
        """Cria indicador de progresso"""
        self.progress_frame = ctk.CTkFrame(self.canvas_frame)

        self.progress_label = ctk.CTkLabel(
            self.progress_frame,
            text="Carregando grafo...",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.progress_label.pack(pady=10)

        self.progress_detail = ctk.CTkLabel(
            self.progress_frame,
            text="",
            font=ctk.CTkFont(size=11)
        )
        self.progress_detail.pack(pady=5)

        self.progress_bar = ctk.CTkProgressBar(self.progress_frame, width=300)
        self.progress_bar.pack(pady=10)
        self.progress_bar.set(0)

        self.cancel_button = ctk.CTkButton(
            self.progress_frame,
            text="Cancelar",
            command=self._cancel_drawing,
            fg_color="red",
            hover_color="darkred"
        )
        self.cancel_button.pack(pady=10)

        # Inicialmente escondido
        self.progress_frame.place_forget()

    def _show_progress(self, message: str, detail: str = "", progress: float = 0.0):
        """Mostra indicador de progresso"""
        self.progress_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.progress_label.configure(text=message)
        self.progress_detail.configure(text=detail)
        self.progress_bar.set(progress)
        self.update()

    def _hide_progress(self):
        """Esconde indicador de progresso"""
        self.progress_frame.place_forget()
        self.update()

    def _cancel_drawing(self):
        """Cancela a renderização em andamento"""
        self.cancel_drawing = True
        self.logger.info("Cancelamento solicitado pelo usuário")
        self._hide_progress()

    def draw_graph(self):
        """Desenha grafo selecionado"""
        if self.is_drawing:
            self.logger.warning("Já existe uma renderização em andamento")
            messagebox.showwarning(
                "Aviso",
                "Aguarde a renderização atual terminar!"
            )
            return

        graph_name = self.graph_var.get()
        layout = self.layout_var.get()
        show_labels = self.show_labels_var.get()
        show_weights = self.show_weights_var.get()

        self.logger.info(f"Iniciando visualização: grafo={graph_name}, layout={layout}")

        # Caminho do arquivo GEXF
        gephi_dir = os.path.join(config.OUTPUT_DIR, "gephi")
        gexf_file = os.path.join(gephi_dir, f"{graph_name}.gexf")

        self.logger.debug(f"Verificando arquivo: {gexf_file}")

        if not os.path.exists(gexf_file):
            self.logger.error(f"Arquivo não encontrado: {gexf_file}")
            messagebox.showerror(
                "Erro",
                f"Arquivo não encontrado:\n{gexf_file}\n\nGere os grafos primeiro!"
            )
            return

        # Verifica tamanho do grafo antes de renderizar
        try:
            from src.gexf_reader import GEXFReader
            reader = GEXFReader(gexf_file)
            reader.parse()
            stats = reader.get_statistics()
            num_nodes = stats.get('num_nodes', 0)
            num_edges = stats.get('num_edges', 0)

            self.logger.info(f"Grafo selecionado: {num_nodes} nós, {num_edges} arestas")

            # Aviso para grafos grandes
            if num_nodes > 500 or num_edges > 2000:
                warning_msg = (
                    f"⚠️ AVISO: Grafo Grande Detectado\n\n"
                    f"Nós: {num_nodes:,}\n"
                    f"Arestas: {num_edges:,}\n\n"
                    f"A visualização pode demorar e consumir muita memória.\n\n"
                    f"Recomendações:\n"
                    f"• Desative 'Mostrar labels dos nós'\n"
                    f"• Desative 'Mostrar pesos das arestas'\n"
                    f"• Use os controles de zoom para navegar\n\n"
                    f"Deseja continuar mesmo assim?"
                )

                result = messagebox.askyesno(
                    "Grafo Grande - Confirmar Visualização",
                    warning_msg,
                    icon='warning'
                )

                if not result:
                    self.logger.info("Visualização cancelada pelo usuário (grafo grande)")
                    return

        except Exception as e:
            self.logger.warning(f"Não foi possível verificar tamanho do grafo: {e}")

        # Inicia renderização em thread separada
        self.cancel_drawing = False
        self.is_drawing = True

        # Mostra indicador de progresso
        self.after(0, lambda: self._show_progress("Preparando visualização...", "", 0.1))

        thread = threading.Thread(
            target=self._draw_graph_thread,
            args=(gexf_file, graph_name, layout, show_labels, show_weights),
            daemon=True
        )
        thread.start()
        self.logger.debug("Thread de renderização iniciada")

    def _draw_graph_thread(self, gexf_file, graph_name, layout, show_labels, show_weights):
        """Desenha o grafo em uma thread separada para não travar a GUI"""
        start_time = time.time()

        try:
            # Verifica cancelamento
            if self.cancel_drawing:
                self.logger.info("Renderização cancelada antes de iniciar")
                self.after(0, self._hide_progress)
                return

            self.logger.info(f"Carregando arquivo GEXF: {gexf_file}")
            self.after(0, lambda: self._show_progress("Carregando arquivo...", "", 0.2))

            # Remove label inicial se existir (deve ser feito na thread principal)
            if self.initial_label:
                self.after(0, lambda: self.initial_label.destroy() if self.initial_label else None)
                self.initial_label = None

            # Remove canvas anterior se existir (deve ser feito na thread principal)
            if self.current_canvas:
                self.after(0, lambda: self.current_canvas.get_tk_widget().destroy() if self.current_canvas else None)
            if self.current_toolbar:
                self.after(0, lambda: self.current_toolbar.destroy() if self.current_toolbar else None)

            # Verifica cancelamento
            if self.cancel_drawing:
                self.logger.info("Renderização cancelada após limpeza")
                self.after(0, self._hide_progress)
                return

            # Cria visualizador
            self.logger.debug("Criando GEXFVisualizer")
            self.after(0, lambda: self._show_progress("Inicializando visualizador...", "", 0.3))
            visualizer = GEXFVisualizer(gexf_file)

            # Verifica cancelamento
            if self.cancel_drawing:
                self.logger.info("Renderização cancelada após criar visualizador")
                self.after(0, self._hide_progress)
                return

            # Cria figura
            self.logger.debug("Criando figura matplotlib")
            self.after(0, lambda: self._show_progress("Criando figura...", "", 0.4))
            fig = Figure(figsize=(12, 10), dpi=100)
            ax = fig.add_subplot(111)

            # Verifica cancelamento
            if self.cancel_drawing:
                self.logger.info("Renderização cancelada antes de desenhar")
                self.after(0, self._hide_progress)
                return

            # Desenha grafo (operação pesada)
            self.logger.info("Desenhando grafo...")
            self.after(0, lambda: self._show_progress(
                "Desenhando grafo...",
                f"Layout: {layout.capitalize()}",
                0.5
            ))
            draw_start = time.time()

            visualizer.draw(
                fig=fig,
                ax=ax,
                layout=layout,
                show_labels=show_labels,
                show_weights=show_weights,
                node_size=300,
                font_size=8
            )

            # Verifica cancelamento
            if self.cancel_drawing:
                self.logger.info("Renderização cancelada após desenhar")
                self.after(0, self._hide_progress)
                return

            draw_elapsed = time.time() - draw_start
            self.logger.info(f"Desenho concluído em {draw_elapsed:.3f}s")

            # Cria canvas e toolbar na thread principal
            self.logger.debug("Criando canvas e toolbar")
            self.after(0, lambda: self._show_progress("Finalizando...", "", 0.9))
            self.after(0, lambda: self._finalize_drawing(fig, visualizer))

            total_elapsed = time.time() - start_time
            self.logger.info(f"Visualização completa em {total_elapsed:.3f}s")

            # Esconde progresso
            self.after(100, self._hide_progress)

        except FileNotFoundError as e:
            self.logger.error(f"Arquivo não encontrado: {e}")
            self.after(0, self._hide_progress)
            self.after(0, lambda: messagebox.showerror(
                "Erro",
                f"Arquivo não encontrado:\n{gexf_file}"
            ))
        except MemoryError as e:
            self.logger.error(f"Memória insuficiente: {e}")
            self.after(0, self._hide_progress)
            self.after(0, lambda: messagebox.showerror(
                "Erro de Memória",
                "Grafo muito grande para visualizar!\n\nTente:\n"
                "- Desabilitar labels e pesos\n"
                "- Fechar outras aplicações\n"
                "- Reduzir o tamanho do grafo"
            ))
        except Exception as e:
            self.logger.exception(f"Erro ao visualizar grafo '{graph_name}'")
            error_msg = str(e)
            self.after(0, self._hide_progress)
            self.after(0, lambda: messagebox.showerror(
                "Erro na Visualização",
                f"Erro ao visualizar grafo:\n\n{error_msg}\n\n"
                f"Verifique os logs em: logs/graph_analyzer.log"
            ))
        finally:
            self.is_drawing = False
            self.cancel_drawing = False
            self.logger.debug("Thread de renderização finalizada")

    def _finalize_drawing(self, fig, visualizer):
        """Finaliza o desenho na thread principal (para widgets Tkinter)"""
        try:
            # Cria toolbar frame primeiro (será empacotado no fundo)
            toolbar_frame = ctk.CTkFrame(self.canvas_frame, fg_color="transparent")
            toolbar_frame.pack(side="bottom", fill="x", pady=(0, 5))

            # Cria canvas (preenche o resto do espaço)
            canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(side="top", fill="both", expand=True)

            # Adiciona toolbar de navegação (zoom, pan, etc)
            toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
            toolbar.update()
            toolbar.pack(side="top", fill="x")

            # Adiciona dica sobre controles
            hint_label = ctk.CTkLabel(
                toolbar_frame,
                text="💡 Dica: Use o scroll do mouse para zoom | Clique nos botões da toolbar para Pan/Zoom/Home",
                font=ctk.CTkFont(size=10),
                text_color=("gray40", "gray60")
            )
            hint_label.pack(side="top", pady=2)

            self.current_fig = fig
            self.current_canvas = canvas
            self.current_toolbar = toolbar

            # Atualiza estatísticas
            self.update_stats(visualizer)

            self.logger.debug("Finalização do desenho concluída")

        except Exception as e:
            self.logger.exception("Erro ao finalizar desenho")
            messagebox.showerror("Erro", f"Erro ao finalizar visualização:\n{e}")

    def update_stats(self, visualizer):
        """
        Atualiza estatísticas do grafo.

        Args:
            visualizer: Instância de GEXFVisualizer
        """
        if visualizer:
            stats = visualizer.get_statistics()
            self.stats_text.configure(state="normal")
            self.stats_text.delete("1.0", "end")
            self.stats_text.insert("1.0", f"Nós: {stats.get('num_nodes', 0):,}\n")
            self.stats_text.insert("end", f"Arestas: {stats.get('num_edges', 0):,}\n")
            self.stats_text.insert("end", f"Densidade: {stats.get('density', 0):.4f}\n")
            if 'avg_degree' in stats:
                self.stats_text.insert("end", f"Grau médio: {stats['avg_degree']:.2f}\n")
                self.stats_text.insert("end", f"Grau máx: {stats['max_degree']}\n")
            self.stats_text.configure(state="disabled")

    def export_image(self):
        """Exporta visualização atual como imagem"""
        if self.current_fig:
            filepath = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG", "*.png"), ("PDF", "*.pdf"), ("SVG", "*.svg")]
            )
            if filepath:
                self.current_fig.savefig(filepath, dpi=300, bbox_inches='tight')
                messagebox.showinfo("Sucesso", f"Imagem salva em:\n{filepath}")
