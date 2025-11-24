"""
Redirecionador de texto para widgets CustomTkinter
"""


class TextRedirector:
    """Redireciona print() para widget de texto"""

    def __init__(self, text_widget):
        """
        Inicializa redirecionador.

        Args:
            text_widget: Widget CTkTextbox para redirecionar output
        """
        self.text_widget = text_widget

    def write(self, text):
        """Escreve texto no widget"""
        if text.strip():  # Ignora strings vazias
            self.text_widget.configure(state="normal")
            self.text_widget.insert("end", text)
            self.text_widget.see("end")
            self.text_widget.configure(state="disabled")
            self.text_widget.update()

    def flush(self):
        """Flush (compatibilidade com sys.stdout)"""
        pass
