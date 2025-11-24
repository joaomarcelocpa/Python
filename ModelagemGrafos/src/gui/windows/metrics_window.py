"""
Janela de Análise de Métricas de Grafos
"""

import os
import threading
import customtkinter as ctk
from tkinter import messagebox, filedialog
from pathlib import Path
from datetime import datetime

import config
from src.gexf_reader import GEXFReader
from src.utils.graph_metrics_analyzer import GraphMetricsAnalyzer
from src.utils.logger import get_logger


class MetricsWindow(ctk.CTkToplevel):
    """
    Janela para análise de métricas de grafos GEXF.

    Responsabilidades:
    - Seleção de grafo
    - Análise de métricas (centralidade, comunidades, estrutura)
    - Exibição de resultados
    - Exportação de relatórios
    """

    def __init__(self, parent):
        """
        Inicializa janela de métricas.

        Args:
            parent: Widget pai
        """
        super().__init__(parent)

        self.title("📈 Análise de Métricas • Graph Analyzer")
        self.geometry("1200x700")
        self.minsize(1000, 600)

        # Logger
        self.logger = get_logger()
        self.logger.info("Janela de métricas aberta")

        # Configura grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Estado
        self.is_analyzing = False
        self.current_results = None
        self.current_analyzer = None

        # Variáveis de controle
        self.graph_var = ctk.StringVar(value="graph_1_comments")

        self._create_widgets()

    def _create_widgets(self):
        """Cria widgets da janela"""
        self._create_control_panel()
        self._create_results_area()

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
            text="📊 Análise de Métricas",
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color=("#2563eb", "#60a5fa")
        ).pack(pady=(20, 25))

        # Seleção de grafo
        self._create_graph_selection()

        # Botões de ação
        self._create_action_buttons()

        # Informações
        self._create_info_section()

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

    def _create_action_buttons(self):
        """Cria botões de ação"""
        # Botão de analisar
        analyze_btn = ctk.CTkButton(
            self.control_panel,
            text="🔍 Analisar Métricas",
            command=self.analyze_graph,
            height=46,
            corner_radius=12,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color=("#3b82f6", "#2563eb"),
            hover_color=("#2563eb", "#1d4ed8")
        )
        analyze_btn.pack(pady=25, padx=20, fill="x")

        # Botão de exportar
        export_btn = ctk.CTkButton(
            self.control_panel,
            text="💾 Exportar Relatórios",
            command=self.export_reports,
            height=38,
            corner_radius=10,
            font=ctk.CTkFont(size=13),
            fg_color=("#10b981", "#059669"),
            hover_color=("#059669", "#047857")
        )
        export_btn.pack(pady=10, padx=20, fill="x")

    def _create_info_section(self):
        """Cria seção de informações"""
        info_frame = ctk.CTkFrame(self.control_panel)
        info_frame.pack(fill="x", padx=10, pady=20)

        ctk.CTkLabel(
            info_frame,
            text="ℹ️ Informações",
            font=ctk.CTkFont(weight="bold")
        ).pack(pady=5)

        info_text = ctk.CTkTextbox(
            info_frame,
            height=200,
            font=ctk.CTkFont(family="Consolas", size=10),
            wrap="word"
        )
        info_text.pack(fill="both", expand=True, padx=5, pady=5)
        info_text.insert("1.0",
            "Métricas Calculadas:\n\n"
            "• Centralidade:\n"
            "  - Degree\n"
            "  - Betweenness\n"
            "  - Closeness\n"
            "  - PageRank\n\n"
            "• Estrutura:\n"
            "  - Densidade\n"
            "  - Clustering\n"
            "  - Assortatividade\n"
            "  - Caminho médio\n\n"
            "• Comunidades:\n"
            "  - Detecção\n"
            "  - Modularidade\n"
            "  - Bridging ties"
        )
        info_text.configure(state="disabled")

    def _create_results_area(self):
        """Cria área de resultados"""
        self.results_frame = ctk.CTkFrame(self)
        self.results_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.results_frame.grid_rowconfigure(0, weight=1)
        self.results_frame.grid_columnconfigure(0, weight=1)

        # Notebook para abas
        self.notebook = ctk.CTkTabview(self.results_frame)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Cria abas
        self.notebook.add("Resumo")
        self.notebook.add("Centralidade")
        self.notebook.add("Estrutura")
        self.notebook.add("Comunidades")

        # Instrução inicial
        self.initial_label = ctk.CTkLabel(
            self.notebook.tab("Resumo"),
            text="Selecione um grafo e clique em 'Analisar Métricas'",
            font=ctk.CTkFont(size=16)
        )
        self.initial_label.pack(pady=50)

    def analyze_graph(self):
        """Analisa métricas do grafo selecionado"""
        if self.is_analyzing:
            messagebox.showwarning(
                "Aviso",
                "Aguarde a análise atual terminar!"
            )
            return

        graph_name = self.graph_var.get()

        # Caminho do arquivo GEXF
        gephi_dir = os.path.join(config.OUTPUT_DIR, "gephi")
        gexf_file = os.path.join(gephi_dir, f"{graph_name}.gexf")

        if not os.path.exists(gexf_file):
            messagebox.showerror(
                "Erro",
                f"Arquivo não encontrado:\n{gexf_file}\n\nGere os grafos primeiro!"
            )
            return

        # Inicia análise em thread separada
        self.is_analyzing = True
        thread = threading.Thread(
            target=self._analyze_thread,
            args=(gexf_file, graph_name),
            daemon=True
        )
        thread.start()

    def _analyze_thread(self, gexf_file, graph_name):
        """Executa análise em thread separada"""
        try:
            self.logger.info(f"Iniciando análise de métricas: {graph_name}")

            # Mostra progresso
            self.after(0, lambda: self._show_progress("Carregando grafo..."))

            # Carrega grafo
            reader = GEXFReader(gexf_file)
            graph = reader.to_graph()

            self.logger.info(f"Grafo carregado: {graph.num_vertices} vértices, {graph.num_edges} arestas")

            # Cria analisador
            self.after(0, lambda: self._show_progress("Analisando métricas..."))
            analyzer = GraphMetricsAnalyzer(graph)

            # Executa análise completa
            results = analyzer.analyze_all()

            self.logger.info("Análise concluída")

            # Armazena resultados
            self.current_results = results
            self.current_analyzer = analyzer

            # Atualiza interface na thread principal
            self.after(0, lambda: self._display_results(results, analyzer))

        except Exception as e:
            self.logger.exception(f"Erro ao analisar grafo '{graph_name}'")
            error_msg = str(e)
            self.after(0, lambda: messagebox.showerror(
                "Erro na Análise",
                f"Erro ao analisar grafo:\n\n{error_msg}"
            ))
        finally:
            self.is_analyzing = False

    def _show_progress(self, message: str):
        """Mostra mensagem de progresso"""
        if hasattr(self, 'initial_label') and self.initial_label.winfo_exists():
            self.initial_label.configure(text=message)

    def _display_results(self, results, analyzer):
        """Exibe resultados na interface"""
        # Remove label inicial se existir
        if hasattr(self, 'initial_label') and self.initial_label.winfo_exists():
            self.initial_label.destroy()

        # Limpa abas anteriores
        self._clear_tabs()

        # Preenche cada aba
        self._fill_summary_tab(results)
        self._fill_centrality_tab(results, analyzer)
        self._fill_structure_tab(results)
        self._fill_communities_tab(results, analyzer)

        messagebox.showinfo("Sucesso", "Análise de métricas concluída!")

    def _clear_tabs(self):
        """Limpa conteúdo das abas"""
        for tab_name in ["Resumo", "Centralidade", "Estrutura", "Comunidades"]:
            tab = self.notebook.tab(tab_name)
            for widget in tab.winfo_children():
                widget.destroy()

    def _fill_summary_tab(self, results):
        """Preenche aba de resumo"""
        tab = self.notebook.tab("Resumo")

        textbox = ctk.CTkTextbox(tab, font=ctk.CTkFont(family="Consolas", size=11))
        textbox.pack(fill="both", expand=True, padx=10, pady=10)

        # Monta resumo
        summary = "=" * 80 + "\n"
        summary += "RESUMO DA ANÁLISE DE MÉTRICAS\n"
        summary += "=" * 80 + "\n\n"

        summary += "INFORMAÇÕES BÁSICAS\n"
        summary += "-" * 80 + "\n"
        summary += f"Vértices: {results['basic_info']['num_vertices']:,}\n"
        summary += f"Arestas: {results['basic_info']['num_edges']:,}\n"
        summary += f"Densidade: {results['basic_info']['density']:.4f}\n"
        summary += f"Reciprocidade: {results['structure']['reciprocity']:.4f}\n\n"

        summary += "ESTRUTURA\n"
        summary += "-" * 80 + "\n"
        summary += f"Coeficiente de Clustering: {results['structure']['clustering_average']:.4f}\n"
        summary += f"Assortatividade: {results['structure']['assortativity']:.4f}\n"
        summary += f"Caminho Médio: {results['structure']['average_path_length']:.2f}\n"
        summary += f"Diâmetro: {results['structure']['diameter']}\n\n"

        summary += "COMUNIDADES\n"
        summary += "-" * 80 + "\n"
        summary += f"Número de comunidades: {results['community']['num_communities']}\n"
        summary += f"Modularidade: {results['community']['modularity']:.4f}\n"
        summary += f"Método: {results['community']['method']}\n\n"

        textbox.insert("1.0", summary)
        textbox.configure(state="disabled")

    def _fill_centrality_tab(self, results, analyzer):
        """Preenche aba de centralidade"""
        tab = self.notebook.tab("Centralidade")

        textbox = ctk.CTkTextbox(tab, font=ctk.CTkFont(family="Consolas", size=10))
        textbox.pack(fill="both", expand=True, padx=10, pady=10)

        content = "TOP 15 COLABORADORES POR MÉTRICA DE CENTRALIDADE\n"
        content += "=" * 80 + "\n\n"

        metrics = [
            ('pagerank', 'PageRank (Influência)'),
            ('betweenness', 'Betweenness (Pontes)'),
            ('degree_total', 'Degree (Atividade)'),
            ('closeness', 'Closeness (Proximidade)')
        ]

        for metric, metric_name in metrics:
            content += f"\n{metric_name}:\n"
            content += "-" * 80 + "\n"

            top = analyzer.get_top_central_nodes(metric, 15)
            for i, (vertex, score, label) in enumerate(top, 1):
                content += f"  {i:2d}. {label:40s} {score:8.4f}\n"

        textbox.insert("1.0", content)
        textbox.configure(state="disabled")

    def _fill_structure_tab(self, results):
        """Preenche aba de estrutura"""
        tab = self.notebook.tab("Estrutura")

        textbox = ctk.CTkTextbox(tab, font=ctk.CTkFont(family="Consolas", size=11))
        textbox.pack(fill="both", expand=True, padx=10, pady=10)

        content = "MÉTRICAS DE ESTRUTURA DA REDE\n"
        content += "=" * 80 + "\n\n"

        basic_info = results['basic_info']
        structure = results['structure']

        content += "Métricas Básicas:\n"
        content += "-" * 80 + "\n"
        content += f"Número de vértices: {basic_info['num_vertices']:,}\n"
        content += f"Número de arestas: {basic_info['num_edges']:,}\n"
        content += f"Densidade: {basic_info['density']:.6f}\n"
        content += f"Reciprocidade: {structure['reciprocity']:.4f}\n\n"

        content += "Métricas de Coesão:\n"
        content += "-" * 80 + "\n"
        content += f"Coeficiente de Clustering (médio): {structure['clustering_average']:.4f}\n"
        content += f"Coeficiente de Clustering (global): {structure['clustering_global']:.4f}\n\n"

        content += "Métricas de Distância:\n"
        content += "-" * 80 + "\n"
        content += f"Caminho médio: {structure['average_path_length']:.2f}\n"
        content += f"Diâmetro: {structure['diameter']}\n\n"

        content += "Outras Métricas:\n"
        content += "-" * 80 + "\n"
        content += f"Assortatividade: {structure['assortativity']:.4f}\n\n"

        content += "INTERPRETAÇÃO:\n"
        content += "-" * 80 + "\n"

        density = structure['density']
        if density > 0.5:
            content += "• Rede MUITO COLABORATIVA (densidade alta)\n"
        elif density > 0.3:
            content += "• Rede COLABORATIVA (densidade moderada)\n"
        else:
            content += "• Rede POUCO CONECTADA (densidade baixa)\n"

        clustering = structure['clustering_average']
        if clustering > 0.6:
            content += "• FORTE formação de grupos coesos\n"
        elif clustering > 0.4:
            content += "• MODERADA formação de grupos\n"
        else:
            content += "• FRACA formação de grupos\n"

        assortativity = structure['assortativity']
        if assortativity > 0.1:
            content += "• Rede CENTRALIZADA (hubs conectados entre si)\n"
        elif assortativity < -0.1:
            content += "• Rede DESCENTRALIZADA (hubs conectam periféricos)\n"
        else:
            content += "• Rede com estrutura EQUILIBRADA\n"

        textbox.insert("1.0", content)
        textbox.configure(state="disabled")

    def _fill_communities_tab(self, results, analyzer):
        """Preenche aba de comunidades"""
        tab = self.notebook.tab("Comunidades")

        textbox = ctk.CTkTextbox(tab, font=ctk.CTkFont(family="Consolas", size=10))
        textbox.pack(fill="both", expand=True, padx=10, pady=10)

        content = "ANÁLISE DE COMUNIDADES\n"
        content += "=" * 80 + "\n\n"

        comm_data = results['community']

        content += f"Número de comunidades detectadas: {comm_data['num_communities']}\n"
        content += f"Modularidade: {comm_data['modularity']:.4f}\n"
        content += f"Método: {comm_data['method']}\n\n"

        # Interpretação da modularidade
        modularity = comm_data['modularity']
        if modularity > 0.4:
            content += "Comunidades MUITO BEM DEFINIDAS\n\n"
        elif modularity > 0.2:
            content += "Comunidades MODERADAMENTE DEFINIDAS\n\n"
        else:
            content += "Comunidades FRACAMENTE DEFINIDAS\n\n"

        # Top bridging ties
        content += "TOP 20 CONECTORES ENTRE COMUNIDADES (Bridging Ties):\n"
        content += "-" * 80 + "\n"

        bridging = comm_data['bridging_ties']
        sorted_bridging = sorted(bridging.items(), key=lambda x: x[1], reverse=True)

        communities = comm_data['communities']
        for i, (vertex, score) in enumerate(sorted_bridging[:20], 1):
            label = analyzer.graph.get_vertex_label(vertex) or f"V{vertex}"
            comm = communities.get(vertex, -1)
            content += f"  {i:2d}. {label:40s} Score: {score:.4f} (Com. {comm})\n"

        # Estatísticas por comunidade
        content += "\n\nESTATÍSTICAS POR COMUNIDADE:\n"
        content += "-" * 80 + "\n"

        comm_stats = comm_data['community_statistics']
        for comm_id in sorted(comm_stats.keys())[:10]:  # Mostra até 10 comunidades
            stats = comm_stats[comm_id]
            content += f"\nComunidade {comm_id}:\n"
            content += f"  Tamanho: {stats['size']} membros\n"
            content += f"  Arestas internas: {stats['internal_edges']}\n"
            content += f"  Arestas externas: {stats['external_edges']}\n"
            if stats['size'] > 1:
                density = stats['internal_edges'] / (stats['size'] * (stats['size'] - 1))
                content += f"  Densidade interna: {density:.4f}\n"

        textbox.insert("1.0", content)
        textbox.configure(state="disabled")

    def export_reports(self):
        """Exporta relatórios de métricas"""
        if self.current_results is None or self.current_analyzer is None:
            messagebox.showwarning(
                "Aviso",
                "Execute a análise primeiro!"
            )
            return

        # Seleciona diretório de saída
        output_dir = filedialog.askdirectory(
            title="Selecione o diretório para salvar os relatórios"
        )

        if not output_dir:
            return

        try:
            output_path = Path(output_dir)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Exporta JSON
            json_file = output_path / f"metrics_{timestamp}.json"
            self.current_analyzer.export_to_json(str(json_file), self.current_results)

            # Exporta relatório textual
            report = self.current_analyzer.generate_report(self.current_results)
            report_file = output_path / f"report_{timestamp}.txt"

            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)

            messagebox.showinfo(
                "Sucesso",
                f"Relatórios exportados com sucesso!\n\n"
                f"JSON: {json_file.name}\n"
                f"Relatório: {report_file.name}\n\n"
                f"Diretório: {output_dir}"
            )

            self.logger.info(f"Relatórios exportados para: {output_dir}")

        except Exception as e:
            self.logger.exception("Erro ao exportar relatórios")
            messagebox.showerror(
                "Erro",
                f"Erro ao exportar relatórios:\n\n{e}"
            )
