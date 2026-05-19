"""
Vista del Cliente — Solicitar Cita.
Esta es la pantalla principal que ve el cliente cuando inicia sesion.
Le permite ver sus citas y solicitar nuevas.
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
ROJO        = "#E74C3C"


class ClienteSolicitarView(ctk.CTkFrame):
    def __init__(self, parent, usuario: dict):
        super().__init__(parent, fg_color="#111111")
        self._usuario = usuario
        self._servicios_map = {}
        self._construir()

    def _construir(self):
        # ── Saludo personalizado con el nombre del cliente ─────────────────
        nombre = self._usuario.get("nombre", "Cliente")
        ctk.CTkLabel(
            self, text=f"¡Bienvenido, {nombre}!",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=TEXT_WHITE,
        ).pack(pady=(20, 4), padx=16, anchor="w")

        ctk.CTkLabel(
            self,
            text="Solicita tu cita con el barbero que prefieras.",
            font=ctk.CTkFont(size=13),
            text_color=TEXT_GRAY,
        ).pack(padx=16, anchor="w", pady=(0, 6))

        # ── Formulario para solicitar una nueva cita ───────────────────────
        tarjeta = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=12)
        tarjeta.pack(fill="x", padx=16, pady=14)

        ctk.CTkLabel(
            tarjeta, text="Nueva cita",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=GOLD,
        ).pack(anchor="w", padx=16, pady=(14, 8))

        # Campos en dos columnas para aprovechar el espacio
        columnas = ctk.CTkFrame(tarjeta, fg_color="transparent")
        columnas.pack(fill="x", padx=16, pady=(0, 10))
        columnas.columnconfigure(0, weight=1)
        columnas.columnconfigure(1, weight=1)

        # Columna izquierda: servicio y fecha
        izq = ctk.CTkFrame(columnas, fg_color="transparent")
        izq.grid(row=0, column=0, padx=(0, 8), sticky="nsew")

        ctk.CTkLabel(izq, text="Servicio que deseas",
                     text_color=TEXT_GRAY, font=ctk.CTkFont(size=11)).pack(anchor="w")
        # Desplegable con los servicios disponibles
        self.opt_servicio = ctk.CTkOptionMenu(
            izq, values=["Cargando servicios..."],
            fg_color=FIELD_BG, button_color="#333333",
            button_hover_color="#3E3E3E",
            text_color=TEXT_WHITE, height=40,
        )
        self.opt_servicio.pack(fill="x", pady=(2, 10))

        ctk.CTkLabel(izq, text="Fecha (YYYY-MM-DD)",
                     text_color=TEXT_GRAY, font=ctk.CTkFont(size=11)).pack(anchor="w")
        self.entry_fecha = ctk.CTkEntry(
            izq, placeholder_text="Ej. 2025-05-15",
            fg_color=FIELD_BG, border_color="#333333",
            text_color=TEXT_WHITE, height=40,
        )
        self.entry_fecha.pack(fill="x", pady=(2, 10))

        # Columna derecha: hora y observaciones
        der = ctk.CTkFrame(columnas, fg_color="transparent")
        der.grid(row=0, column=1, padx=(8, 0), sticky="nsew")

        ctk.CTkLabel(der, text="Hora preferida (HH:MM)",
                     text_color=TEXT_GRAY, font=ctk.CTkFont(size=11)).pack(anchor="w")
        self.entry_hora = ctk.CTkEntry(
            der, placeholder_text="Ej. 09:00 o 14:30",
            fg_color=FIELD_BG, border_color="#333333",
            text_color=TEXT_WHITE, height=40,
        )
        self.entry_hora.pack(fill="x", pady=(2, 10))

        ctk.CTkLabel(der, text="Observaciones (opcional)",
                     text_color=TEXT_GRAY, font=ctk.CTkFont(size=11)).pack(anchor="w")
        # Campo libre para instrucciones especiales del cliente
        self.entry_observaciones = ctk.CTkEntry(
            der, placeholder_text="Ej. Corte bajo los lados",
            fg_color=FIELD_BG, border_color="#333333",
            text_color=TEXT_WHITE, height=40,
        )
        self.entry_observaciones.pack(fill="x", pady=(2, 10))

        # Boton para enviar la solicitud — el controlador le asigna el comando
        self.btn_solicitar = ctk.CTkButton(
            tarjeta, text="Solicitar Cita",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=GOLD, hover_color=GOLD_HOVER,
            text_color="#111111", height=48, corner_radius=8,
        )
        self.btn_solicitar.pack(anchor="w", padx=16, pady=(4, 14))

        # Label de resultado — muestra confirmacion o error de la solicitud
        self.lbl_resultado = ctk.CTkLabel(
            tarjeta, text="",
            font=ctk.CTkFont(size=13),
            text_color=VERDE,
        )
        self.lbl_resultado.pack(padx=16, pady=(0, 8))

        # ── Seccion de citas del cliente ──────────────────────────────────
        tarjeta2 = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=12)
        tarjeta2.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        ctk.CTkLabel(
            tarjeta2, text="Mis citas",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=GOLD,
        ).pack(anchor="w", padx=16, pady=(12, 4))

        # Textbox monoespaciado para mostrar la tabla de citas del cliente
        self.tabla_citas = ctk.CTkTextbox(
            tarjeta2, state="disabled",
            fg_color=FIELD_BG, text_color=TEXT_WHITE,
            font=ctk.CTkFont(size=12, family="Courier"),
        )
        self.tabla_citas.pack(fill="both", expand=True, padx=16, pady=(0, 14))

    def mostrar_resultado(self, mensaje, error=False):
        """Muestra un mensaje de exito en verde o de error en rojo."""
        color = ROJO if error else VERDE
        self.lbl_resultado.configure(text=mensaje, text_color=color)

    def cargar_servicios(self, servicios):
        """Carga los servicios activos en el OptionMenu."""
        self._servicios_map = {s["nombre"]: s["id"] for s in servicios}
        nombres = list(self._servicios_map.keys()) or ["Sin servicios"]
        self.opt_servicio.configure(values=nombres)
        self.opt_servicio.set(nombres[0])

    def get_servicio_id(self):
        """Retorna el id del servicio seleccionado."""
        return self._servicios_map.get(self.opt_servicio.get())

    def cargar_citas(self, citas):
        """Llena la tabla con las citas del cliente recibidas del controlador."""
        self.tabla_citas.configure(state="normal")
        self.tabla_citas.delete("1.0", "end")

        if not citas:
            self.tabla_citas.insert("end", "No tienes citas registradas todavía.")
        else:
            # Encabezado de la tabla con columnas alineadas
            encabezado = f"{'CÓDIGO':<10} {'SERVICIO':<22} {'FECHA':<12} {'HORA':<8} {'ESTADO':<14}\n"
            self.tabla_citas.insert("end", encabezado)
            self.tabla_citas.insert("end", "-" * 70 + "\n")

            for cita in citas:
                linea = (
                    f"{cita.get('codigo',''):<10} "
                    f"{cita.get('servicio',''):<22} "
                    f"{cita.get('fecha',''):<12} "
                    f"{cita.get('hora',''):<8} "
                    f"{cita.get('estado',''):<14}\n"
                )
                self.tabla_citas.insert("end", linea)

        self.tabla_citas.configure(state="disabled")
