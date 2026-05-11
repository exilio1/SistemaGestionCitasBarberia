"""
Tooltip sencillo para mostrar ayudas cortas sobre botones o campos.
"""

import customtkinter as ctk


class ToolTip:
    def __init__(self, widget, texto):
        self.widget = widget
        self.texto = texto
        self._ventana = None
        widget.bind("<Enter>", self._mostrar)
        widget.bind("<Leave>", self._ocultar)

    def _mostrar(self, _event=None):
        if self._ventana:
            return

        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 6

        self._ventana = ctk.CTkToplevel(self.widget)
        self._ventana.wm_overrideredirect(True)
        self._ventana.geometry(f"+{x}+{y}")
        self._ventana.attributes("-topmost", True)

        label = ctk.CTkLabel(
            self._ventana,
            text=self.texto,
            fg_color="#1F1F1F",
            text_color="#F0F0F0",
            corner_radius=6,
            padx=10,
            pady=6,
        )
        label.pack()

    def _ocultar(self, _event=None):
        if self._ventana:
            self._ventana.destroy()
            self._ventana = None
