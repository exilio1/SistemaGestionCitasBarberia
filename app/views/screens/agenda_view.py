"""
Vista de Agenda — Calendario tipo grid con columnas por barbero.
Muestra las citas del dia ordenadas por hora, una columna por empleado.
Boton '+ NUEVA CITA' abre el modal de registro.
"""

import calendar
import customtkinter as ctk
from datetime import date, datetime, timedelta
from app.views.components.tooltip import ToolTip
from app.config import HORARIO_INICIO, HORARIO_FIN

# ── Colores ───────────────────────────────────────────────────────────────────
GOLD        = "#C9A020"
GOLD_HOVER  = "#A8841A"
BG          = "#111111"
CARD        = "#1A1A1A"
CARD2       = "#1F1F1F"
HEADER_COL  = "#161616"
TEXT_W      = "#F0F0F0"
TEXT_G      = "#777777"
AZUL        = "#2980B9"
AZUL_HOVER  = "#1A6A9A"
ROJO        = "#C0392B"

# Colores por estado — cada estado tiene su propio fondo y color de texto
COLOR_ESTADO = {
    "confirmada": ("#2E2A1A", "#C9A020", "CONFIRMADA"),
    "en_curso":   ("#2A2200", "#D4A017", "EN SERVICIO"),
    "pendiente":  ("#1E1E1E", "#888888", "PENDIENTE"),
    "completada": ("#1A2A1A", "#27AE60", "FINALIZADA"),
    "cancelada":  ("#2A1A1A", "#7F3030", "CANCELADA"),
}

MESES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
]

DIAS_SEMANA = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]


class CalendarioPopup(ctk.CTkToplevel):
    def __init__(self, parent, fecha_actual: str, al_seleccionar):
        super().__init__(parent)
        self.title("Seleccionar fecha")
        self.geometry("320x320")
        self.resizable(False, False)
        self.configure(fg_color=CARD)
        self.al_seleccionar = al_seleccionar

        try:
            fecha_base = datetime.strptime(fecha_actual, "%Y-%m-%d").date()
        except ValueError:
            fecha_base = date.today()

        self.anio = fecha_base.year
        self.mes = fecha_base.month

        self.transient(parent.winfo_toplevel())
        self.grab_set()

        self._construir()
        self._dibujar_dias()

    def _construir(self):
        barra = ctk.CTkFrame(self, fg_color="transparent")
        barra.pack(fill="x", padx=12, pady=(12, 6))

        ctk.CTkButton(
            barra,
            text="<",
            width=36,
            command=self._mes_anterior,
            fg_color="#2A2A2A",
            hover_color="#333333",
        ).pack(side="left")

        self.lbl_mes = ctk.CTkLabel(
            barra,
            text="",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=TEXT_W,
        )
        self.lbl_mes.pack(side="left", expand=True)

        ctk.CTkButton(
            barra,
            text=">",
            width=36,
            command=self._mes_siguiente,
            fg_color="#2A2A2A",
            hover_color="#333333",
        ).pack(side="right")

        dias = ctk.CTkFrame(self, fg_color="transparent")
        dias.pack(fill="x", padx=12, pady=(6, 4))

        for col, nombre_dia in enumerate(DIAS_SEMANA):
            ctk.CTkLabel(
                dias,
                text=nombre_dia,
                text_color=TEXT_G,
                font=ctk.CTkFont(size=11, weight="bold"),
            ).grid(row=0, column=col, padx=2, pady=2, sticky="nsew")
            dias.columnconfigure(col, weight=1)

        self.frame_dias = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_dias.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        for fila in range(6):
            self.frame_dias.rowconfigure(fila, weight=1)
        for col in range(7):
            self.frame_dias.columnconfigure(col, weight=1)

    def _dibujar_dias(self):
        self.lbl_mes.configure(text=f"{MESES[self.mes - 1]} {self.anio}")

        for widget in self.frame_dias.winfo_children():
            widget.destroy()

        semanas = calendar.monthcalendar(self.anio, self.mes)
        hoy = date.today()

        for fila, semana in enumerate(semanas):
            for col, dia in enumerate(semana):
                if dia == 0:
                    ctk.CTkLabel(self.frame_dias, text="").grid(
                        row=fila, column=col, padx=2, pady=2, sticky="nsew"
                    )
                    continue

                fecha_boton = date(self.anio, self.mes, dia)
                es_hoy = fecha_boton == hoy

                boton = ctk.CTkButton(
                    self.frame_dias,
                    text=str(dia),
                    height=36,
                    corner_radius=8,
                    fg_color=GOLD if es_hoy else "#202020",
                    hover_color=GOLD_HOVER if es_hoy else "#2D2D2D",
                    text_color="#111111" if es_hoy else TEXT_W,
                    command=lambda f=fecha_boton: self._seleccionar_fecha(f),
                )
                boton.grid(row=fila, column=col, padx=2, pady=2, sticky="nsew")

    def _mes_anterior(self):
        if self.mes == 1:
            self.mes = 12
            self.anio -= 1
        else:
            self.mes -= 1
        self._dibujar_dias()

    def _mes_siguiente(self):
        if self.mes == 12:
            self.mes = 1
            self.anio += 1
        else:
            self.mes += 1
        self._dibujar_dias()

    def _seleccionar_fecha(self, fecha: date):
        self.al_seleccionar(fecha.isoformat())
        self.destroy()


class PopupReprogramar(ctk.CTkToplevel):
    """
    Dialogo para reprogramar una cita.
    Muestra un selector de fecha (con calendario) y botones de hora disponibles.
    Los botones Guardar/Cancelar están siempre visibles al fondo.
    Llama a on_guardar(codigo, nueva_fecha, nueva_hora) al confirmar.
    """

    _COLS = 4   # botones de hora por fila

    def __init__(self, parent, cita: dict, on_guardar):
        super().__init__(parent)
        self.title("Reprogramar Cita")
        self.geometry("440x480")
        self.resizable(False, False)
        self.configure(fg_color=CARD)
        self.transient(parent.winfo_toplevel())
        self.grab_set()

        self._cita              = cita
        self._on_guardar        = on_guardar
        self._hora_seleccionada = None
        self._btns_hora         = {}   # hora_str → CTkButton

        self._construir()

    def _construir(self):
        # ── FOOTER — se packea PRIMERO para que siempre quede visible al fondo ──
        ctk.CTkFrame(self, height=1, fg_color="#2A2A2A").pack(
            side="bottom", fill="x", padx=24, pady=(0, 0)
        )
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(side="bottom", fill="x", padx=24, pady=(10, 18))

        ctk.CTkButton(
            footer, text="Guardar cambios",
            fg_color=GOLD, hover_color=GOLD_HOVER,
            text_color="#111111", height=42, corner_radius=8,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._guardar,
        ).pack(side="left", expand=True, fill="x", padx=(0, 6))

        ctk.CTkButton(
            footer, text="Cancelar",
            fg_color="#2A2A2A", hover_color="#333333",
            text_color=TEXT_G, height=42, corner_radius=8,
            font=ctk.CTkFont(size=13),
            command=self.destroy,
        ).pack(side="left", expand=True, fill="x")

        # ── HEADER ────────────────────────────────────────────────────────
        ctk.CTkLabel(
            self,
            text=f"Reprogramar  {self._cita.get('codigo', '')}",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=GOLD,
        ).pack(padx=24, pady=(20, 2), anchor="w")

        ctk.CTkLabel(
            self,
            text=f"Servicio: {self._cita.get('servicio', '')}",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_G,
        ).pack(padx=24, anchor="w")

        ctk.CTkFrame(self, height=1, fg_color="#2A2A2A").pack(fill="x", padx=24, pady=12)

        # ── FECHA ─────────────────────────────────────────────────────────
        ctk.CTkLabel(
            self, text="NUEVA FECHA",
            font=ctk.CTkFont(size=9, weight="bold"), text_color=TEXT_G,
        ).pack(padx=24, anchor="w")

        fila_fecha = ctk.CTkFrame(self, fg_color="transparent")
        fila_fecha.pack(fill="x", padx=24, pady=(4, 0))

        self._entry_fecha = ctk.CTkEntry(
            fila_fecha,
            placeholder_text=date.today().isoformat(),
            fg_color="#1F1F1F", border_color="#333333",
            text_color=TEXT_W, height=38, font=ctk.CTkFont(size=13),
        )
        self._entry_fecha.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self._entry_fecha.bind("<Return>", lambda _e: self._cargar_horas())

        ctk.CTkButton(
            fila_fecha, text="Calendario", width=104, height=38,
            fg_color="#2A2A2A", hover_color="#333333", text_color=TEXT_W,
            font=ctk.CTkFont(size=12),
            command=self._abrir_calendario,
        ).pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            fila_fecha, text="Buscar", width=68, height=38,
            fg_color=AZUL, hover_color=AZUL_HOVER, text_color="white",
            font=ctk.CTkFont(size=12),
            command=self._cargar_horas,
        ).pack(side="left")

        # ── HORAS (scrollable — ocupa el espacio restante entre header y footer) ──
        ctk.CTkLabel(
            self, text="HORA DISPONIBLE",
            font=ctk.CTkFont(size=9, weight="bold"), text_color=TEXT_G,
        ).pack(padx=24, anchor="w", pady=(12, 4))

        self._scroll_horas = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color="#333333",
            scrollbar_button_hover_color="#444444",
        )
        self._scroll_horas.pack(fill="both", expand=True, padx=24, pady=(0, 8))

        # Configuro 4 columnas de igual peso para el grid de botones
        for c in range(self._COLS):
            self._scroll_horas.columnconfigure(c, weight=1)

        # Mensaje inicial
        ctk.CTkLabel(
            self._scroll_horas,
            text="Selecciona una fecha y pulsa Buscar",
            font=ctk.CTkFont(size=11), text_color=TEXT_G,
        ).grid(row=0, column=0, columnspan=self._COLS, pady=14)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _abrir_calendario(self):
        fecha_actual = self._entry_fecha.get().strip() or date.today().isoformat()
        CalendarioPopup(self, fecha_actual, self._poner_fecha)

    def _poner_fecha(self, fecha: str):
        self._entry_fecha.delete(0, "end")
        self._entry_fecha.insert(0, fecha)
        self._cargar_horas()

    def _cargar_horas(self):
        """Consulta horas libres y las dibuja como botones en el grid."""
        from app.models.cita_model import CitaModel
        from tkinter import messagebox

        fecha = self._entry_fecha.get().strip()
        if not fecha:
            return

        try:
            datetime.strptime(fecha, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Fecha inválida", "Usa el formato AAAA-MM-DD.", parent=self)
            return

        empleado_id = self._cita.get("empleado_id")
        horas = CitaModel().horarios_disponibles(fecha, empleado_id)

        # Limpio el grid y reseteo selección
        for w in self._scroll_horas.winfo_children():
            w.destroy()
        self._btns_hora.clear()
        self._hora_seleccionada = None

        if not horas:
            ctk.CTkLabel(
                self._scroll_horas,
                text=f"No hay horas disponibles el {fecha}.\nElige otra fecha.",
                font=ctk.CTkFont(size=11), text_color=TEXT_G,
                justify="center",
            ).grid(row=0, column=0, columnspan=self._COLS, pady=14)
            return

        # Coloco cada botón en su celda del grid — la última fila queda
        # con las celdas vacías sin estirar, igual de ancha que las demás
        for i, hora in enumerate(horas):
            fila = i // self._COLS
            col  = i %  self._COLS
            btn = ctk.CTkButton(
                self._scroll_horas, text=hora,
                fg_color="#252525", hover_color="#303030",
                text_color=TEXT_W, height=36, corner_radius=6,
                font=ctk.CTkFont(size=12, weight="bold"),
                command=lambda h=hora: self._seleccionar_hora(h),
            )
            btn.grid(row=fila, column=col, padx=3, pady=3, sticky="ew")
            self._btns_hora[hora] = btn

    def _seleccionar_hora(self, hora: str):
        """Resalta el botón elegido en dorado y desactiva los demás."""
        for btn in self._btns_hora.values():
            btn.configure(fg_color="#252525", text_color=TEXT_W)
        if hora in self._btns_hora:
            self._btns_hora[hora].configure(fg_color=GOLD, text_color="#111111")
        self._hora_seleccionada = hora

    def _guardar(self):
        from tkinter import messagebox

        nueva_fecha = self._entry_fecha.get().strip()
        if not nueva_fecha:
            messagebox.showerror("Fecha requerida", "Selecciona una fecha.", parent=self)
            return
        if not self._hora_seleccionada:
            messagebox.showerror("Hora requerida", "Selecciona una hora disponible.", parent=self)
            return
        try:
            datetime.strptime(nueva_fecha, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Fecha inválida", "Usa el formato AAAA-MM-DD.", parent=self)
            return

        if self._on_guardar:
            self._on_guardar(self._cita.get("codigo"), nueva_fecha, self._hora_seleccionada)
        self.destroy()


class PopupDetalleCita(ctk.CTkToplevel):
    """
    Ventana emergente que muestra el detalle completo de una cita al hacer clic
    sobre su celda en la agenda. Ofrece todas las acciones segun el estado:
      - pendiente  → Confirmar, Iniciar Servicio, Reprogramar, Cancelar
      - confirmada → Iniciar Servicio, Reprogramar, Cancelar
      - en_curso   → Finalizar Servicio, Cancelar
      - completada / cancelada → solo Cerrar
    """

    def __init__(
        self, parent, cita: dict,
        on_confirmar=None, on_iniciar=None,
        on_finalizar=None, on_cancelar=None, on_reprogramar=None,
    ):
        super().__init__(parent)
        self.title("Detalle de cita")
        self.geometry("400x480")
        self.resizable(False, False)
        self.configure(fg_color=CARD)
        self.transient(parent.winfo_toplevel())
        self.grab_set()

        self._cita          = cita
        self._on_reprogramar = on_reprogramar

        estado = cita.get("estado", "pendiente")
        bg_estado, color_estado, label_estado = COLOR_ESTADO.get(
            estado, ("#1E1E1E", "#888888", estado.upper())
        )

        # ── Banda de color con el estado ──────────────────────────────────
        banda = ctk.CTkFrame(self, fg_color=bg_estado, corner_radius=0, height=44)
        banda.pack(fill="x")
        banda.pack_propagate(False)
        ctk.CTkLabel(
            banda, text=label_estado,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=color_estado,
        ).pack(expand=True)

        # ── Datos de la cita ──────────────────────────────────────────────
        contenido = ctk.CTkFrame(self, fg_color="transparent")
        contenido.pack(fill="both", expand=True, padx=24, pady=12)

        def _fila(etiqueta, valor):
            f = ctk.CTkFrame(contenido, fg_color="transparent")
            f.pack(fill="x", pady=3)
            ctk.CTkLabel(
                f, text=f"{etiqueta}:",
                font=ctk.CTkFont(size=11), text_color=TEXT_G,
                width=88, anchor="w",
            ).pack(side="left")
            ctk.CTkLabel(
                f, text=str(valor) if valor else "—",
                font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_W,
                anchor="w",
            ).pack(side="left")

        _fila("Codigo",   cita.get("codigo", ""))
        _fila("Cliente",  cita.get("cliente_nombre") or cita.get("nombre", ""))
        _fila("Cedula",   cita.get("cliente_cedula") or cita.get("cedula", ""))
        _fila("Telefono", cita.get("cliente_telefono") or cita.get("telefono", ""))
        _fila("Servicio", cita.get("servicio", ""))
        _fila("Barbero",  cita.get("empleado_nombre", ""))
        _fila("Fecha",    cita.get("fecha", ""))
        _fila("Hora",     str(cita.get("hora", ""))[:5])

        # ── Botones de accion segun el estado ─────────────────────────────
        btns = ctk.CTkFrame(self, fg_color="transparent")
        btns.pack(fill="x", padx=24, pady=(0, 16))

        codigo = cita.get("codigo")

        if estado == "pendiente" and on_confirmar:
            ctk.CTkButton(
                btns, text="Confirmar cita",
                fg_color=AZUL, hover_color=AZUL_HOVER,
                text_color="white", height=38, corner_radius=8,
                font=ctk.CTkFont(size=13, weight="bold"),
                command=lambda: [on_confirmar(codigo), self.destroy()],
            ).pack(fill="x", pady=(0, 5))

        if estado in ("pendiente", "confirmada") and on_iniciar:
            ctk.CTkButton(
                btns, text="Iniciar Servicio",
                fg_color="#E67E22", hover_color="#CA6F1E",
                text_color="white", height=38, corner_radius=8,
                font=ctk.CTkFont(size=13, weight="bold"),
                command=lambda: [on_iniciar(codigo), self.destroy()],
            ).pack(fill="x", pady=(0, 5))

        if estado == "en_curso" and on_finalizar:
            ctk.CTkButton(
                btns, text="Finalizar Servicio",
                fg_color="#8E44AD", hover_color="#7D3C98",
                text_color="white", height=38, corner_radius=8,
                font=ctk.CTkFont(size=13, weight="bold"),
                command=lambda: [on_finalizar(codigo), self.destroy()],
            ).pack(fill="x", pady=(0, 5))

        if estado in ("pendiente", "confirmada") and on_reprogramar:
            ctk.CTkButton(
                btns, text="Reprogramar",
                fg_color=GOLD, hover_color=GOLD_HOVER,
                text_color="#111111", height=38, corner_radius=8,
                font=ctk.CTkFont(size=13, weight="bold"),
                command=self._abrir_reprogramar,
            ).pack(fill="x", pady=(0, 5))

        if estado not in ("completada", "cancelada") and on_cancelar:
            ctk.CTkButton(
                btns, text="Cancelar Cita",
                fg_color="#3A1A1A", hover_color="#4A2A2A",
                text_color=ROJO, height=38, corner_radius=8,
                font=ctk.CTkFont(size=13, weight="bold"),
                command=lambda: self._confirmar_cancelacion(codigo, on_cancelar),
            ).pack(fill="x", pady=(0, 5))

        ctk.CTkButton(
            btns, text="Cerrar",
            fg_color="#2A2A2A", hover_color="#333333",
            text_color=TEXT_G, height=34, corner_radius=8,
            command=self.destroy,
        ).pack(fill="x")

    def _abrir_reprogramar(self):
        """Abre el dialogo de reprogramacion. Al guardar, cierra este popup tambien."""
        def _on_guardado(codigo, fecha, hora):
            if self._on_reprogramar:
                self._on_reprogramar(codigo, fecha, hora)
            self.destroy()

        PopupReprogramar(self, self._cita, _on_guardado)

    def _confirmar_cancelacion(self, codigo, on_cancelar):
        """Pide confirmacion antes de cancelar para evitar cancelaciones accidentales."""
        from tkinter import messagebox
        if messagebox.askyesno(
            "Cancelar cita",
            f"¿Seguro que deseas cancelar la cita {codigo}?\nEsta accion no se puede deshacer.",
            parent=self,
        ):
            on_cancelar(codigo)
            self.destroy()


class AgendaView(ctk.CTkFrame):
    def __init__(self, parent, usuario: dict):
        super().__init__(parent, fg_color=BG)
        self.usuario      = usuario
        self._empleados   = []
        # El controlador conecta estos callbacks para las acciones del popup de detalle
        self._on_confirmar  = None
        self._on_iniciar    = None
        self._on_finalizar  = None
        self._on_cancelar   = None
        self._on_reprogramar = None
        self._construir()

    def _construir(self):
        # ── Barra superior: titulo + selector de fecha + boton nueva cita ─
        barra = ctk.CTkFrame(self, fg_color="transparent")
        barra.pack(fill="x", padx=20, pady=(16, 8))

        self.lbl_titulo = ctk.CTkLabel(
            barra, text="Agenda de Hoy",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=TEXT_W,
        )
        self.lbl_titulo.pack(side="left")

        # Campo para escribir una fecha diferente a la de hoy
        self.entry_fecha = ctk.CTkEntry(
            barra, width=140, height=36,
            fg_color="#1F1F1F", border_color="#333333",
            text_color=TEXT_W, font=ctk.CTkFont(size=13),
            placeholder_text=date.today().isoformat(),
        )
        self.entry_fecha.pack(side="left", padx=(20, 0))
        self.entry_fecha.insert(0, date.today().isoformat())
        self.entry_fecha.bind("<Return>", lambda event: self.btn_buscar.invoke())

        self.btn_calendario = ctk.CTkButton(
            barra,
            text="Calendario",
            font=ctk.CTkFont(size=12),
            fg_color="#2A2A2A",
            hover_color="#333333",
            text_color=TEXT_W,
            width=100,
            height=36,
            command=self.abrir_calendario,
        )
        self.btn_calendario.pack(side="left", padx=8)

        # Boton para buscar la agenda de la fecha ingresada
        self.btn_buscar = ctk.CTkButton(
            barra, text="Buscar",
            font=ctk.CTkFont(size=12),
            fg_color="#2A2A2A", hover_color="#333333",
            text_color=TEXT_W, width=80, height=36,
        )
        self.btn_buscar.pack(side="left", padx=8)

        # Texto descriptivo con el dia de hoy
        self.lbl_fecha_larga = ctk.CTkLabel(
            barra, text="",
            font=ctk.CTkFont(size=13),
            text_color=TEXT_G,
        )
        self.lbl_fecha_larga.pack(side="left", padx=16)

        # Boton para abrir el modal de nueva cita (lo conecta el controlador)
        self.btn_nueva_cita = ctk.CTkButton(
            barra, text="+ Nueva Cita",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=GOLD, hover_color=GOLD_HOVER,
            text_color="#0D0D0D", height=40, corner_radius=8, width=140,
        )
        self.btn_nueva_cita.pack(side="right")
        self._tt_nueva_cita = ToolTip(
            self.btn_nueva_cita, "Abre el formulario para agendar una cita nueva."
        )
        self._tt_calendario = ToolTip(
            self.btn_calendario, "Abre un calendario para escoger el día que deseas ver."
        )

        # ── Contenedor principal scrollable ───────────────────────────────
        # El scroll permite ver muchas filas de horas sin que se corte la pantalla
        self._scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self._scroll.pack(expand=True, fill="both", padx=20, pady=(0, 16))

        # Frame donde se construye el grid de columnas
        self.frame_grid = ctk.CTkFrame(self._scroll, fg_color="transparent")
        self.frame_grid.pack(fill="both", expand=True)

        # Mensaje inicial mientras no se cargan los datos
        ctk.CTkLabel(
            self.frame_grid,
            text="Selecciona una fecha y presiona Buscar",
            text_color=TEXT_G, font=ctk.CTkFont(size=13),
        ).pack(pady=40)

        self.actualizar_titulo_fecha(date.today().isoformat())

    def abrir_calendario(self):
        fecha_actual = self.entry_fecha.get().strip() or date.today().isoformat()
        self._popup_calendario = CalendarioPopup(self, fecha_actual, self._poner_fecha)

    def _poner_fecha(self, fecha: str):
        self.entry_fecha.delete(0, "end")
        self.entry_fecha.insert(0, fecha)
        self.btn_buscar.invoke()

    def actualizar_titulo_fecha(self, fecha: str):
        try:
            fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
        except ValueError:
            fecha_obj = date.today()

        if fecha_obj == date.today():
            self.lbl_titulo.configure(text="Agenda de Hoy")
        else:
            self.lbl_titulo.configure(text="Agenda del Día")

        self.lbl_fecha_larga.configure(text=self._formatear_fecha_larga(fecha_obj))

    def _formatear_fecha_larga(self, fecha_obj: date):
        dias = [
            "Lunes", "Martes", "Miércoles", "Jueves",
            "Viernes", "Sábado", "Domingo"
        ]
        return f"{dias[fecha_obj.weekday()]}, {fecha_obj.day} de {MESES[fecha_obj.month - 1]}"

    def cargar_agenda(self, empleados, citas):
        """Dibuja la agenda en formato de grilla con una columna por empleado.

        empleados: lista de dicts con id, nombre, especialidad
        citas: lista de dicts con empleado_id, hora, servicio, estado, etc.
        """
        self._empleados = empleados

        # Limpio el grid anterior antes de dibujar el nuevo
        for widget in self.frame_grid.winfo_children():
            widget.destroy()

        # Si no hay barberos registrados, muestro un mensaje
        if not empleados:
            ctk.CTkLabel(
                self.frame_grid,
                text="No hay barberos registrados.",
                text_color=TEXT_G, font=ctk.CTkFont(size=13),
            ).pack(pady=40)
            return

        # Configuro columnas: primera para horas, luego una por empleado
        self.frame_grid.columnconfigure(0, weight=0, minsize=80)
        for i in range(len(empleados)):
            self.frame_grid.columnconfigure(i + 1, weight=1, minsize=200)

        # ── Encabezado: nombre de cada barbero ────────────────────────────
        # Celda vacia en la esquina superior izquierda (esquina de horas)
        ctk.CTkFrame(
            self.frame_grid, fg_color=HEADER_COL, height=80
        ).grid(row=0, column=0, sticky="nsew", padx=(0, 2), pady=(0, 2))

        for col, emp in enumerate(empleados):
            cabecera = ctk.CTkFrame(
                self.frame_grid, fg_color=HEADER_COL, corner_radius=8, height=80,
            )
            cabecera.grid(row=0, column=col + 1, sticky="nsew", padx=2, pady=(0, 2))
            cabecera.pack_propagate(False)

            # Circulo con la inicial del barbero (simula foto de perfil)
            inicial = emp.get("nombre", "?")[0].upper()
            circulo = ctk.CTkFrame(cabecera, fg_color=GOLD, corner_radius=22, width=44, height=44)
            circulo.pack(pady=(10, 4))
            circulo.pack_propagate(False)
            ctk.CTkLabel(
                circulo, text=inicial,
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color="#0D0D0D",
            ).pack(expand=True)

            # Nombre y especialidad del barbero
            ctk.CTkLabel(
                cabecera, text=emp.get("nombre", ""),
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=TEXT_W,
            ).pack()
            ctk.CTkLabel(
                cabecera, text=emp.get("especialidad", "").upper(),
                font=ctk.CTkFont(size=9),
                text_color=TEXT_G,
            ).pack(pady=(0, 6))

        # Columna extra para citas sin barbero asignado
        sin_asig = ctk.CTkFrame(
            self.frame_grid, fg_color=HEADER_COL, corner_radius=8, height=80,
        )
        sin_asig.grid(row=0, column=len(empleados) + 1, sticky="nsew", padx=2, pady=(0, 2))
        self.frame_grid.columnconfigure(len(empleados) + 1, weight=1, minsize=120)
        ctk.CTkLabel(sin_asig, text="[ ]", font=ctk.CTkFont(size=20)).pack(pady=(14, 2))
        ctk.CTkLabel(sin_asig, text="Sin Asignar", font=ctk.CTkFont(size=11),
                     text_color=TEXT_G).pack()
        ctk.CTkLabel(sin_asig, text="TURNO LIBRE", font=ctk.CTkFont(size=9),
                     text_color=TEXT_G).pack(pady=(0, 6))

        # ── Filas de horas (9:00 AM a 5:00 PM) ───────────────────────────
        # Genero los slots de 30 min usando el horario real de la barberia
        _inicio = datetime.strptime(HORARIO_INICIO, "%H:%M")
        _fin    = datetime.strptime(HORARIO_FIN,    "%H:%M")
        horas   = []
        _h = _inicio
        while _h < _fin:
            horas.append(_h.strftime("%H:%M"))
            _h += timedelta(minutes=30)

        # Organizo las citas en un diccionario (empleado_id, hora) -> cita
        # para buscarlas rapido al dibujar cada celda
        mapa_citas = {}
        for cita in citas:
            emp_id = cita.get("empleado_id")
            hora   = cita.get("hora", "")[:5]  # solo tomo HH:MM
            clave  = (emp_id, hora)
            mapa_citas[clave] = cita

        for fila_idx, hora in enumerate(horas):
            row_num = fila_idx + 1

            # Celda de la hora (columna 0) — altura 82 para que alinee con las celdas de cita
            celda_hora = ctk.CTkFrame(
                self.frame_grid, fg_color="transparent", height=82
            )
            celda_hora.grid(row=row_num, column=0, sticky="nw", pady=2)
            celda_hora.pack_propagate(False)
            ctk.CTkLabel(
                celda_hora, text=hora,
                font=ctk.CTkFont(size=11),
                text_color=TEXT_G,
            ).pack(padx=8, pady=14)

            # Dibujo la celda de cada barbero en esa hora
            for col, emp in enumerate(empleados):
                emp_id = emp.get("id")
                cita = mapa_citas.get((emp_id, hora))
                self._celda_cita(row_num, col + 1, cita)

            # Celda vacia en la columna "Sin Asignar"
            ctk.CTkFrame(
                self.frame_grid, fg_color="#161616", corner_radius=6, height=82,
            ).grid(row=row_num, column=len(empleados) + 1, sticky="nsew", padx=2, pady=2)

    def _celda_cita(self, row, col, cita):
        """Crea una celda en la grilla: llena si hay cita o vacia si no hay."""
        if cita:
            estado = cita.get("estado", "pendiente")
            bg_color, texto_color, label_estado = COLOR_ESTADO.get(
                estado, ("#1E1E1E", "#888888", estado.upper())
            )
            # Las celdas pendientes tienen borde mas grueso para destacar
            borde = 2 if estado == "pendiente" else 1
            celda = ctk.CTkFrame(
                self.frame_grid, fg_color=bg_color,
                corner_radius=6, height=82,
                border_width=borde, border_color=texto_color,
            )
            celda.grid(row=row, column=col, sticky="nsew", padx=2, pady=2)
            celda.pack_propagate(False)

            lbl_estado = ctk.CTkLabel(
                celda, text=label_estado,
                font=ctk.CTkFont(size=8, weight="bold"),
                text_color=texto_color,
            )
            lbl_estado.pack(anchor="w", padx=8, pady=(6, 0))

            # Muestra el nombre del cliente si viene en la consulta
            nombre_cliente = cita.get("cliente_nombre") or ""
            if nombre_cliente:
                ctk.CTkLabel(
                    celda, text=nombre_cliente[:20],
                    font=ctk.CTkFont(size=10, weight="bold"),
                    text_color=TEXT_W,
                ).pack(anchor="w", padx=8, pady=(2, 0))

            lbl_servicio = ctk.CTkLabel(
                celda, text=cita.get("servicio", "")[:22],
                font=ctk.CTkFont(size=10),
                text_color=TEXT_G,
            )
            lbl_servicio.pack(anchor="w", padx=8, pady=(1, 0))

            # Al hacer clic en cualquier parte de la celda se abre el popup de detalle
            def _abrir_popup(event=None, _cita=cita):
                PopupDetalleCita(
                    self,
                    _cita,
                    on_confirmar=self._on_confirmar,
                    on_iniciar=self._on_iniciar,
                    on_finalizar=self._on_finalizar,
                    on_cancelar=self._on_cancelar,
                    on_reprogramar=self._on_reprogramar,
                )

            for widget in [celda, lbl_estado, lbl_servicio]:
                widget.bind("<Button-1>", _abrir_popup)
            if nombre_cliente:
                # lbl_cliente es el ultimo label pack-eado, lo bindeamos también
                for w in celda.winfo_children():
                    w.bind("<Button-1>", _abrir_popup)

        else:
            celda = ctk.CTkFrame(
                self.frame_grid, fg_color="#161616",
                corner_radius=6, height=82,
            )
            celda.grid(row=row, column=col, sticky="nsew", padx=2, pady=2)
