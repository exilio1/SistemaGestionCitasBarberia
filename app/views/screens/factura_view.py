"""
Vista de Facturas.
Permite generar facturas de los pagos y consultar las facturas existentes.
"""

import customtkinter as ctk

# Colores de la aplicacion
GOLD        = "#C9A020"
GOLD_HOVER  = "#A8841A"
BG_CARD     = "#1C1C1C"
FIELD_BG    = "#252525"
TEXT_GRAY   = "#888888"
TEXT_WHITE  = "#F0F0F0"
VERDE       = "#27AE60"
ROJO        = "#E74C3C"


class FacturaView(ctk.CTkFrame):
    def __init__(self, parent, usuario: dict):
        super().__init__(parent, fg_color="#111111")
        self._usuario = usuario
        self._construir()

    def _construir(self):
        # ── Titulo de la pantalla ─────────────────────────────────────────
        ctk.CTkLabel(
            self, text="Generar Factura",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=TEXT_WHITE,
        ).pack(pady=(16, 4), padx=16, anchor="w")

        ctk.CTkLabel(
            self,
            text="Ingrese el código de pago para generar la factura del servicio.",
            font=ctk.CTkFont(size=13),
            text_color=TEXT_GRAY,
        ).pack(padx=16, anchor="w")

        # ── Formulario para generar factura ───────────────────────────────
        tarjeta = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=12)
        tarjeta.pack(fill="x", padx=16, pady=14)

        ctk.CTkLabel(
            tarjeta, text="Datos para la factura",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=GOLD,
        ).pack(anchor="w", padx=16, pady=(12, 8))

        # Campo: ID del pago — necesario para buscar el pago en la BD
        ctk.CTkLabel(
            tarjeta, text="ID del pago",
            text_color=TEXT_GRAY, font=ctk.CTkFont(size=11),
        ).pack(anchor="w", padx=16)
        self.entry_pago_id = ctk.CTkEntry(
            tarjeta, placeholder_text="Ej. 1, 2, 3...",
            fg_color=FIELD_BG, border_color="#333333",
            text_color=TEXT_WHITE, height=40, width=300,
        )
        self.entry_pago_id.pack(anchor="w", padx=16, pady=(2, 10))

        # Campo: Detalle adicional — texto libre que se agrega a la factura
        ctk.CTkLabel(
            tarjeta, text="Detalle adicional (opcional)",
            text_color=TEXT_GRAY, font=ctk.CTkFont(size=11),
        ).pack(anchor="w", padx=16)
        self.entry_detalle = ctk.CTkEntry(
            tarjeta, placeholder_text="Ej. Corte + barba incluida",
            fg_color=FIELD_BG, border_color="#333333",
            text_color=TEXT_WHITE, height=40, width=400,
        )
        self.entry_detalle.pack(anchor="w", padx=16, pady=(2, 10))

        # Boton para generar la factura — lo conecta el controlador
        self.btn_generar = ctk.CTkButton(
            tarjeta, text="Generar Factura",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=GOLD, hover_color=GOLD_HOVER,
            text_color="#111111", height=44, corner_radius=8,
        )
        self.btn_generar.pack(anchor="w", padx=16, pady=(4, 14))

        # Label de resultado — muestra el numero de factura generada o el error
        self.lbl_resultado = ctk.CTkLabel(
            tarjeta, text="",
            font=ctk.CTkFont(size=13),
            text_color=VERDE,
        )
        self.lbl_resultado.pack(padx=16, pady=(0, 10))

        # ── Lista de facturas ya generadas ────────────────────────────────
        tarjeta2 = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=12)
        tarjeta2.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        ctk.CTkLabel(
            tarjeta2, text="Facturas generadas",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=GOLD,
        ).pack(anchor="w", padx=16, pady=(12, 4))

        # Textbox con fuente monoespaciada para mantener la tabla alineada
        self.tabla_facturas = ctk.CTkTextbox(
            tarjeta2, state="disabled",
            fg_color=FIELD_BG, text_color=TEXT_WHITE,
            font=ctk.CTkFont(size=12, family="Courier"),
        )
        self.tabla_facturas.pack(fill="both", expand=True, padx=16, pady=(0, 14))

    def mostrar_resultado(self, mensaje, error=False):
        """Muestra un mensaje de exito o error debajo del boton."""
        color = ROJO if error else VERDE
        self.lbl_resultado.configure(text=mensaje, text_color=color)

    def cargar_facturas(self, facturas):
        """Llena la tabla con el historial de facturas generadas."""
        self.tabla_facturas.configure(state="normal")
        self.tabla_facturas.delete("1.0", "end")

        if not facturas:
            self.tabla_facturas.insert("end", "No hay facturas generadas todavía.")
        else:
            # Encabezado de la tabla con columnas alineadas
            encabezado = f"{'N° FACTURA':<20} {'FECHA':<12} {'CLIENTE':<20} {'SERVICIO':<20} {'MONTO':>10}\n"
            self.tabla_facturas.insert("end", encabezado)
            self.tabla_facturas.insert("end", "-" * 85 + "\n")

            for f in facturas:
                linea = (
                    f"{f.get('numero_factura',''):<20} "
                    f"{f.get('fecha_emision',''):<12} "
                    f"{f.get('nombre_cliente',''):<20} "
                    f"{f.get('servicio',''):<20} "
                    f"${f.get('monto',0):>9,.0f}\n"
                )
                self.tabla_facturas.insert("end", linea)

        self.tabla_facturas.configure(state="disabled")
