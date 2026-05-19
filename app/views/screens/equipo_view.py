"""
Vista de Equipo — Gestion del equipo de barberos.
Panel izquierdo: tabla de empleados con estado y estadisticas.
Panel derecho: consulta de pago a barbero y registro rapido de gasto.
Solo disponible para el administrador.
"""

import customtkinter as ctk
from datetime import date
from app.views.components.calendario import CalendarioPopup, formatear_fecha_larga_es

# ── Colores ───────────────────────────────────────────────────────────────────
GOLD       = "#C9A020"
GOLD_HOVER = "#A8841A"
GOLD_DIM   = "#2E2A1A"   # fondo del circulo con la inicial
BG         = "#111111"
CARD       = "#1A1A1A"
CARD2      = "#1F1F1F"
BORDER     = "#2A2A2A"
TEXT_W     = "#F0F0F0"
TEXT_G     = "#777777"
VERDE      = "#27AE60"
VERDE_DIM  = "#1A4A2A"
ROJO       = "#C0392B"


class EquipoView(ctk.CTkFrame):
    """Pantalla de gestion del equipo (solo administrador)."""

    def __init__(self, parent, usuario: dict):
        super().__init__(parent, fg_color=BG)
        self._usuario = usuario
        self._construir()

    def _construir(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(expand=True, fill="both", padx=20, pady=16)

        # ── Titulo ────────────────────────────────────────────────────────
        ctk.CTkLabel(
            scroll, text="EQUIPO DE TRABAJO",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=TEXT_W,
        ).pack(anchor="w")

        ctk.CTkLabel(
            scroll,
            text="Gestiona los barberos, calcula pagos y registra gastos.",
            font=ctk.CTkFont(size=13),
            text_color=TEXT_G,
        ).pack(anchor="w", pady=(2, 16))

        # ── Layout de dos columnas ────────────────────────────────────────
        # Columna izquierda mas ancha para la tabla de empleados
        dos_col = ctk.CTkFrame(scroll, fg_color="transparent")
        dos_col.pack(fill="both", expand=True)
        dos_col.columnconfigure(0, weight=3)
        dos_col.columnconfigure(1, weight=2)

        # ── Panel izquierdo: lista de barberos activos ─────────────────────
        panel_izq = ctk.CTkFrame(dos_col, fg_color=CARD, corner_radius=12)
        panel_izq.grid(row=0, column=0, padx=(0, 8), sticky="nsew")

        fila_izq_h = ctk.CTkFrame(panel_izq, fg_color="transparent")
        fila_izq_h.pack(fill="x", padx=16, pady=(12, 8))

        ctk.CTkLabel(
            fila_izq_h, text="Barberos Activos e Inactivos",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=TEXT_W,
        ).pack(side="left")

        # Boton para ir a la pantalla de agregar nuevo barbero
        self.btn_agregar = ctk.CTkButton(
            fila_izq_h, text="+ Agregar Barbero",
            font=ctk.CTkFont(size=11),
            fg_color="#2A2A2A", hover_color="#333333",
            text_color=TEXT_G, height=30, corner_radius=8,
        )
        self.btn_agregar.pack(side="right")

        # Encabezado de la tabla de empleados
        enc = ctk.CTkFrame(panel_izq, fg_color="#161616")
        enc.pack(fill="x", padx=16, pady=(0, 2))
        for texto, w in [("EMPLEADO", 170), ("ESPECIALIDAD", 100), ("% GANANCIA", 80), ("ESTADO", 80), ("ACCIÓN", 90)]:
            ctk.CTkLabel(
                enc, text=texto, width=w,
                font=ctk.CTkFont(size=9, weight="bold"),
                text_color=TEXT_G, anchor="w",
            ).pack(side="left", padx=4, pady=4)

        # Contenedor donde se insertan las filas de empleados dinamicamente
        self.frame_empleados = ctk.CTkFrame(panel_izq, fg_color="transparent")
        self.frame_empleados.pack(fill="both", expand=True, padx=16)

        # Mensaje de carga temporal
        ctk.CTkLabel(
            self.frame_empleados,
            text="Cargando empleados...",
            text_color=TEXT_G, font=ctk.CTkFont(size=12),
        ).pack(pady=20)

        # Formulario rapido para agregar barbero (el controlador lo maneja)
        self.frame_form_barbero = ctk.CTkFrame(panel_izq, fg_color=CARD2, corner_radius=8)
        # Este frame se muestra solo cuando se presiona el boton agregar

        ctk.CTkLabel(
            panel_izq, text="",
            fg_color="transparent", height=8,
        ).pack()

        # ── Panel derecho: calculo de pago + registro de gasto rapido ─────
        panel_der = ctk.CTkFrame(dos_col, fg_color="transparent")
        panel_der.grid(row=0, column=1, sticky="nsew")

        # Subpanel: calcular cuanto se le paga a cada barbero
        pago_panel = ctk.CTkFrame(panel_der, fg_color=CARD, corner_radius=12)
        pago_panel.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            pago_panel, text="Calcular Pago a Barbero",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=GOLD,
        ).pack(anchor="w", padx=14, pady=(12, 8))

        # Campo de fecha inicial del periodo
        self._label_small(pago_panel, "PERÍODO DESDE")
        self.entry_desde = ctk.CTkEntry(
            pago_panel, height=36,
            fg_color=CARD2, border_color=BORDER, border_width=1,
            text_color=TEXT_W, font=ctk.CTkFont(size=12),
            placeholder_text="AAAA-MM-DD",
        )
        self.entry_desde.pack(fill="x", padx=14, pady=(2, 6))
        self.btn_cal_desde = ctk.CTkButton(
            pago_panel, text="Abrir calendario",
            font=ctk.CTkFont(size=11),
            fg_color="#2A2A2A", hover_color="#333333",
            text_color=TEXT_W, height=30,
            command=lambda: self._abrir_calendario("desde"),
        )
        self.btn_cal_desde.pack(fill="x", padx=14, pady=(0, 6))

        # Campo de fecha final del periodo
        self._label_small(pago_panel, "PERÍODO HASTA")
        self.entry_hasta = ctk.CTkEntry(
            pago_panel, height=36,
            fg_color=CARD2, border_color=BORDER, border_width=1,
            text_color=TEXT_W, font=ctk.CTkFont(size=12),
            placeholder_text="AAAA-MM-DD",
        )
        self.entry_hasta.pack(fill="x", padx=14, pady=(2, 8))
        self.btn_cal_hasta = ctk.CTkButton(
            pago_panel, text="Abrir calendario",
            font=ctk.CTkFont(size=11),
            fg_color="#2A2A2A", hover_color="#333333",
            text_color=TEXT_W, height=30,
            command=lambda: self._abrir_calendario("hasta"),
        )
        self.btn_cal_hasta.pack(fill="x", padx=14, pady=(0, 8))

        self.lbl_periodo_pago = ctk.CTkLabel(
            pago_panel, text="",
            font=ctk.CTkFont(size=11), text_color=TEXT_G,
            justify="left",
        )
        self.lbl_periodo_pago.pack(anchor="w", padx=14, pady=(0, 8))

        # Boton calcular — el controlador le asigna el comando
        self.btn_calcular = ctk.CTkButton(
            pago_panel, text="CALCULAR PAGO",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=GOLD, hover_color=GOLD_HOVER,
            text_color="#0D0D0D", height=40, corner_radius=8,
        )
        self.btn_calcular.pack(fill="x", padx=14, pady=(0, 8))

        # Tabla de resultados del calculo de pago
        self.tabla_pago = ctk.CTkTextbox(
            pago_panel,
            state="disabled",
            fg_color=CARD2, border_color=BORDER, border_width=1,
            text_color=TEXT_W,
            font=ctk.CTkFont(size=10, family="Courier"),
            height=180,
        )
        self.tabla_pago.pack(fill="x", padx=14, pady=(0, 14))

        # Subpanel: registrar un gasto rapido desde esta pantalla
        gasto_panel = ctk.CTkFrame(panel_der, fg_color=CARD, corner_radius=12)
        gasto_panel.pack(fill="x")

        ctk.CTkLabel(
            gasto_panel, text="Registrar Gasto Rapido",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=ROJO,
        ).pack(anchor="w", padx=14, pady=(12, 8))

        # Campo de descripcion del gasto
        self._label_small(gasto_panel, "DESCRIPCIÓN")
        self.entry_gasto_desc = ctk.CTkEntry(
            gasto_panel, height=36,
            fg_color=CARD2, border_color=BORDER, border_width=1,
            text_color=TEXT_W, font=ctk.CTkFont(size=12),
            placeholder_text="Ej. Compra de navajas",
        )
        self.entry_gasto_desc.pack(fill="x", padx=14, pady=(2, 6))

        # Fila con categoria y monto en dos columnas
        fila_gasto = ctk.CTkFrame(gasto_panel, fg_color="transparent")
        fila_gasto.pack(fill="x", padx=14, pady=(0, 8))
        fila_gasto.columnconfigure(0, weight=1)
        fila_gasto.columnconfigure(1, weight=1)

        # Columna izquierda: categoria del gasto
        col_cat = ctk.CTkFrame(fila_gasto, fg_color="transparent")
        col_cat.grid(row=0, column=0, padx=(0, 4), sticky="ew")
        self._label_small(col_cat, "CATEGORÍA")
        self.opt_gasto_cat = ctk.CTkOptionMenu(
            col_cat,
            values=["arriendo", "servicios", "insumos", "nomina", "otros"],
            fg_color=CARD2, button_color="#333333",
            button_hover_color="#444444",
            text_color=TEXT_W, height=36,
            font=ctk.CTkFont(size=12),
            dropdown_fg_color=CARD,
            dropdown_hover_color="#333333",
            dropdown_text_color=TEXT_W,
        )
        self.opt_gasto_cat.pack(fill="x", pady=(2, 0))

        # Columna derecha: monto del gasto
        col_mon = ctk.CTkFrame(fila_gasto, fg_color="transparent")
        col_mon.grid(row=0, column=1, padx=(4, 0), sticky="ew")
        self._label_small(col_mon, "MONTO ($)")
        self.entry_gasto_monto = ctk.CTkEntry(
            col_mon, height=36,
            fg_color=CARD2, border_color=BORDER, border_width=1,
            text_color=TEXT_W, font=ctk.CTkFont(size=12),
            placeholder_text="Ej. 250000",
        )
        self.entry_gasto_monto.pack(fill="x", pady=(2, 0))

        # Boton para registrar el gasto — rojo para distinguirlo del calcular
        self.btn_gasto = ctk.CTkButton(
            gasto_panel, text="REGISTRAR GASTO",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#3A1A1A", hover_color="#4A2A2A",
            text_color=ROJO, height=40, corner_radius=8,
        )
        self.btn_gasto.pack(fill="x", padx=14, pady=(0, 8))

        # Mensaje de resultado del registro de gasto
        self.lbl_msg_gasto = ctk.CTkLabel(
            gasto_panel, text="",
            font=ctk.CTkFont(size=11), text_color=VERDE,
        )
        self.lbl_msg_gasto.pack(anchor="w", padx=14, pady=(0, 8))

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _label_small(self, parent, texto):
        """Crea una etiqueta pequena gris como titulo de campo."""
        ctk.CTkLabel(
            parent, text=texto,
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color=TEXT_G,
        ).pack(anchor="w", padx=14)

    # ── Metodos que llama el controlador ─────────────────────────────────────

    def cargar_empleados(self, empleados):
        """Dibuja una fila por cada empleado en el panel izquierdo."""
        # Limpio las filas anteriores antes de redibujar
        for w in self.frame_empleados.winfo_children():
            w.destroy()

        if not empleados:
            ctk.CTkLabel(
                self.frame_empleados,
                text="No hay empleados registrados.",
                text_color=TEXT_G, font=ctk.CTkFont(size=12),
            ).pack(pady=20)
            return

        for emp in empleados:
            fila = ctk.CTkFrame(
                self.frame_empleados, fg_color=CARD2, corner_radius=8
            )
            fila.pack(fill="x", pady=3)

            # Circulo con la inicial del empleado
            inicial = emp.get("nombre", "?")[0].upper()
            circulo = ctk.CTkFrame(fila, fg_color=GOLD_DIM, corner_radius=16, width=32, height=32)
            circulo.pack(side="left", padx=(10, 6), pady=8)
            circulo.pack_propagate(False)
            ctk.CTkLabel(
                circulo, text=inicial,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=GOLD,
            ).pack(expand=True)

            # Nombre del empleado
            ctk.CTkLabel(
                fila, text=emp.get("nombre", ""),
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=TEXT_W, width=140, anchor="w",
            ).pack(side="left", padx=(0, 4))

            # Especialidad
            ctk.CTkLabel(
                fila, text=emp.get("especialidad", ""),
                font=ctk.CTkFont(size=11),
                text_color=TEXT_G, width=90, anchor="w",
            ).pack(side="left", padx=4)

            # Porcentaje de ganancia del empleado
            pct = emp.get("porcentaje_ganancia", 60)
            ctk.CTkLabel(
                fila, text=f"{pct:.0f}%",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=GOLD, width=60, anchor="center",
            ).pack(side="left", padx=4)

            # Badge de estado: ACTIVO en verde o INACTIVO en rojo
            activo = emp.get("activo", 1)
            color_badge = VERDE if activo else ROJO
            texto_badge = "ACTIVO" if activo else "INACTIVO"
            ctk.CTkLabel(
                fila, text=texto_badge,
                font=ctk.CTkFont(size=9, weight="bold"),
                text_color=color_badge,
                fg_color="#111111", corner_radius=6,
            ).pack(side="left", padx=6, ipadx=8, ipady=3)

            texto_btn = "Desactivar" if activo else "Activar"
            color_btn = "#3A1A1A" if activo else "#1A3A1A"
            hover_btn = "#4A2A2A" if activo else "#245224"
            ctk.CTkButton(
                fila,
                text=texto_btn,
                width=90,
                height=28,
                fg_color=color_btn,
                hover_color=hover_btn,
                text_color=TEXT_W,
                font=ctk.CTkFont(size=11),
                command=lambda emp_id=emp.get("id"), emp_activo=activo: self._accion_estado(emp_id, emp_activo),
            ).pack(side="right", padx=10)

    def mostrar_pago_barbero(self, datos):
        """Llena la tabla del panel derecho con el calculo de pago por barbero."""
        self.tabla_pago.configure(state="normal")
        self.tabla_pago.delete("1.0", "end")

        if not datos:
            self.tabla_pago.insert("end", "No hay datos en el periodo seleccionado.")
            self.tabla_pago.configure(state="disabled")
            return

        enc = f"{'BARBERO':<18} {'CITAS':>5} {'FACTURADO':>12} {'A PAGAR':>12}\n"
        self.tabla_pago.insert("end", enc)
        self.tabla_pago.insert("end", "─" * 50 + "\n")

        # Acumulo el total para mostrarlo al final
        total_pagar = 0
        for d in datos:
            total_pagar += d.get("total_empleado", 0) or 0
            linea = (
                f"{d.get('nombre_empleado',''):<18} "
                f"{d.get('total_citas', 0):>5} "
                f"${d.get('total_facturado', 0):>10,.0f} "
                f"${d.get('total_empleado', 0):>10,.0f}\n"
            )
            self.tabla_pago.insert("end", linea)

        self.tabla_pago.insert("end", "─" * 50 + "\n")
        self.tabla_pago.insert("end", f"{'TOTAL A PAGAR':>37} ${total_pagar:>10,.0f}\n")
        self.tabla_pago.configure(state="disabled")

    def mostrar_msg_gasto(self, msg, error=False):
        """Muestra un mensaje de exito o error en el panel de gastos rapidos."""
        color = "#E74C3C" if error else VERDE
        self.lbl_msg_gasto.configure(text=msg, text_color=color)

    def set_accion_estado(self, callback):
        """Guarda la función que cambia el estado del empleado."""
        self._accion_estado = callback

    def actualizar_periodo_pago(self, desde, hasta):
        texto = f"Período: {formatear_fecha_larga_es(desde)}\nhasta {formatear_fecha_larga_es(hasta)}"
        self.lbl_periodo_pago.configure(text=texto)

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
