"""
Helper para diálogos e mensagens
"""

from tkinter import messagebox
from typing import Callable, Optional


class DialogHelper:
    """Helper para diálogos padronizados"""

    @staticmethod
    def show_error(title: str, message: str):
        """Mostra erro"""
        messagebox.showerror(title, message)

    @staticmethod
    def show_success(title: str, message: str):
        """Mostra sucesso"""
        messagebox.showinfo(title, message)

    @staticmethod
    def show_warning(title: str, message: str):
        """Mostra aviso"""
        messagebox.showwarning(title, message)

    @staticmethod
    def confirm(title: str, message: str) -> bool:
        """
        Pede confirmação.

        Returns:
            True se usuário confirmou
        """
        return messagebox.askyesno(title, message)

    @staticmethod
    def confirm_deletion(what: str, details: str = "") -> bool:
        """
        Confirmação de deleção.

        Args:
            what: O que será deletado
            details: Detalhes adicionais

        Returns:
            True se confirmado
        """
        message = f"Deseja realmente deletar {what}?\n\n"
        if details:
            message += f"{details}\n\n"
        message += "Esta ação não pode ser desfeita!"

        return messagebox.askyesno("Confirmar Deleção", message, icon='warning')
