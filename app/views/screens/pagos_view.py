"""
Vista de Pagos.
La recepcionista registra el pago de una cita.
El administrador solo puede ver el historial (no puede registrar).
Al registrar el pago se calcula automaticamente la ganancia
del empleado y del negocio.
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


class PagosView(ctk.CTkFrame):
    def __init__(self, parent, usuario: dict):
        super().__init__(parent, fg_color="#111111")
        self._usuario = usuario
        self._rol = usuario.get("rol", "")
        self._construir()

    def _construir(self):
        # ── Titulo ────────────────────────────────────────────────────────
        ctk.CTkLabel(
            self, text="Registro de Pagos",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=TEXT_WHITE,
        ).pack(pady=(16, 4), padx=16, anchor="w")

        ctk.CTkLabel(
            self,
            text="Registra el pago de una cita. Se calcula la ganancia automaticamente.",
            font=ctk.CTkFont(size=13),
            text_color=TEXT_GRAY,
        ).pack(padx=16, anchor="w")

        # ── Formulario de registro (solo visible para la recepcionista) ────
        tarjeta = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=12)
        tarjeta.pack(fill="x", padx=16, pady=14)

        # Solo la recepcionista puede registrar — el admin ve solo el historial
        if self._rol != "administrador":
            ctk.CTkLabel(
                tarjeta, text="Registrar pago",
                font=ctk.CTkFont(size=15, weight="bold"),
                text_color=GOLD,
            ).pack(anchor="w", padx=16, pady=(12, 8))

            # Tres campos en una sola fila
            fila = ctk.CTkFrame(tarjeta, fg_color="transparent")
            fila.pack(fill="x", padx=16, pady=(0, 10))
            fila.columnconfigure(0, weight=1)
            fila.columnconfigure(1, weight=1)
            fila.columnconfigure(2, weight=1)

            # Columna 1: Codigo de la cita a pagar
            c1 = ctk.CTkFrame(fila, fg_color="transparent")
            c1.grid(row=0, column=0, padx=(0, 8), sticky="nsew")
            ctk.CTkLabel(c1, text="Código de la cita",
                         text_color=TEXT_GRAY, font=ctk.CTkFont(size=11)).pack(anchor="w")
            self.entry_codigo = ctk.CTkEntry(
                c1, placeholder_text="Ej. A1B2C3D4",
                fg_color=FIELD_BG, border_color="#333333",
                text_color=TEXT_WHITE, height=40,
            )
            self.entry_codigo.pack(fill="x", pady=(2, 0))

            # Columna 2: Monto del pago
            c2 = ctk.CTkFrame(fila, fg_color="transparent")
            c2.grid(row=0, column=1, padx=8, sticky="nsew")
            ctk.CTkLabel(c2, text="Monto ($)",
                         text_color=TEXT_GRAY, font=ctk.CTkFont(size=11)).pack(anchor="w")
            self.entry_monto = ctk.CTkEntry(
                c2, placeholder_text="Ej. 35000",
                fg_color=FIELD_BG, border_color="#333333",
                text_color=TEXT_WHITE, height=40,
            )
            self.entry_monto.pack(fill="x", pady=(2, 0))

            # Columna 3: Metodo de pago
            c3 = ctk.CTkFrame(fila, fg_color="transparent")
            c3.grid(row=0, column=2, padx=(8, 0), sticky="nsew")
            ctk.CTkLabel(c3, text="Método de pago",
                         text_color=TEXT_GRAY, font=ctk.CTkFont(size=11)).pack(anchor="w")
            self.opt_metodo = ctk.CTkOptionMenu(
                c3, values=["efectivo", "transferencia", "tarjeta", "otro"],
                fg_color=FIELD_BG, button_color="#333333",
                button_hover_color="#3E3E3E",
                text_color=TEXT_WHITE, height=40,
            )
            self.opt_metodo.pack(fill="x", pady=(2, 0))

            # Boton registrar — el controlador le asigna el comando
            self.btn_registrar = ctk.CTkButton(
                tarjeta, text="Registrar Pago",
                font=ctk.CTkFont(size=13, weight="bold"),
                fg_color=GOLD, hover_color=GOLD_HOVER,
                text_color="#111111", height=44, corner_radius=8,
            )
            self.btn_registrar.pack(anchor="w", padx=16, pady=(8, 6))

            # Desglose de ganancias — se llena despues de registrar el pago exitosamente
            self.lbl_desglose = ctk.CTkLabel(
                tarjeta, text="",
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=VERDE,
            )
            self.lbl_desglose.pack(padx=16, pady=(0, 14))

        else:
            # Para el admin solo muestro un aviso de que esta en modo lectura
            ctk.CTkLabel(
                tarjeta,
                text="ℹ  Vista de solo lectura — el administrador no registra pagos.",
                text_color=TEXT_GRAY,
                font=ctk.CTkFont(size=13),
            ).pack(padx=16, pady=20)

        # ── Historial de pagos del mes actual ─────────────────────────────
        tarjeta2 = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=12)
        tarjeta2.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        ctk.CTkLabel(
            tarjeta2, text="Historial de pagos del mes",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=GOLD,
        ).pack(anchor="w", padx=16, pady=(12, 4))

        # Textbox monoespaciado para alinear las columnas de la tabla
        self.tabla_pagos = ctk.CTkTextbox(
            tarjeta2, state="disabled",
            fg_color=FIELD_BG, text_color=TEXT_WHITE,
            font=ctk.CTkFont(size=12, family="Courier"),
        )
        self.tabla_pagos.pack(fill="both", expand=True, padx=16, pady=(0, 14))

    def mostrar_desglose(self, empleado, negocio, numero_factura=None):
        """Muestra la distribucion de ganancias y el número de factura generado."""
        if hasattr(self, "lbl_desglose"):
            factura_txt = f"   |   Factura: {numero_factura}" if numero_factura else ""
            self.lbl_desglose.configure(
                text=f"Pago registrado  —  Barbero: ${empleado:,.0f}   |   Negocio: ${negocio:,.0f}{factura_txt}"
            )

    def mostrar_historial(self, pagos):
        """Llena la tabla con el historial de pagos del mes."""
        self.tabla_pagos.configure(state="normal")
        self.tabla_pagos.delete("1.0", "end")

        if not pagos:
            self.tabla_pagos.insert("end", "No hay pagos registrados este mes.")
        else:
            # Encabezado de la tabla
            encabezado = f"{'ID':<6} {'FECHA':<12} {'MONTO':>10} {'MÉTODO':<14} {'ESTADO':<10}\n"
            self.tabla_pagos.insert("end", encabezado)
            self.tabla_pagos.insert("end", "-" * 55 + "\n")

            # Acumulo el total para mostrarlo al final
            total = 0
            for p in pagos:
                monto = p.get("monto", 0) or 0
                total += monto
                linea = (
                    f"{p.get('id',''):<6} "
                    f"{p.get('fecha',''):<12} "
                    f"${monto:>8,.0f} "
                    f"{p.get('metodo',''):<14} "
                    f"{p.get('estado',''):<10}\n"
                )
                self.tabla_pagos.insert("end", linea)

            # Fila de totales
            self.tabla_pagos.insert("end", "-" * 55 + "\n")
            self.tabla_pagos.insert("end", f"{'TOTAL':>30} ${total:>8,.0f}\n")

        self.tabla_pagos.configure(state="disabled")
