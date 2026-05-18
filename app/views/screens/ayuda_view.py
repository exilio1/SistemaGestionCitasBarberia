"""
Vista de Ayuda y Preguntas Frecuentes.
Se usa para cumplir con RNF01: ayuda contextual y FAQ.
"""

import customtkinter as ctk

GOLD = "#C9A020"
BG = "#111111"
CARD = "#1A1A1A"
TEXT_W = "#F0F0F0"
TEXT_G = "#777777"


class AyudaView(ctk.CTkFrame):
    def __init__(self, parent, usuario: dict):
        super().__init__(parent, fg_color=BG)
        self._usuario = usuario
        self._construir()

    def _construir(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(expand=True, fill="both", padx=20, pady=16)

        ctk.CTkLabel(
            scroll, text="AYUDA Y PREGUNTAS FRECUENTES",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=TEXT_W,
        ).pack(anchor="w")

        ctk.CTkLabel(
            scroll,
            text="Aquí puedes consultar guías rápidas para usar el sistema.",
            font=ctk.CTkFont(size=13),
            text_color=TEXT_G,
        ).pack(anchor="w", pady=(2, 16))

        ayudas = [
            (
                "¿Cómo registro una cita?",
                "Ve al módulo Agenda o Citas, llena los datos del cliente, "
                "selecciona barbero, servicio, fecha y hora, y luego guarda.",
            ),
            (
                "¿Cómo confirmo o cancelo una cita?",
                "En Citas puedes usar el código de la cita para confirmarla, "
                "reprogramarla o cancelarla.",
            ),
            (
                "¿Cómo registro un pago?",
                "En Facturación escribe el código de la cita, el monto y el método "
                "de pago. El sistema calcula la ganancia y genera la factura.",
            ),
            (
                "¿Cómo veo la rentabilidad?",
                "En Reportes puedes filtrar por fechas para ver ingresos, "
                "citas, ganancia del negocio y rendimiento por barbero.",
            ),
            (
                "¿Cómo se hacen los respaldos?",
                "El sistema crea un respaldo automático de la base de datos al iniciar "
                "la aplicación, guardándolo en la carpeta data/backups.",
            ),
        ]

        for titulo, texto in ayudas:
            tarjeta = ctk.CTkFrame(scroll, fg_color=CARD, corner_radius=12)
            tarjeta.pack(fill="x", pady=(0, 12))

            ctk.CTkLabel(
                tarjeta, text=titulo,
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=GOLD,
                wraplength=780, justify="left",
            ).pack(anchor="w", padx=16, pady=(12, 6))

            ctk.CTkLabel(
                tarjeta, text=texto,
                font=ctk.CTkFont(size=12),
                text_color=TEXT_W,
                wraplength=780, justify="left",
            ).pack(anchor="w", padx=16, pady=(0, 12))
