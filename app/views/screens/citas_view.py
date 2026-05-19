"""
Vista de Citas.
Flujo completo segun el caso de uso:
  pendiente → confirmada → en_curso → completada / cancelada

Acciones disponibles:
  - Agendar        (recepcionista y admin)
  - Confirmar      (recepcionista y admin)
  - Iniciar servicio  (recepcionista y admin) — pendiente/confirmada → en_curso
  - Finalizar servicio (recepcionista y admin) — en_curso → completada
  - Reprogramar    (recepcionista y admin)
  - Cancelar       (recepcionista y admin)
"""

import customtkinter as ctk

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
AZUL       = "#2980B9"
NARANJA    = "#E67E22"
MORADO     = "#8E44AD"
ROJO       = "#C0392B"


class CitasView(ctk.CTkFrame):
    """Pantalla de gestion de citas con todas las acciones del flujo."""

    def __init__(self, parent, usuario: dict):
        super().__init__(parent, fg_color=BG)
        self._usuario = usuario
        # Mapa nombre → id para convertir la seleccion del OptionMenu a FK de servicio
        self._servicios_map: dict[str, int] = {}
        self._construir()

    def _construir(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(expand=True, fill="both", padx=20, pady=16)

        # ── Titulo ────────────────────────────────────────────────────────
        ctk.CTkLabel(
            scroll, text="Gestion de Citas",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=TEXT_W,
        ).pack(anchor="w")

        ctk.CTkLabel(
            scroll,
            text="Agende, confirme, inicie, finalice, reprograme o cancele citas.",
            font=ctk.CTkFont(size=13), text_color=TEXT_G,
        ).pack(anchor="w", pady=(2, 16))

        # ── Diagrama del flujo de estados (referencia visual) ─────────────
        flujo = ctk.CTkFrame(scroll, fg_color=CARD, corner_radius=10)
        flujo.pack(fill="x", pady=(0, 14))

        ctk.CTkLabel(
            flujo,
            text="Flujo:  PENDIENTE  →  CONFIRMADA  →  EN SERVICIO  →  COMPLETADA  /  CANCELADA",
            font=ctk.CTkFont(size=11, family="Courier"),
            text_color=TEXT_G,
        ).pack(padx=16, pady=8)

        # ── Formulario de datos de la cita ────────────────────────────────
        form = ctk.CTkFrame(scroll, fg_color=CARD, corner_radius=12)
        form.pack(fill="x", pady=(0, 14))

        ctk.CTkLabel(
            form, text="Datos de la Cita",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=GOLD,
        ).pack(anchor="w", padx=16, pady=(12, 8))

        # Divido el formulario en dos columnas para que quepan mas campos
        cols = ctk.CTkFrame(form, fg_color="transparent")
        cols.pack(fill="x", padx=16, pady=(0, 10))
        cols.columnconfigure(0, weight=1)
        cols.columnconfigure(1, weight=1)

        izq = ctk.CTkFrame(cols, fg_color="transparent")
        izq.grid(row=0, column=0, padx=(0, 8), sticky="nsew")

        der = ctk.CTkFrame(cols, fg_color="transparent")
        der.grid(row=0, column=1, padx=(8, 0), sticky="nsew")

        # Campos de la columna izquierda
        self._label(izq, "Codigo de cita")
        self.entry_codigo = self._entry(izq, "Para confirmar/iniciar/cancelar...")

        self._label(izq, "Cedula del cliente")
        self.entry_cedula = self._entry(izq, "Ej. 1234567890")

        self._label(izq, "Telefono del cliente")
        self.entry_telefono = self._entry(izq, "Ej. 3001234567")

        self._label(izq, "Nombre del cliente")
        self.entry_nombre = self._entry(izq, "Ej. Juan Perez")

        # Campos de la columna derecha
        self._label(der, "Servicio")
        # El OptionMenu se llena automaticamente desde la base de datos
        self.opt_servicio = self._option_menu_servicios(der)

        self._label(der, "Fecha (AAAA-MM-DD)")
        self.entry_fecha = self._entry(der, "Ej. 2025-05-15")

        self._label(der, "Hora (HH:MM)")
        self.entry_hora = self._entry(der, "Ej. 09:00")

        # ── Botones de accion ─────────────────────────────────────────────
        # Fila 1: Agendar | Confirmar
        fila1 = ctk.CTkFrame(form, fg_color="transparent")
        fila1.pack(fill="x", padx=16, pady=(4, 4))

        self.btn_agendar = ctk.CTkButton(
            fila1, text="Agendar",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=VERDE, hover_color="#1E8449",
            text_color="white", height=42, corner_radius=8,
        )
        self.btn_agendar.pack(side="left", padx=(0, 6), expand=True, fill="x")

        # Boton Confirmar disponible para recepcionista y admin
        self.btn_confirmar = ctk.CTkButton(
            fila1, text="Confirmar",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=AZUL, hover_color="#1A6A9A",
            text_color="white", height=42, corner_radius=8,
        )
        self.btn_confirmar.pack(side="left", padx=(6, 0), expand=True, fill="x")

        # Fila 2: Iniciar servicio | Finalizar servicio
        fila2 = ctk.CTkFrame(form, fg_color="transparent")
        fila2.pack(fill="x", padx=16, pady=(0, 4))

        self.btn_iniciar = ctk.CTkButton(
            fila2, text="Iniciar Servicio",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=NARANJA, hover_color="#CA6F1E",
            text_color="white", height=42, corner_radius=8,
        )
        self.btn_iniciar.pack(side="left", padx=(0, 6), expand=True, fill="x")

        self.btn_finalizar = ctk.CTkButton(
            fila2, text="Finalizar Servicio",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=MORADO, hover_color="#7D3C98",
            text_color="white", height=42, corner_radius=8,
        )
        self.btn_finalizar.pack(side="left", padx=(6, 0), expand=True, fill="x")

        # Fila 3: Reprogramar | Cancelar
        fila3 = ctk.CTkFrame(form, fg_color="transparent")
        fila3.pack(fill="x", padx=16, pady=(0, 14))

        self.btn_reprogramar = ctk.CTkButton(
            fila3, text="Reprogramar",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=GOLD, hover_color=GOLD_HOVER,
            text_color="#111111", height=42, corner_radius=8,
        )
        self.btn_reprogramar.pack(side="left", padx=(0, 6), expand=True, fill="x")

        # Boton cancelar con fondo rojizo para que el usuario lo piense dos veces
        self.btn_cancelar = ctk.CTkButton(
            fila3, text="Cancelar Cita",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#3A1A1A", hover_color="#4A2A2A",
            text_color=ROJO, height=42, corner_radius=8,
        )
        self.btn_cancelar.pack(side="left", padx=(6, 0), expand=True, fill="x")

        # Mensaje de resultado — se actualiza desde el controlador
        self.lbl_resultado = ctk.CTkLabel(
            form, text="",
            font=ctk.CTkFont(size=13), text_color=VERDE,
        )
        self.lbl_resultado.pack(pady=(0, 10))

        # ── Leyenda de colores de estado ──────────────────────────────────
        leyenda = ctk.CTkFrame(scroll, fg_color=CARD, corner_radius=10)
        leyenda.pack(fill="x", pady=(0, 14))

        fila_ley = ctk.CTkFrame(leyenda, fg_color="transparent")
        fila_ley.pack(fill="x", padx=16, pady=8)

        # Muestro un badge de color por cada estado posible
        for texto, color in [
            ("PENDIENTE", TEXT_G),
            ("CONFIRMADA", GOLD),
            ("EN SERVICIO", NARANJA),
            ("COMPLETADA", VERDE),
            ("CANCELADA", ROJO),
        ]:
            ctk.CTkLabel(
                fila_ley, text=f"  {texto}  ",
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=color, fg_color=CARD2, corner_radius=6,
            ).pack(side="left", padx=4, ipadx=4, ipady=3)

        # ── Tabla de citas del dia ────────────────────────────────────────
        tabla_card = ctk.CTkFrame(scroll, fg_color=CARD, corner_radius=12)
        tabla_card.pack(fill="both", expand=True, pady=(0, 16))

        ctk.CTkLabel(
            tabla_card, text="Citas de hoy",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=TEXT_W,
        ).pack(anchor="w", padx=16, pady=(12, 2))

        # Instruccion para la recepcionista
        ctk.CTkLabel(
            tabla_card,
            text="Copia el codigo de la tabla, pegalo en el campo 'Codigo de cita' de arriba y presiona el boton que necesites.",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_G,
            wraplength=700,
            justify="left",
        ).pack(anchor="w", padx=16, pady=(0, 8))

        # Textbox monoespaciado para mostrar la tabla de citas
        self.tabla_citas = ctk.CTkTextbox(
            tabla_card, state="disabled",
            fg_color=CARD2, border_color=BORDER, border_width=1,
            text_color=TEXT_W,
            font=ctk.CTkFont(size=11, family="Courier"),
        )
        self.tabla_citas.pack(fill="both", expand=True, padx=16, pady=(0, 14))

    # ── Helpers de construccion ───────────────────────────────────────────────

    def _label(self, parent, texto):
        """Crea una etiqueta gris encima de un campo del formulario."""
        ctk.CTkLabel(
            parent, text=texto,
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=TEXT_G,
        ).pack(anchor="w", pady=(6, 0))

    def _entry(self, parent, placeholder):
        """Crea un campo de texto con estilo oscuro."""
        e = ctk.CTkEntry(
            parent,
            placeholder_text=placeholder,
            placeholder_text_color="#444",
            fg_color=CARD2, border_color=BORDER, border_width=1,
            text_color=TEXT_W, height=38, font=ctk.CTkFont(size=13),
        )
        e.pack(fill="x", pady=(2, 0))
        return e

    def _option_menu_servicios(self, parent):
        """Crea un OptionMenu cargado con los servicios activos de la BD."""
        om = ctk.CTkOptionMenu(
            parent,
            values=["Cargando servicios..."],
            fg_color=CARD2,
            button_color="#333333",
            button_hover_color="#444444",
            text_color=TEXT_W,
            font=ctk.CTkFont(size=13),
            dropdown_fg_color=CARD2,
            dropdown_hover_color="#333333",
            dropdown_text_color=TEXT_W,
            height=38,
        )
        om.pack(fill="x", pady=(2, 0))
        om.set("Cargando servicios...")
        return om

    def get_servicio_id(self):
        """Retorna el ID del servicio actualmente seleccionado en el OptionMenu."""
        nombre = self.opt_servicio.get()
        return self._servicios_map.get(nombre)

    def cargar_servicios(self, servicios):
        """Carga el catálogo de servicios activos."""
        self._servicios_map = {s["nombre"]: s["id"] for s in servicios}
        nombres = list(self._servicios_map.keys()) or ["Sin servicios"]
        self.opt_servicio.configure(values=nombres)
        self.opt_servicio.set(nombres[0])

    # ── Metodos que llama el controlador ─────────────────────────────────────

    def mostrar_resultado(self, mensaje, error=False):
        """Muestra un mensaje de exito en verde o de error en rojo."""
        color = ROJO if error else VERDE
        self.lbl_resultado.configure(text=mensaje, text_color=color)

    def cargar_citas(self, citas):
        """Llena la tabla con la lista de citas del dia incluyendo el nombre del cliente."""
        self.tabla_citas.configure(state="normal")
        self.tabla_citas.delete("1.0", "end")

        if not citas:
            self.tabla_citas.insert("end", "No hay citas registradas hoy.")
        else:
            # Encabezado con todas las columnas que la recepcionista necesita ver
            enc = (
                f"{'CODIGO':<10} "
                f"{'CLIENTE':<20} "
                f"{'SERVICIO':<20} "
                f"{'HORA':<7} "
                f"{'BARBERO':<18} "
                f"{'ESTADO'}\n"
            )
            self.tabla_citas.insert("end", enc)
            self.tabla_citas.insert("end", "─" * 82 + "\n")

            for c in citas:
                estado = c.get("estado", "")
                linea = (
                    f"{c.get('codigo',''):<10} "
                    f"{(c.get('cliente_nombre') or '')[:18]:<20} "
                    f"{c.get('servicio','')[:18]:<20} "
                    f"{c.get('hora','')[:5]:<7} "
                    f"{(c.get('empleado_nombre') or 'Sin asignar')[:16]:<18} "
                    f"{estado.upper()}\n"
                )
                self.tabla_citas.insert("end", linea)

        self.tabla_citas.configure(state="disabled")
