"""
Vista de Gastos.
Permite registrar y ver los gastos del negocio como arriendo,
servicios publicos, insumos, etc.
"""

import customtkinter as ctk

# Colores de la aplicacion
GOLD       = "#C9A020"
GOLD_HOVER = "#A8841A"
BG_CARD    = "#1C1C1C"
FIELD_BG   = "#252525"
TEXT_GRAY  = "#888888"
TEXT_WHITE = "#F0F0F0"
VERDE      = "#27AE60"


class GastosView(ctk.CTkFrame):
    def __init__(self, parent, usuario: dict):
        super().__init__(parent, fg_color="#111111")
        self._usuario = usuario
        self._construir()

    def _construir(self):
        # ── Titulo ────────────────────────────────────────────────────────
        ctk.CTkLabel(
            self, text="Registro de Gastos",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=TEXT_WHITE,
        ).pack(pady=(16, 4), padx=16, anchor="w")

        ctk.CTkLabel(
            self,
            text="Registra los gastos del negocio para calcular la rentabilidad.",
            font=ctk.CTkFont(size=13),
            text_color=TEXT_GRAY,
        ).pack(padx=16, anchor="w")

        # ── Formulario para registrar un gasto nuevo ───────────────────────
        tarjeta = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=12)
        tarjeta.pack(fill="x", padx=16, pady=14)

        ctk.CTkLabel(
            tarjeta, text="Nuevo gasto",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=GOLD,
        ).pack(anchor="w", padx=16, pady=(12, 8))

        # Fila 1: Descripcion (ancha) y categoria (mas estrecha)
        fila1 = ctk.CTkFrame(tarjeta, fg_color="transparent")
        fila1.pack(fill="x", padx=16, pady=(0, 8))
        fila1.columnconfigure(0, weight=2)   # descripcion ocupa mas espacio
        fila1.columnconfigure(1, weight=1)

        col_izq = ctk.CTkFrame(fila1, fg_color="transparent")
        col_izq.grid(row=0, column=0, padx=(0, 8), sticky="nsew")

        ctk.CTkLabel(col_izq, text="Descripcion del gasto",
                     text_color=TEXT_GRAY, font=ctk.CTkFont(size=11)).pack(anchor="w")
        self.entry_descripcion = ctk.CTkEntry(
            col_izq, placeholder_text="Ej. Arriendo del local",
            fg_color=FIELD_BG, border_color="#333333",
            text_color=TEXT_WHITE, height=40,
        )
        self.entry_descripcion.pack(fill="x", pady=(2, 0))

        col_der = ctk.CTkFrame(fila1, fg_color="transparent")
        col_der.grid(row=0, column=1, padx=(8, 0), sticky="nsew")

        ctk.CTkLabel(col_der, text="Categoría",
                     text_color=TEXT_GRAY, font=ctk.CTkFont(size=11)).pack(anchor="w")
        # Desplegable con las categorias predefinidas del negocio
        self.opt_categoria = ctk.CTkOptionMenu(
            col_der,
            values=["arriendo", "servicios", "insumos", "nomina", "otros"],
            fg_color=FIELD_BG, button_color="#333333",
            button_hover_color="#3E3E3E",
            text_color=TEXT_WHITE, height=40,
        )
        self.opt_categoria.pack(fill="x", pady=(2, 0))

        # Fila 2: Monto y Fecha
        fila2 = ctk.CTkFrame(tarjeta, fg_color="transparent")
        fila2.pack(fill="x", padx=16, pady=(8, 10))
        fila2.columnconfigure(0, weight=1)
        fila2.columnconfigure(1, weight=1)

        col_m = ctk.CTkFrame(fila2, fg_color="transparent")
        col_m.grid(row=0, column=0, padx=(0, 8), sticky="nsew")

        ctk.CTkLabel(col_m, text="Monto ($)",
                     text_color=TEXT_GRAY, font=ctk.CTkFont(size=11)).pack(anchor="w")
        self.entry_monto = ctk.CTkEntry(
            col_m, placeholder_text="Ej. 500000",
            fg_color=FIELD_BG, border_color="#333333",
            text_color=TEXT_WHITE, height=40,
        )
        self.entry_monto.pack(fill="x", pady=(2, 0))

        col_f = ctk.CTkFrame(fila2, fg_color="transparent")
        col_f.grid(row=0, column=1, padx=(8, 0), sticky="nsew")

        # Si el usuario deja la fecha vacia, el controlador usa la fecha de hoy
        ctk.CTkLabel(col_f, text="Fecha (dejar vacío = hoy)",
                     text_color=TEXT_GRAY, font=ctk.CTkFont(size=11)).pack(anchor="w")
        self.entry_fecha = ctk.CTkEntry(
            col_f, placeholder_text="YYYY-MM-DD",
            fg_color=FIELD_BG, border_color="#333333",
            text_color=TEXT_WHITE, height=40,
        )
        self.entry_fecha.pack(fill="x", pady=(2, 0))

        # Boton registrar — el controlador le asigna el comando
        self.btn_registrar = ctk.CTkButton(
            tarjeta, text="Registrar Gasto",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=GOLD, hover_color=GOLD_HOVER,
            text_color="#111111", height=44, corner_radius=8,
        )
        self.btn_registrar.pack(anchor="w", padx=16, pady=(0, 14))

        # ── Tabla con los gastos del mes actual ───────────────────────────
        tarjeta2 = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=12)
        tarjeta2.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        ctk.CTkLabel(
            tarjeta2, text="Gastos del mes actual",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=GOLD,
        ).pack(anchor="w", padx=16, pady=(12, 4))

        # Textbox monoespaciado para alinear las columnas
        self.tabla = ctk.CTkTextbox(
            tarjeta2, state="disabled",
            fg_color=FIELD_BG, text_color=TEXT_WHITE,
            font=ctk.CTkFont(size=12, family="Courier"),
        )
        self.tabla.pack(fill="both", expand=True, padx=16, pady=(0, 14))

    def cargar_gastos(self, gastos):
        """Llena la tabla con los gastos del mes recibidos del modelo."""
        self.tabla.configure(state="normal")
        self.tabla.delete("1.0", "end")

        if not gastos:
            self.tabla.insert("end", "No hay gastos registrados este mes.")
        else:
            # Encabezado con columnas alineadas
            encabezado = f"{'FECHA':<12} {'CATEGORÍA':<14} {'DESCRIPCIÓN':<30} {'MONTO':>12}\n"
            self.tabla.insert("end", encabezado)
            self.tabla.insert("end", "-" * 70 + "\n")

            # Acumulo el total para mostrarlo al final
            total = 0
            for g in gastos:
                monto = g.get("monto", 0) or 0
                total += monto
                linea = (
                    f"{g.get('fecha_gasto',''):<12} "
                    f"{g.get('categoria',''):<14} "
                    f"{g.get('descripcion',''):<30} "
                    f"${monto:>10,.0f}\n"
                )
                self.tabla.insert("end", linea)

            # Fila de total al final de la tabla
            self.tabla.insert("end", "-" * 70 + "\n")
            self.tabla.insert("end", f"{'TOTAL':>58} ${total:>10,.0f}\n")

        self.tabla.configure(state="disabled")
