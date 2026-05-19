import calendar
import customtkinter as ctk
from datetime import date, datetime


GOLD = "#C9A020"
GOLD_HOVER = "#A8841A"
CARD = "#1A1A1A"
TEXT_W = "#F0F0F0"
TEXT_G = "#777777"

MESES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]

DIAS_SEMANA = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
DIAS_LARGOS = [
    "lunes", "martes", "miércoles", "jueves",
    "viernes", "sábado", "domingo"
]


def formatear_fecha_es(fecha_txt):
    """Convierte AAAA-MM-DD a una fecha corta en español."""
    try:
        fecha = datetime.strptime(fecha_txt, "%Y-%m-%d").date()
    except ValueError:
        return fecha_txt
    return f"{fecha.day:02d}/{fecha.month:02d}/{fecha.year}"


def formatear_fecha_larga_es(fecha_txt):
    """Convierte AAAA-MM-DD a texto largo en español."""
    try:
        fecha = datetime.strptime(fecha_txt, "%Y-%m-%d").date()
    except ValueError:
        return fecha_txt
    dia_nombre = DIAS_LARGOS[fecha.weekday()]
    mes_nombre = MESES[fecha.month - 1]
    return f"{dia_nombre.title()}, {fecha.day} de {mes_nombre} de {fecha.year}"


class CalendarioPopup(ctk.CTkToplevel):
    """Ventana sencilla para escoger una fecha del mes."""

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
        self.lbl_mes.configure(text=f"{MESES[self.mes - 1].title()} {self.anio}")

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
