"""
Vista de Pago a Barberos.
Muestra cuanto ha ganado cada empleado en un periodo
para poder generar el pago correspondiente.
Solo el administrador puede ver esta pantalla.
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


class PagoBarberoView(ctk.CTkFrame):
    def __init__(self, parent, usuario: dict):
        super().__init__(parent, fg_color="#111111")
        self._usuario = usuario
        self._construir()

    def _construir(self):
        # ── Titulo ────────────────────────────────────────────────────────
        ctk.CTkLabel(
            self, text="Pago a Barberos",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=TEXT_WHITE,
        ).pack(pady=(16, 4), padx=16, anchor="w")

        ctk.CTkLabel(
            self,
            text="Consulte las ganancias de cada barbero por periodo para generar su pago.",
            font=ctk.CTkFont(size=13),
            text_color=TEXT_GRAY,
        ).pack(padx=16, anchor="w")

        # ── Filtro de fechas para seleccionar el periodo ───────────────────
        tarjeta_filtro = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=12)
        tarjeta_filtro.pack(fill="x", padx=16, pady=14)

        ctk.CTkLabel(
            tarjeta_filtro, text="Seleccionar periodo",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=GOLD,
        ).pack(anchor="w", padx=16, pady=(12, 8))

        # Fila con los campos de fecha y el boton consultar
        fila = ctk.CTkFrame(tarjeta_filtro, fg_color="transparent")
        fila.pack(fill="x", padx=16, pady=(0, 14))

        ctk.CTkLabel(fila, text="Desde:", text_color=TEXT_GRAY).pack(side="left", padx=(0, 4))
        self.entry_desde = ctk.CTkEntry(
            fila, placeholder_text="YYYY-MM-DD",
            fg_color=FIELD_BG, border_color="#333333",
            text_color=TEXT_WHITE, height=40, width=140,
        )
        self.entry_desde.pack(side="left", padx=(0, 12))

        ctk.CTkLabel(fila, text="Hasta:", text_color=TEXT_GRAY).pack(side="left", padx=(0, 4))
        self.entry_hasta = ctk.CTkEntry(
            fila, placeholder_text="YYYY-MM-DD",
            fg_color=FIELD_BG, border_color="#333333",
            text_color=TEXT_WHITE, height=40, width=140,
        )
        self.entry_hasta.pack(side="left", padx=(0, 12))

        # Boton para ejecutar la consulta — el controlador le asigna el comando
        self.btn_consultar = ctk.CTkButton(
            fila, text="Consultar",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=GOLD, hover_color=GOLD_HOVER,
            text_color="#111111", height=40, corner_radius=8,
        )
        self.btn_consultar.pack(side="left")

        # ── Resumen del total a pagar ──────────────────────────────────────
        # Lo actualiza el controlador con el periodo y el total sumado
        self.lbl_resumen = ctk.CTkLabel(
            self, text="",
            font=ctk.CTkFont(size=14),
            text_color=VERDE,
        )
        self.lbl_resumen.pack(padx=16, pady=(0, 6), anchor="w")

        # ── Tabla con ganancias detalladas por empleado ───────────────────
        tarjeta2 = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=12)
        tarjeta2.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        ctk.CTkLabel(
            tarjeta2, text="Ganancias por barbero",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=GOLD,
        ).pack(anchor="w", padx=16, pady=(12, 4))

        # Textbox monoespaciado para alinear las columnas de la tabla
        self.tabla = ctk.CTkTextbox(
            tarjeta2, state="disabled",
            fg_color=FIELD_BG, text_color=TEXT_WHITE,
            font=ctk.CTkFont(size=12, family="Courier"),
        )
        self.tabla.pack(fill="both", expand=True, padx=16, pady=(0, 14))

    def cargar_ganancias(self, datos):
        """Llena la tabla con las ganancias de cada empleado en el periodo."""
        self.tabla.configure(state="normal")
        self.tabla.delete("1.0", "end")

        if not datos:
            self.tabla.insert("end", "No hay datos para el periodo seleccionado.")
        else:
            # Encabezado de la tabla
            encabezado = (
                f"{'EMPLEADO':<22} {'ESPECIALIDAD':<20} "
                f"{'CITAS':>6} {'FACTURADO':>12} {'GANANCIA':>12}\n"
            )
            self.tabla.insert("end", encabezado)
            self.tabla.insert("end", "-" * 76 + "\n")

            total_pagos = 0

            for empleado in datos:
                ganancia  = empleado.get("total_empleado", 0) or 0
                facturado = empleado.get("total_facturado", 0) or 0
                citas     = empleado.get("total_citas", 0) or 0
                total_pagos += ganancia

                linea = (
                    f"{empleado.get('nombre_empleado',''):<22} "
                    f"{empleado.get('especialidad',''):<20} "
                    f"{citas:>6} "
                    f"${facturado:>10,.0f} "
                    f"${ganancia:>10,.0f}\n"
                )
                self.tabla.insert("end", linea)

            # Linea de totales al final — muestra cuanto hay que pagarle a todos
            self.tabla.insert("end", "-" * 76 + "\n")
            self.tabla.insert("end",
                f"{'TOTAL A PAGAR':>60} ${total_pagos:>10,.0f}\n")

        self.tabla.configure(state="disabled")

    def mostrar_resumen(self, texto):
        """Muestra el texto de resumen del periodo consultado."""
        self.lbl_resumen.configure(text=texto)
