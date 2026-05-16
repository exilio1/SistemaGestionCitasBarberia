"""
Vista de Reportes — Estadisticas del negocio.
Muestra KPIs del periodo, grafico de barras de ingresos semanales
y una tabla de rendimiento por barbero.
Solo disponible para el administrador.
"""

import customtkinter as ctk
from app.views.components.tooltip import ToolTip
from datetime import date
from app.views.components.calendario import CalendarioPopup, formatear_fecha_larga_es

# ── Colores ───────────────────────────────────────────────────────────────────
GOLD       = "#C9A020"
GOLD_HOVER = "#A8841A"
GOLD_DIM   = "#2E2A1A"
BG         = "#111111"
CARD       = "#1A1A1A"
CARD2      = "#1F1F1F"
BORDER     = "#2A2A2A"
TEXT_W     = "#F0F0F0"
TEXT_G     = "#777777"
VERDE      = "#27AE60"
VERDE_DIM  = "#1A4A2A"
AZUL       = "#3A8FD4"


class ReportesView(ctk.CTkFrame):
    """Pantalla de reportes con KPIs y grafico de barras simple."""

    def __init__(self, parent, usuario: dict):
        super().__init__(parent, fg_color=BG)
        self._usuario = usuario
        self._construir()

    def _construir(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(expand=True, fill="both", padx=20, pady=16)

        # ── Encabezado ────────────────────────────────────────────────────
        ctk.CTkLabel(
            scroll, text="REPORTES",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=TEXT_W,
        ).pack(anchor="w")

        ctk.CTkLabel(
            scroll,
            text="Analiza los ingresos, ocupación y rendimiento del equipo.",
            font=ctk.CTkFont(size=13),
            text_color=TEXT_G,
        ).pack(anchor="w", pady=(2, 16))

        # ── Filtro de fechas para el periodo del reporte ──────────────────
        filtro_card = ctk.CTkFrame(scroll, fg_color=CARD, corner_radius=12)
        filtro_card.pack(fill="x", pady=(0, 16))

        fila_f = ctk.CTkFrame(filtro_card, fg_color="transparent")
        fila_f.pack(fill="x", padx=16, pady=12)

        ctk.CTkLabel(
            fila_f, text="Período:",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=TEXT_W,
        ).pack(side="left")

        # Campos de fecha inicio y fin del periodo
        ctk.CTkLabel(
            fila_f, text="Desde:",
            font=ctk.CTkFont(size=12), text_color=TEXT_G,
        ).pack(side="left", padx=(16, 4))
        self.entry_desde = ctk.CTkEntry(
            fila_f, width=120, height=34,
            fg_color=CARD2, border_color=BORDER,
            text_color=TEXT_W, font=ctk.CTkFont(size=12),
            placeholder_text="AAAA-MM-DD",
        )
        self.entry_desde.pack(side="left")
        self.btn_cal_desde = ctk.CTkButton(
            fila_f, text="Cal", width=38, height=34,
            fg_color="#2A2A2A", hover_color="#333333", text_color=TEXT_W,
            command=lambda: self._abrir_calendario("desde"),
        )
        self.btn_cal_desde.pack(side="left", padx=(4, 0))

        ctk.CTkLabel(
            fila_f, text="Hasta:",
            font=ctk.CTkFont(size=12), text_color=TEXT_G,
        ).pack(side="left", padx=(10, 4))
        self.entry_hasta = ctk.CTkEntry(
            fila_f, width=120, height=34,
            fg_color=CARD2, border_color=BORDER,
            text_color=TEXT_W, font=ctk.CTkFont(size=12),
            placeholder_text="AAAA-MM-DD",
        )
        self.entry_hasta.pack(side="left")
        self.btn_cal_hasta = ctk.CTkButton(
            fila_f, text="Cal", width=38, height=34,
            fg_color="#2A2A2A", hover_color="#333333", text_color=TEXT_W,
            command=lambda: self._abrir_calendario("hasta"),
        )
        self.btn_cal_hasta.pack(side="left", padx=(4, 0))

        # Boton para generar el reporte con las fechas seleccionadas
        self.btn_generar = ctk.CTkButton(
            fila_f, text="Generar Reporte",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=GOLD, hover_color=GOLD_HOVER,
            text_color="#0D0D0D", height=34, corner_radius=8, width=140,
        )
        self.btn_generar.pack(side="left", padx=12)
        self._tt_generar = ToolTip(
            self.btn_generar, "Genera el reporte usando el rango de fechas escrito."
        )

        self.lbl_periodo = ctk.CTkLabel(
            filtro_card, text="",
            font=ctk.CTkFont(size=12), text_color=TEXT_G,
        )
        self.lbl_periodo.pack(anchor="w", padx=16, pady=(0, 12))

        # ── Fila de cuatro KPIs del periodo ───────────────────────────────
        fila_kpis = ctk.CTkFrame(scroll, fg_color="transparent")
        fila_kpis.pack(fill="x", pady=(0, 16))
        for i in range(4):
            fila_kpis.columnconfigure(i, weight=1)

        # Creo las tarjetas y guardo referencia a los labels para actualizarlos
        self.lbl_ingresos   = self._kpi(fila_kpis, "", "INGRESOS TOTALES",  GOLD,  0)
        self.lbl_ticket     = self._kpi(fila_kpis, "", "TICKET PROMEDIO",    VERDE, 1)
        self.lbl_citas      = self._kpi(fila_kpis, "", "OCUPACIÓN %",        AZUL,  2)
        self.lbl_ganancia   = self._kpi(fila_kpis, "", "GANANCIA NEGOCIO",   GOLD,  3)

        # ── Grafico de barras simple con bloques Unicode ───────────────────
        grafico_card = ctk.CTkFrame(scroll, fg_color=CARD, corner_radius=12)
        grafico_card.pack(fill="x", pady=(0, 16))

        ctk.CTkLabel(
            grafico_card, text="Ingresos por Día",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=TEXT_W,
        ).pack(anchor="w", padx=16, pady=(12, 4))

        # El grafico se construye con el metodo mostrar_grafico_barras
        self.frame_grafico = ctk.CTkFrame(grafico_card, fg_color=CARD2, corner_radius=8)
        self.frame_grafico.pack(fill="x", padx=16, pady=(0, 14))

        # Label donde se renderizan las barras en texto monoespaciado
        self.lbl_grafico = ctk.CTkLabel(
            self.frame_grafico, text="",
            font=ctk.CTkFont(size=12, family="Courier"),
            text_color=GOLD, justify="left",
        )
        self.lbl_grafico.pack(padx=16, pady=12)

        # ── Tabla de rendimiento por barbero ──────────────────────────────
        tabla_card = ctk.CTkFrame(scroll, fg_color=CARD, corner_radius=12)
        tabla_card.pack(fill="both", expand=True, pady=(0, 16))

        fila_t_h = ctk.CTkFrame(tabla_card, fg_color="transparent")
        fila_t_h.pack(fill="x", padx=16, pady=(12, 8))

        ctk.CTkLabel(
            fila_t_h, text="Rendimiento por Barbero",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=TEXT_W,
        ).pack(side="left")

        # Textbox monoespaciado para la tabla de barberos
        self.tabla_barberos = ctk.CTkTextbox(
            tabla_card,
            state="disabled",
            fg_color=CARD2, border_color=BORDER, border_width=1,
            text_color=TEXT_W,
            font=ctk.CTkFont(size=11, family="Courier"),
            height=200,
        )
        self.tabla_barberos.pack(fill="both", expand=True, padx=16, pady=(0, 14))

        # ── Resumen de rentabilidad (ingresos - gastos) ───────────────────
        res_card = ctk.CTkFrame(scroll, fg_color=CARD, corner_radius=12)
        res_card.pack(fill="x", pady=(0, 16))

        ctk.CTkLabel(
            res_card, text="Rentabilidad del Período",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=TEXT_W,
        ).pack(anchor="w", padx=16, pady=(12, 4))

        # Label donde se muestra el texto del resumen generado por el controlador
        self.lbl_resumen = ctk.CTkLabel(
            res_card, text="—",
            font=ctk.CTkFont(size=13),
            text_color=TEXT_G, justify="left",
        )
        self.lbl_resumen.pack(anchor="w", padx=16, pady=(0, 14))

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _kpi(self, parent, icono, titulo, color, col):
        """Crea una tarjeta KPI y retorna el label del valor para actualizarlo."""
        card = ctk.CTkFrame(parent, fg_color=CARD, corner_radius=12)
        card.grid(row=0, column=col, padx=(0 if col == 0 else 6, 0), sticky="nsew")

        fila = ctk.CTkFrame(card, fg_color="transparent")
        fila.pack(fill="x", padx=14, pady=(12, 2))
        ctk.CTkLabel(
            fila, text=icono, font=ctk.CTkFont(size=18), text_color=color,
        ).pack(side="left")

        ctk.CTkLabel(
            card, text=titulo,
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color=TEXT_G,
        ).pack(anchor="w", padx=14)

        # Label del valor grande — lo retorno para que el controlador lo actualice
        lbl = ctk.CTkLabel(
            card, text="—",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=color,
        )
        lbl.pack(anchor="w", padx=14, pady=(2, 12))
        return lbl

    # ── Metodos que llama el controlador ─────────────────────────────────────

    def actualizar_kpis(self, ingresos, ticket, ocupacion, ganancia):
        """Actualiza los cuatro KPIs del encabezado del reporte."""
        self.lbl_ingresos.configure(text=f"${ingresos:,.0f}")
        self.lbl_ticket.configure(text=f"${ticket:,.0f}")
        self.lbl_citas.configure(text=f"{ocupacion:.1f}%")
        self.lbl_ganancia.configure(text=f"${ganancia:,.0f}")

    def mostrar_grafico_barras(self, etiquetas, valores):
        """Dibuja un grafico de barras simple con caracteres de bloque Unicode.

        etiquetas: lista de strings (ej. dias de la semana abreviados)
        valores:   lista de numeros que representan los ingresos de cada dia
        """
        if not valores:
            self.lbl_grafico.configure(text="Sin datos para graficar.")
            return

        maximo = max(valores) if max(valores) > 0 else 1
        altura = 6   # cantidad maxima de bloques por barra
        lineas = []

        # Construyo el grafico de arriba hacia abajo (nivel 6 al 1)
        for nivel in range(altura, 0, -1):
            linea = ""
            for v in valores:
                # Calculo que tan alta debe ser la barra proporcional al maximo
                bloque = int((v / maximo) * altura)
                if bloque >= nivel:
                    linea += "██  "
                else:
                    linea += "    "
            lineas.append(linea)

        # Eje X: etiquetas de los dias abreviadas a 3 caracteres
        eje_x = "  ".join(
            e[:3].upper() for e in etiquetas
        )
        lineas.append("─" * (len(etiquetas) * 4))
        lineas.append(eje_x)

        self.lbl_grafico.configure(text="\n".join(lineas))

    def mostrar_tabla_barberos(self, datos):
        """Llena la tabla de rendimiento con los datos de cada barbero."""
        self.tabla_barberos.configure(state="normal")
        self.tabla_barberos.delete("1.0", "end")

        if not datos:
            self.tabla_barberos.insert("end", "Sin datos en el período seleccionado.")
            self.tabla_barberos.configure(state="disabled")
            return

        # Encabezado de la tabla
        enc = (
            f"{'BARBERO':<20} {'ESPECIALIDAD':<16} "
            f"{'CITAS':>6} {'FACTURADO':>12} {'GANANCIA':>12}\n"
        )
        self.tabla_barberos.insert("end", enc)
        self.tabla_barberos.insert("end", "─" * 68 + "\n")

        for d in datos:
            linea = (
                f"{d.get('nombre_empleado',''):<20} "
                f"{d.get('especialidad',''):<16} "
                f"{d.get('total_citas', 0):>6} "
                f"${d.get('total_facturado', 0):>10,.0f} "
                f"${d.get('total_empleado', 0):>10,.0f}\n"
            )
            self.tabla_barberos.insert("end", linea)

        self.tabla_barberos.configure(state="disabled")

    def mostrar_resumen(self, texto):
        """Actualiza el texto del resumen de rentabilidad."""
        self.lbl_resumen.configure(text=texto)

    def actualizar_periodo(self, desde, hasta):
        texto = f"Período analizado: {formatear_fecha_larga_es(desde)} hasta {formatear_fecha_larga_es(hasta)}"
        self.lbl_periodo.configure(text=texto)

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
