"""
Vista de Agenda — Calendario tipo grid con columnas por barbero.
Muestra las citas del dia ordenadas por hora, una columna por empleado.
Boton '+ NUEVA CITA' abre el modal de registro.
"""

import calendar
import customtkinter as ctk
from datetime import date, datetime
from app.views.components.tooltip import ToolTip

# ── Colores ───────────────────────────────────────────────────────────────────
GOLD        = "#C9A020"
GOLD_HOVER  = "#A8841A"
BG          = "#111111"
CARD        = "#1A1A1A"
CARD2       = "#1F1F1F"
HEADER_COL  = "#161616"   # fondo de las cabeceras de columna
TEXT_W      = "#F0F0F0"
TEXT_G      = "#777777"

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


class AgendaView(ctk.CTkFrame):
    def __init__(self, parent, usuario: dict):
        super().__init__(parent, fg_color=BG)
        self.usuario = usuario
        self._empleados = []       # lista de empleados, la carga el controlador
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
        horas = [f"{h:02d}:00" for h in range(9, 18)]

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

            # Celda de la hora (columna 0)
            celda_hora = ctk.CTkFrame(
                self.frame_grid, fg_color="transparent", height=64
            )
            celda_hora.grid(row=row_num, column=0, sticky="nw", pady=2)
            celda_hora.pack_propagate(False)
            ctk.CTkLabel(
                celda_hora, text=hora,
                font=ctk.CTkFont(size=11),
                text_color=TEXT_G,
            ).pack(padx=8, pady=10)

            # Dibujo la celda de cada barbero en esa hora
            for col, emp in enumerate(empleados):
                emp_id = emp.get("id")
                cita = mapa_citas.get((emp_id, hora))
                self._celda_cita(row_num, col + 1, cita)

            # Celda vacia en la columna "Sin Asignar"
            ctk.CTkFrame(
                self.frame_grid, fg_color="#161616", corner_radius=6, height=64,
            ).grid(row=row_num, column=len(empleados) + 1, sticky="nsew", padx=2, pady=2)

    def _celda_cita(self, row, col, cita):
        """Crea una celda en la grilla: llena si hay cita o vacia si no hay."""
        if cita:
            # Si hay cita, la muestro con el color del estado correspondiente
            estado = cita.get("estado", "pendiente")
            bg_color, texto_color, label_estado = COLOR_ESTADO.get(
                estado, ("#1E1E1E", "#888888", estado.upper())
            )
            celda = ctk.CTkFrame(
                self.frame_grid, fg_color=bg_color,
                corner_radius=6, height=64,
                border_width=1, border_color=texto_color,
            )
            celda.grid(row=row, column=col, sticky="nsew", padx=2, pady=2)
            celda.pack_propagate(False)

            # Badge del estado (CONFIRMADA, PENDIENTE, etc.)
            ctk.CTkLabel(
                celda, text=label_estado,
                font=ctk.CTkFont(size=8, weight="bold"),
                text_color=texto_color,
            ).pack(anchor="w", padx=8, pady=(4, 0))

            # Nombre del servicio
            ctk.CTkLabel(
                celda, text=cita.get("servicio", "")[:22],
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=TEXT_W,
            ).pack(anchor="w", padx=8)

            # Codigo de la cita para identificarla
            ctk.CTkLabel(
                celda, text=f"Cód: {cita.get('codigo','')}",
                font=ctk.CTkFont(size=9),
                text_color=TEXT_G,
            ).pack(anchor="w", padx=8)
        else:
            # Celda vacia — slot disponible
            celda = ctk.CTkFrame(
                self.frame_grid, fg_color="#161616",
                corner_radius=6, height=64,
            )
            celda.grid(row=row, column=col, sticky="nsew", padx=2, pady=2)
