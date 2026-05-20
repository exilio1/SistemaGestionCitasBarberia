"""
Vista de Facturacion — Pantalla unificada de pagos y facturas.
Muestra el historial de pagos, permite registrar pagos (recepcionista)
y generar facturas para los pagos realizados.
"""

import customtkinter as ctk
from datetime import date
from app.views.components.tooltip import ToolTip
from app.views.components.calendario import CalendarioPopup, formatear_fecha_es, formatear_fecha_larga_es

# ── Colores ───────────────────────────────────────────────────────────────────
GOLD       = "#C9A020"
GOLD_HOVER = "#A8841A"
BG         = "#111111"
CARD       = "#1A1A1A"
CARD2      = "#1F1F1F"
BORDER     = "#2A2A2A"
TEXT_W     = "#F0F0F0"
TEXT_G     = "#777777"
VERDE      = "#27AE60"
VERDE_DIM  = "#1A4A2A"
AZUL       = "#3A8FD4"
ROJO       = "#C0392B"


class FacturacionView(ctk.CTkFrame):
    """Pantalla de Facturacion: registro de pagos + historial + facturas."""

    def __init__(self, parent, usuario: dict):
        super().__init__(parent, fg_color=BG)
        self._usuario = usuario
        self._rol     = usuario.get("rol", "recepcionista")
        self._construir()

    def _construir(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(expand=True, fill="both", padx=20, pady=16)

        # ── Encabezado ────────────────────────────────────────────────────
        ctk.CTkLabel(
            scroll, text="FACTURACION",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=TEXT_W,
        ).pack(anchor="w")

        ctk.CTkLabel(
            scroll,
            text="Registro de pagos y generación de facturas.",
            font=ctk.CTkFont(size=13),
            text_color=TEXT_G,
        ).pack(anchor="w", pady=(2, 16))

        # ── Tarjetas de resumen (KPIs) ────────────────────────────────────
        # Tres KPIs: ingresos de hoy, del mes y citas pendientes
        fila_kpis = ctk.CTkFrame(scroll, fg_color="transparent")
        fila_kpis.pack(fill="x", pady=(0, 16))
        for i in range(3):
            fila_kpis.columnconfigure(i, weight=1)

        # Guardo referencias a los labels de valor para actualizarlos desde el controlador
        self._lbl_hoy  = self._kpi_card(fila_kpis, "", "HOY",           GOLD,  col=0)
        self._lbl_mes  = self._kpi_card(fila_kpis, "", "ESTE MES",       VERDE, col=1)
        self._lbl_pend = self._kpi_card(fila_kpis, "", "CITAS PENDIENTES", AZUL, col=2)

        # ── Servicios finalizados sin cobrar ──────────────────────────────
        # Muestra las citas con estado 'completada' que aún no tienen pago.
        # El botón "Cobrar" rellena el formulario automáticamente.
        panel_sinc = ctk.CTkFrame(scroll, fg_color=CARD, corner_radius=12)
        panel_sinc.pack(fill="x", pady=(0, 14))

        hdr_sinc = ctk.CTkFrame(panel_sinc, fg_color="transparent")
        hdr_sinc.pack(fill="x", padx=16, pady=(12, 4))

        ctk.CTkLabel(
            hdr_sinc,
            text="Servicios finalizados sin cobrar",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=TEXT_W,
        ).pack(side="left")

        # Badge que muestra cuántas citas están pendientes de cobro
        self._lbl_sinc_badge = ctk.CTkLabel(
            hdr_sinc, text="",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#2A2A2A", corner_radius=8,
            text_color=TEXT_G,
        )
        self._lbl_sinc_badge.pack(side="left", padx=(10, 0), ipadx=10, ipady=3)

        ctk.CTkLabel(
            panel_sinc,
            text="Haz clic en 'Cobrar' para rellenar el formulario con los datos de esa cita.",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_G,
        ).pack(anchor="w", padx=16, pady=(0, 8))

        # Lista scrollable con las citas pendientes de cobro
        self._frame_sinc = ctk.CTkScrollableFrame(
            panel_sinc,
            fg_color="transparent",
            height=160,
            scrollbar_button_color="#333333",
            scrollbar_button_hover_color="#444444",
        )
        self._frame_sinc.pack(fill="x", padx=16, pady=(0, 12))

        # Mensaje inicial antes de que el controlador cargue los datos
        ctk.CTkLabel(
            self._frame_sinc,
            text="Cargando...",
            font=ctk.CTkFont(size=11), text_color=TEXT_G,
        ).pack(pady=10)

        # ── Formulario de registro de pago (solo para la recepcionista) ───
        if self._rol == "recepcionista":
            panel_form = ctk.CTkFrame(scroll, fg_color=CARD, corner_radius=12)
            panel_form.pack(fill="x", pady=(0, 14))

            ctk.CTkLabel(
                panel_form, text="Registrar Pago",
                font=ctk.CTkFont(size=15, weight="bold"),
                text_color=GOLD,
            ).pack(anchor="w", padx=16, pady=(12, 8))

            fila_f = ctk.CTkFrame(panel_form, fg_color="transparent")
            fila_f.pack(fill="x", padx=16, pady=(0, 8))
            for i in range(3):
                fila_f.columnconfigure(i, weight=1)

            # Campos del formulario de pago en tres columnas
            # Columna 0: Codigo de cita
            self._label_col(fila_f, "CÓDIGO DE CITA", col=0, row=0)
            self.entry_codigo = self._entry_col(fila_f, "Ej. AB12CD34", col=0, row=1)

            # Columna 1: Monto del pago
            self._label_col(fila_f, "MONTO ($)", col=1, row=0)
            self.entry_monto = self._entry_col(fila_f, "Ej. 35000", col=1, row=1)

            # Columna 2: Metodo de pago
            self._label_col(fila_f, "MÉTODO DE PAGO", col=2, row=0)
            self.opt_metodo = ctk.CTkOptionMenu(
                fila_f,
                values=["efectivo", "transferencia", "tarjeta", "otro"],
                fg_color=CARD2, button_color="#333333",
                button_hover_color="#444444",
                text_color=TEXT_W,
                font=ctk.CTkFont(size=13),
                dropdown_fg_color=CARD,
                dropdown_hover_color="#333333",
                dropdown_text_color=TEXT_W,
            )
            self.opt_metodo.grid(row=1, column=2, sticky="ew", padx=(6, 0))
            self.opt_metodo.set("efectivo")

            # Boton para registrar el pago
            self.btn_registrar = ctk.CTkButton(
                panel_form, text="REGISTRAR PAGO",
                font=ctk.CTkFont(size=13, weight="bold"),
                fg_color=VERDE, hover_color="#1E8A4A",
                text_color=TEXT_W, height=42, corner_radius=8,
            )
            self.btn_registrar.pack(anchor="w", padx=16, pady=(0, 14))
            self._tt_registrar = ToolTip(
                self.btn_registrar,
                "Registra el pago y genera la factura automática.",
            )

            # Mensaje de resultado del registro
            self.lbl_msg_pago = ctk.CTkLabel(
                panel_form, text="",
                font=ctk.CTkFont(size=12), text_color=VERDE,
            )
            self.lbl_msg_pago.pack(anchor="w", padx=16, pady=(0, 8))

        # ── Historial de pagos con filtro de fechas ───────────────────────
        panel_hist = ctk.CTkFrame(scroll, fg_color=CARD, corner_radius=12)
        panel_hist.pack(fill="both", expand=True, pady=(0, 14))

        fila_hist_h = ctk.CTkFrame(panel_hist, fg_color="transparent")
        fila_hist_h.pack(fill="x", padx=16, pady=(12, 8))

        ctk.CTkLabel(
            fila_hist_h, text="Historial de Pagos",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=TEXT_W,
        ).pack(side="left")

        # Filtros rapidos de fecha para el historial
        ctk.CTkLabel(
            fila_hist_h, text="Desde:",
            font=ctk.CTkFont(size=11), text_color=TEXT_G,
        ).pack(side="left", padx=(20, 4))
        self.entry_desde = ctk.CTkEntry(
            fila_hist_h, width=110, height=30,
            fg_color=CARD2, border_color=BORDER,
            text_color=TEXT_W, font=ctk.CTkFont(size=12),
            placeholder_text="AAAA-MM-DD",
        )
        self.entry_desde.pack(side="left")
        self.btn_cal_desde = ctk.CTkButton(
            fila_hist_h, text="Cal", width=38, height=30,
            fg_color="#2A2A2A", hover_color="#333333", text_color=TEXT_W,
            command=lambda: self._abrir_calendario("desde"),
        )
        self.btn_cal_desde.pack(side="left", padx=(4, 0))

        ctk.CTkLabel(
            fila_hist_h, text="Hasta:",
            font=ctk.CTkFont(size=11), text_color=TEXT_G,
        ).pack(side="left", padx=(8, 4))
        self.entry_hasta = ctk.CTkEntry(
            fila_hist_h, width=110, height=30,
            fg_color=CARD2, border_color=BORDER,
            text_color=TEXT_W, font=ctk.CTkFont(size=12),
            placeholder_text="AAAA-MM-DD",
        )
        self.entry_hasta.pack(side="left")
        self.btn_cal_hasta = ctk.CTkButton(
            fila_hist_h, text="Cal", width=38, height=30,
            fg_color="#2A2A2A", hover_color="#333333", text_color=TEXT_W,
            command=lambda: self._abrir_calendario("hasta"),
        )
        self.btn_cal_hasta.pack(side="left", padx=(4, 0))

        # Boton para aplicar el filtro de fechas
        self.btn_filtrar = ctk.CTkButton(
            fila_hist_h, text="Filtrar",
            font=ctk.CTkFont(size=11),
            fg_color="#2A2A2A", hover_color="#333333",
            text_color=TEXT_G, width=70, height=30,
        )
        self.btn_filtrar.pack(side="left", padx=8)

        self.lbl_rango = ctk.CTkLabel(
            panel_hist, text="",
            font=ctk.CTkFont(size=12), text_color=TEXT_G,
        )
        self.lbl_rango.pack(anchor="w", padx=16, pady=(0, 8))

        # Tabla de pagos con fuente monoespaciada para alinear columnas
        self.tabla_pagos = ctk.CTkTextbox(
            panel_hist,
            state="disabled",
            fg_color=CARD2,
            border_color=BORDER, border_width=1,
            text_color=TEXT_W,
            font=ctk.CTkFont(size=11, family="Courier"),
            height=220,
        )
        self.tabla_pagos.pack(fill="both", expand=True, padx=16, pady=(0, 14))

        # ── Panel para generar facturas ───────────────────────────────────
        panel_fac = ctk.CTkFrame(scroll, fg_color=CARD, corner_radius=12)
        panel_fac.pack(fill="x", pady=(0, 14))

        ctk.CTkLabel(
            panel_fac, text="Generar Factura",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=GOLD,
        ).pack(anchor="w", padx=16, pady=(12, 8))

        fila_fac = ctk.CTkFrame(panel_fac, fg_color="transparent")
        fila_fac.pack(fill="x", padx=16, pady=(0, 8))
        fila_fac.columnconfigure(0, weight=1)
        fila_fac.columnconfigure(1, weight=2)

        # Campos para generar la factura: ID del pago y detalle adicional
        self._label_col(fila_fac, "ID DEL PAGO", col=0, row=0)
        self.entry_pago_id = self._entry_col(fila_fac, "Ej. 1", col=0, row=1)

        self._label_col(fila_fac, "DETALLE ADICIONAL (opcional)", col=1, row=0)
        self.entry_detalle = self._entry_col(fila_fac, "Ej. Descuento aplicado", col=1, row=1)

        # Boton para generar la factura
        self.btn_generar_factura = ctk.CTkButton(
            panel_fac, text="GENERAR FACTURA",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=GOLD, hover_color=GOLD_HOVER,
            text_color="#0D0D0D", height=42, corner_radius=8,
        )
        self.btn_generar_factura.pack(anchor="w", padx=16, pady=(0, 14))
        self._tt_factura = ToolTip(
            self.btn_generar_factura,
            "Usa este botón solo si necesitas generar una factura manual.",
        )

        # Mensaje resultado de la generacion de factura
        self.lbl_msg_factura = ctk.CTkLabel(
            panel_fac, text="",
            font=ctk.CTkFont(size=12), text_color=VERDE,
        )
        self.lbl_msg_factura.pack(anchor="w", padx=16, pady=(0, 8))

        # Tabla con las facturas ya emitidas
        ctk.CTkLabel(
            panel_fac, text="Facturas emitidas",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=TEXT_G,
        ).pack(anchor="w", padx=16, pady=(4, 4))

        self.tabla_facturas = ctk.CTkTextbox(
            panel_fac,
            state="disabled",
            fg_color=CARD2,
            border_color=BORDER, border_width=1,
            text_color=TEXT_W,
            font=ctk.CTkFont(size=11, family="Courier"),
            height=140,
        )
        self.tabla_facturas.pack(fill="x", padx=16, pady=(0, 14))

    # ── Helpers de construccion ───────────────────────────────────────────────

    def _kpi_card(self, parent, icono, titulo, color, col):
        """Crea una tarjeta de resumen numerico y retorna el label de valor."""
        card = ctk.CTkFrame(parent, fg_color=CARD, corner_radius=12)
        card.grid(row=0, column=col, padx=(0 if col == 0 else 6, 0), sticky="nsew")

        fila = ctk.CTkFrame(card, fg_color="transparent")
        fila.pack(fill="x", padx=14, pady=(12, 4))
        ctk.CTkLabel(
            fila, text=icono, font=ctk.CTkFont(size=18), text_color=color,
        ).pack(side="left")

        ctk.CTkLabel(
            card, text=titulo,
            font=ctk.CTkFont(size=10), text_color=TEXT_G,
        ).pack(anchor="w", padx=14)

        # Label del valor — lo retorno para que el controlador lo actualice
        lbl_val = ctk.CTkLabel(
            card, text="—",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=color,
        )
        lbl_val.pack(anchor="w", padx=14, pady=(2, 12))
        return lbl_val

    def _label_col(self, parent, texto, col, row):
        """Etiqueta de campo usando grid (para formularios de multiples columnas)."""
        ctk.CTkLabel(
            parent, text=texto,
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=TEXT_G,
        ).grid(row=row, column=col, sticky="w",
               padx=(0 if col == 0 else 6, 0), pady=(0, 2))

    def _entry_col(self, parent, placeholder, col, row):
        """Entry posicionado en una columna del grid."""
        e = ctk.CTkEntry(
            parent,
            placeholder_text=placeholder,
            placeholder_text_color="#444",
            fg_color=CARD2, border_color=BORDER, border_width=1,
            text_color=TEXT_W, font=ctk.CTkFont(size=13), height=38,
        )
        e.grid(row=row, column=col, sticky="ew",
               padx=(0 if col == 0 else 6, 0))
        return e

    # ── Metodos que llama el controlador ─────────────────────────────────────

    def actualizar_kpi_hoy(self, valor):
        """Actualiza el KPI de ingresos del dia."""
        self._lbl_hoy.configure(text=valor)

    def actualizar_kpi_mes(self, valor):
        """Actualiza el KPI de ingresos del mes."""
        self._lbl_mes.configure(text=valor)

    def actualizar_kpi_pendientes(self, valor):
        """Actualiza el KPI de citas pendientes."""
        self._lbl_pend.configure(text=str(valor))

    def mostrar_pagos(self, pagos):
        """Llena la tabla del historial con los pagos recibidos."""
        self.tabla_pagos.configure(state="normal")
        self.tabla_pagos.delete("1.0", "end")

        if not pagos:
            self.tabla_pagos.insert("end", "No hay pagos en el período seleccionado.")
        else:
            # Encabezado de la tabla alineado con fuente monoespaciada
            enc = f"{'ID':>4}  {'FECHA':<12} {'CÓDIGO':<10} {'MÉTODO':<14} {'MONTO':>12}  {'GANANCIA EMP':>14}\n"
            self.tabla_pagos.insert("end", enc)
            self.tabla_pagos.insert("end", "─" * 72 + "\n")

            total = 0
            for p in pagos:
                monto = p.get("monto", 0) or 0
                total += monto
                linea = (
                    f"{p.get('id',''):>4}  "
                    f"{formatear_fecha_es(p.get('fecha','')):<12} "
                    f"{p.get('codigo_cita',''):<10} "
                    f"{p.get('metodo',''):<14} "
                    f"${monto:>10,.0f}  "
                    f"${p.get('ganancia_empleado', 0):>12,.0f}\n"
                )
                self.tabla_pagos.insert("end", linea)

            # Linea de totales al final
            self.tabla_pagos.insert("end", "─" * 72 + "\n")
            self.tabla_pagos.insert("end", f"{'TOTAL':>58} ${total:>10,.0f}\n")

        self.tabla_pagos.configure(state="disabled")

    def mostrar_facturas(self, facturas):
        """Llena la tabla de facturas con los datos recibidos."""
        self.tabla_facturas.configure(state="normal")
        self.tabla_facturas.delete("1.0", "end")

        if not facturas:
            self.tabla_facturas.insert("end", "No hay facturas generadas.")
        else:
            enc = f"{'NÚMERO':<20} {'FECHA':<12} {'MONTO':>12}\n"
            self.tabla_facturas.insert("end", enc)
            self.tabla_facturas.insert("end", "─" * 50 + "\n")
            for f in facturas:
                linea = (
                    f"{f.get('numero_factura',''):<20} "
                    f"{formatear_fecha_es(f.get('fecha_emision','')):<12} "
                    f"${f.get('monto', 0):>10,.0f}\n"
                )
                self.tabla_facturas.insert("end", linea)

        self.tabla_facturas.configure(state="disabled")

    def mostrar_msg_pago(self, msg, error=False):
        """Muestra un mensaje de exito o error en el formulario de pago."""
        # Solo lo hago si el label existe (la recepcionista tiene el formulario, el admin no)
        if hasattr(self, "lbl_msg_pago"):
            color = "#E74C3C" if error else VERDE
            self.lbl_msg_pago.configure(text=msg, text_color=color)

    def mostrar_msg_factura(self, msg, error=False):
        """Muestra un mensaje de exito o error en el panel de facturas."""
        color = "#E74C3C" if error else VERDE
        self.lbl_msg_factura.configure(text=msg, text_color=color)

    def actualizar_rango(self, desde, hasta):
        """Muestra el rango filtrado en español."""
        texto = f"Mostrando pagos desde {formatear_fecha_larga_es(desde)} hasta {formatear_fecha_larga_es(hasta)}"
        self.lbl_rango.configure(text=texto)

    def mostrar_sin_cobrar(self, citas: list):
        """Refresca la sección de servicios finalizados sin cobrar."""
        n = len(citas)

        # Actualizo el badge de conteo
        if n == 0:
            self._lbl_sinc_badge.configure(text="Todo al día", text_color=VERDE)
        else:
            self._lbl_sinc_badge.configure(
                text=f"{n} pendiente{'s' if n > 1 else ''}",
                text_color="#E67E22",
            )

        # Limpio filas anteriores
        for w in self._frame_sinc.winfo_children():
            w.destroy()

        if not citas:
            ctk.CTkLabel(
                self._frame_sinc,
                text="No hay servicios pendientes de cobro.",
                font=ctk.CTkFont(size=11), text_color=TEXT_G,
            ).pack(pady=14)
            return

        for cita in citas:
            fila = ctk.CTkFrame(self._frame_sinc, fg_color=CARD2, corner_radius=6)
            fila.pack(fill="x", pady=2)

            # Badge con el código de la cita
            ctk.CTkLabel(
                fila,
                text=cita.get("codigo", ""),
                fg_color="#252525", corner_radius=4,
                font=ctk.CTkFont(size=11, family="Courier", weight="bold"),
                text_color=GOLD,
            ).pack(side="left", padx=(8, 10), pady=7, ipadx=6, ipady=2)

            # Info: cliente · servicio · precio · fecha hora
            cliente  = (cita.get("cliente_nombre") or "—")[:16]
            servicio = (cita.get("servicio") or "")[:18]
            precio   = cita.get("precio", 0) or 0
            fecha    = cita.get("fecha", "")
            hora     = str(cita.get("hora", ""))[:5]

            ctk.CTkLabel(
                fila,
                text=f"{cliente}  ·  {servicio}  ·  ${precio:,.0f}  ·  {fecha}  {hora}",
                font=ctk.CTkFont(size=11),
                text_color=TEXT_W,
                anchor="w",
            ).pack(side="left", fill="x", expand=True)

            # Botón Cobrar — solo visible para la recepcionista que tiene el formulario
            if hasattr(self, "entry_codigo"):
                ctk.CTkButton(
                    fila, text="Cobrar",
                    width=72, height=28, corner_radius=6,
                    fg_color="#1A3A2A", hover_color="#1E5A3A",
                    text_color=VERDE,
                    font=ctk.CTkFont(size=11, weight="bold"),
                    command=lambda c=cita: self._auto_fill_cobro(c),
                ).pack(side="right", padx=8, pady=6)

    def _auto_fill_cobro(self, cita: dict):
        """Rellena el formulario de pago con los datos de la cita elegida."""
        if hasattr(self, "entry_codigo"):
            self.entry_codigo.delete(0, "end")
            self.entry_codigo.insert(0, cita.get("codigo", ""))

        if hasattr(self, "entry_monto"):
            self.entry_monto.delete(0, "end")
            precio = cita.get("precio")
            if precio is not None:
                self.entry_monto.insert(0, str(int(float(precio))))

    def _abrir_calendario(self, campo):
        entry = self.entry_desde if campo == "desde" else self.entry_hasta
        fecha_actual = entry.get().strip() or date.today().isoformat()
        self._popup_calendario = CalendarioPopup(
            self, fecha_actual, lambda fecha: self._poner_fecha(campo, fecha)
        )

    def _poner_fecha(self, campo, fecha):
        entry = self.entry_desde if campo == "desde" else self.entry_hasta
        entry.delete(0, "end")
        entry.insert(0, fecha)
