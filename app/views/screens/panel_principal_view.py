"""
Vista del Panel Principal (Home / Dashboard).
Muestra KPIs del dia, proximas citas y tendencia semanal.
Es la primera pantalla que ve el usuario al iniciar sesion.
"""

import customtkinter as ctk
from datetime import datetime

# ── Colores ───────────────────────────────────────────────────────────────────
GOLD       = "#C9A020"
GOLD_DIM   = "#7A5F10"
BG         = "#111111"
CARD       = "#1A1A1A"
CARD2      = "#1F1F1F"
TEXT_W     = "#F0F0F0"
TEXT_G     = "#777777"
VERDE      = "#27AE60"
VERDE_DIM  = "#1A4A2A"   # fondo del badge "+12% VS AYER"
GOLD_BG    = "#2E2A1A"

# Colores para los badges de estado de citas
COLOR_CONFIRMADA  = "#C9A020"
COLOR_EN_SERVICIO = "#D4A017"
COLOR_PENDIENTE   = "#555555"
COLOR_FINALIZADA  = "#27AE60"
COLOR_CANCELADA   = "#7F3030"


class PanelPrincipalView(ctk.CTkFrame):
    def __init__(self, parent, usuario: dict):
        super().__init__(parent, fg_color=BG)
        self._usuario = usuario
        self._rol = usuario.get("rol", "")
        self._construir()

    def _construir(self):
        # Scrollable para que todo quepa en pantallas pequeñas
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(expand=True, fill="both", padx=20, pady=16)

        # ── Encabezado con fecha ──────────────────────────────────────────
        hoy = datetime.now()
        fecha_str = hoy.strftime("Cali, Colombia  •  %d de %B %Y").title()

        ctk.CTkLabel(
            scroll, text="RESUMEN DEL DÍA",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=TEXT_W,
        ).pack(anchor="w")

        ctk.CTkLabel(
            scroll, text=fecha_str,
            font=ctk.CTkFont(size=13),
            text_color=TEXT_G,
        ).pack(anchor="w", pady=(2, 18))

        # ── Fila de KPIs ──────────────────────────────────────────────────
        self.frame_kpis = ctk.CTkFrame(scroll, fg_color="transparent")
        self.frame_kpis.pack(fill="x", pady=(0, 20))

        # Creo las tarjetas de KPI segun el rol del usuario
        self._kpi_frames = {}
        kpis_config = self._get_kpis_config()
        for i, (clave, icono, titulo, color) in enumerate(kpis_config):
            self.frame_kpis.columnconfigure(i, weight=1)
            f = self._crear_kpi_card(self.frame_kpis, icono, titulo, "—", color)
            f.grid(row=0, column=i, padx=(0, 10) if i < len(kpis_config) - 1 else 0, sticky="nsew")
            # Guardo la referencia del frame del KPI para actualizarlo desde el controlador
            self._kpi_frames[clave] = f

        # ── Fila inferior: proximas citas + tendencia semanal ─────────────
        fila_inf = ctk.CTkFrame(scroll, fg_color="transparent")
        fila_inf.pack(fill="both", expand=True)
        fila_inf.columnconfigure(0, weight=3)   # panel citas es mas ancho
        fila_inf.columnconfigure(1, weight=2)

        # Panel izquierdo: lista de proximas citas del dia
        panel_citas = ctk.CTkFrame(fila_inf, fg_color=CARD, corner_radius=12)
        panel_citas.grid(row=0, column=0, padx=(0, 10), sticky="nsew")

        fila_header = ctk.CTkFrame(panel_citas, fg_color="transparent")
        fila_header.pack(fill="x", padx=16, pady=(14, 8))
        ctk.CTkLabel(
            fila_header, text="PRÓXIMAS CITAS",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=TEXT_W,
        ).pack(side="left")

        # Boton para navegar a la agenda completa
        self.btn_ver_agenda = ctk.CTkButton(
            fila_header, text="VER AGENDA COMPLETA →",
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color="transparent", hover_color="#2A2A2A",
            text_color=GOLD, width=160, height=28,
        )
        self.btn_ver_agenda.pack(side="right")

        # Contenedor donde se insertan las filas de citas
        self.frame_citas = ctk.CTkFrame(panel_citas, fg_color="transparent")
        self.frame_citas.pack(fill="both", padx=16, pady=(0, 14))

        # Mensaje de carga mientras el controlador trae los datos
        ctk.CTkLabel(
            self.frame_citas,
            text="Cargando citas...",
            text_color=TEXT_G, font=ctk.CTkFont(size=12),
        ).pack(pady=20)

        # Panel derecho: tendencia semanal con grafico de barras
        panel_der = ctk.CTkFrame(fila_inf, fg_color=CARD, corner_radius=12)
        panel_der.grid(row=0, column=1, sticky="nsew")

        ctk.CTkLabel(
            panel_der, text="TENDENCIA DE CITAS",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=TEXT_W,
        ).pack(anchor="w", padx=16, pady=(14, 8))

        # Area para la grafica — el controlador la llena con barras ASCII
        self.frame_grafica = ctk.CTkFrame(panel_der, fg_color=CARD2, corner_radius=8)
        self.frame_grafica.pack(fill="both", expand=True, padx=16, pady=(0, 14))

        # Etiquetas de los dias de la semana (encabezado del grafico)
        ctk.CTkLabel(
            self.frame_grafica,
            text="LUN  MAR  MIE  JUE  VIE  SAB  DOM",
            font=ctk.CTkFont(size=11, family="Courier"),
            text_color=TEXT_G,
        ).pack(pady=(16, 4))

        # Las barras de tendencia se generan con caracteres Unicode (bloques)
        self.lbl_tendencia = ctk.CTkLabel(
            self.frame_grafica, text="",
            font=ctk.CTkFont(size=12, family="Courier"),
            text_color=GOLD,
        )
        self.lbl_tendencia.pack(pady=8)

        ctk.CTkLabel(
            panel_der, text="",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_G,
        ).pack(padx=16, pady=(0, 4))

        # Resumen del total de citas de la semana
        self.lbl_resumen_semanal = ctk.CTkLabel(
            panel_der, text="",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=VERDE,
        )
        self.lbl_resumen_semanal.pack(padx=16, pady=(0, 14))

    def _get_kpis_config(self):
        """Retorna la lista de KPIs segun el rol del usuario."""
        # Los tres primeros KPIs los ven todos
        base = [
            ("citas_hoy",    "",  "CITAS HOY",           GOLD),
            ("ingresos",     "",  "INGRESOS ESTIMADOS",  VERDE),
            ("ocupacion",    "",  "OCUPACION %",         "#3A8FD4"),
        ]
        # El KPI de gastos solo lo ve el administrador
        if self._rol == "administrador":
            base.append(("gastos_hoy", "",  "GASTOS HOY", COLOR_CANCELADA))
        return base

    def _crear_kpi_card(self, parent, icono, titulo, valor, color):
        """Crea una tarjeta de KPI con icono, titulo y valor numerico grande."""
        card = ctk.CTkFrame(parent, fg_color=CARD, corner_radius=12)

        fila = ctk.CTkFrame(card, fg_color="transparent")
        fila.pack(fill="x", padx=16, pady=(14, 4))

        # Icono del KPI
        ctk.CTkLabel(
            fila, text=icono,
            font=ctk.CTkFont(size=20),
            text_color=color,
        ).pack(side="left")

        # Badge estatico de tendencia (visual)
        ctk.CTkLabel(
            fila, text="+12% VS AYER",
            font=ctk.CTkFont(size=9),
            text_color=VERDE,
            fg_color=VERDE_DIM, corner_radius=4,
        ).pack(side="right", ipadx=6, ipady=2)

        # Titulo del KPI
        ctk.CTkLabel(
            card, text=titulo,
            font=ctk.CTkFont(size=10),
            text_color=TEXT_G,
        ).pack(anchor="w", padx=16)

        # Valor numerico grande — se actualiza desde el controlador
        lbl_valor = ctk.CTkLabel(
            card, text=valor,
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=color,
        )
        lbl_valor.pack(anchor="w", padx=16, pady=(2, 14))

        # Guardo referencia al label del valor dentro del frame del card
        card._lbl_valor = lbl_valor
        return card

    # ── Metodos que llama el controlador ─────────────────────────────────────

    def actualizar_kpi(self, clave, valor):
        """Actualiza el valor mostrado en la tarjeta KPI correspondiente."""
        if clave in self._kpi_frames:
            self._kpi_frames[clave]._lbl_valor.configure(text=valor)

    def cargar_proximas_citas(self, citas):
        """Dibuja la lista de proximas citas en el panel inferior izquierdo."""
        # Limpio el contenido anterior
        for widget in self.frame_citas.winfo_children():
            widget.destroy()

        if not citas:
            ctk.CTkLabel(
                self.frame_citas,
                text="No hay citas próximas para hoy.",
                text_color=TEXT_G, font=ctk.CTkFont(size=12),
            ).pack(pady=20)
            return

        # Muestro solo las primeras 5 citas para no saturar la pantalla
        for cita in citas[:5]:
            self._fila_cita(self.frame_citas, cita)

    def _fila_cita(self, parent, cita):
        """Crea una fila visual para una cita en la lista de proximas citas."""
        estado = cita.get("estado", "pendiente")
        # Determino el color del badge segun el estado de la cita
        color_estado = {
            "confirmada":  COLOR_CONFIRMADA,
            "en_curso":    COLOR_EN_SERVICIO,
            "pendiente":   COLOR_PENDIENTE,
            "completada":  COLOR_FINALIZADA,
            "cancelada":   COLOR_CANCELADA,
        }.get(estado, COLOR_PENDIENTE)

        fila = ctk.CTkFrame(parent, fg_color=CARD2, corner_radius=8)
        fila.pack(fill="x", pady=3)

        # Bloque de hora a la izquierda
        hora = cita.get("hora", "00:00")
        hh, mm = hora.split(":") if ":" in hora else ("00", "00")
        bloque_hora = ctk.CTkFrame(fila, fg_color="transparent", width=60)
        bloque_hora.pack(side="left", padx=(12, 8), pady=10)
        bloque_hora.pack_propagate(False)
        ctk.CTkLabel(
            bloque_hora, text=hh,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=TEXT_W,
        ).pack()
        ctk.CTkLabel(
            bloque_hora, text=mm + " PM" if int(hh) >= 12 else mm + " AM",
            font=ctk.CTkFont(size=10), text_color=TEXT_G,
        ).pack()

        # Separador vertical entre hora e informacion
        ctk.CTkFrame(fila, fg_color="#2A2A2A", width=1).pack(side="left", fill="y", pady=8)

        # Informacion de la cita: servicio y codigo
        info = ctk.CTkFrame(fila, fg_color="transparent")
        info.pack(side="left", fill="both", expand=True, padx=12, pady=10)
        ctk.CTkLabel(
            info, text=cita.get("servicio", "Servicio"),
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=TEXT_W, anchor="w",
        ).pack(anchor="w")
        ctk.CTkLabel(
            info, text="Cód: " + cita.get("codigo", ""),
            font=ctk.CTkFont(size=11),
            text_color=TEXT_G, anchor="w",
        ).pack(anchor="w")

        # Badge del estado a la derecha
        estado_label = estado.upper().replace("_", " ")
        ctk.CTkLabel(
            fila, text=estado_label,
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=color_estado,
            fg_color="#1A1A1A", corner_radius=6,
        ).pack(side="right", padx=12, ipadx=8, ipady=4)

    def mostrar_tendencia(self, datos_semana):
        """Genera barras ASCII con bloques Unicode para mostrar la tendencia semanal."""
        if not datos_semana:
            return
        maximo = max(datos_semana) if datos_semana else 1
        barras = ""
        # Construyo las barras proporcionales al maximo de la semana
        for n in datos_semana:
            altura = int((n / maximo) * 5) if maximo > 0 else 0
            barras += "█" * altura + " "
        self.lbl_tendencia.configure(text=barras.strip())

    def mostrar_resumen_semanal(self, total, cambio):
        """Muestra el total de citas de la semana con su variacion porcentual."""
        signo = "+" if cambio >= 0 else "-"
        self.lbl_resumen_semanal.configure(
            text=f"{total} Citas  {signo}{abs(cambio):.1f}%"
        )
