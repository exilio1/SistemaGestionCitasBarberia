"""
Modal Nueva Cita — CTkToplevel
Formulario para registrar una cita nueva desde la Agenda.
Pasos: 1) Datos del cliente  2) Barbero  3) Servicio  4) Fecha y hora
"""

import customtkinter as ctk
from datetime import date
from app.models.cita_model import CitaModel
from app.models.empleado_model import EmpleadoModel
from app.models.cliente_model import ClienteModel
from app.models.servicio_model import ServicioModel

# ── Paleta ────────────────────────────────────────────────────────────────────
GOLD        = "#C9A020"
GOLD_HOVER  = "#A8841A"
BG          = "#161616"
CARD        = "#1F1F1F"
CARD2       = "#242424"
BORDER      = "#2A2A2A"
TEXT_W      = "#F0F0F0"
TEXT_G      = "#777777"
VERDE       = "#27AE60"
ROJO        = "#E74C3C"


class ModalNuevaCita(ctk.CTkToplevel):
    """Ventana emergente para agendar una cita nueva desde la agenda."""

    def __init__(self, parent, usuario: dict):
        super().__init__(parent)

        self._usuario        = usuario
        # Instancio los modelos que necesito para guardar la cita
        self._modelo_cita    = CitaModel()
        self._modelo_emp     = EmpleadoModel()
        self._modelo_cli     = ClienteModel()
        self._modelo_servicio = ServicioModel()

        # Callback que el controlador asigna para refrescar la agenda al cerrar
        self.on_cita_creada = None

        # Estado interno: guarda el barbero y servicio seleccionados por el usuario
        self._barbero_sel  = None   # dict del barbero elegido
        self._servicio_sel = None   # dict del servicio elegido (id, nombre, precio)

        # Configuro la ventana modal
        self.title("Nueva Cita")
        self.geometry("620x700")
        self.resizable(False, False)
        self.configure(fg_color=BG)

        self._construir()

    # ── Construccion del modal ────────────────────────────────────────────────

    def _construir(self):
        # Titulo del modal
        ctk.CTkLabel(
            self, text="NUEVA CITA",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=TEXT_W,
        ).pack(anchor="w", padx=24, pady=(20, 4))

        ctk.CTkLabel(
            self, text="Completa los datos para agendar la cita",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_G,
        ).pack(anchor="w", padx=24, pady=(0, 16))

        # Scrollable para que el formulario quepa en pantallas pequeñas
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(expand=True, fill="both", padx=16, pady=0)

        # ── SECCION 1: Datos del cliente ──────────────────────────────────
        self._seccion(scroll, "1. DATOS DEL CLIENTE")

        fila1 = ctk.CTkFrame(scroll, fg_color="transparent")
        fila1.pack(fill="x", pady=(4, 12))
        fila1.columnconfigure(0, weight=1)
        fila1.columnconfigure(1, weight=1)

        # Nombre y cedula en la misma fila (dos columnas)
        self._label(fila1, "Nombre completo",         col=0, row=0)
        self._label(fila1, "Cedula (documento)",      col=1, row=0)
        self.entry_nombre   = self._entry_col(fila1, "Ej. Juan Pérez",    col=0, row=1)
        self.entry_cedula   = self._entry_col(fila1, "Ej. 1000234567",    col=1, row=1)

        # Telefono ocupa las dos columnas
        fila1.columnconfigure(0, weight=1)
        fila1.columnconfigure(1, weight=1)
        self._label_full(fila1, "Teléfono (opcional)", row=2)
        self.entry_telefono = self._entry_full(fila1, "Ej. 3001234567", row=3)

        # ── SECCION 2: Elegir barbero (tarjetas clickeables) ──────────────
        self._seccion(scroll, "2. SELECCIONAR BARBERO")

        # Las tarjetas se generan dinamicamente con los barberos de la BD
        self.frame_barberos = ctk.CTkFrame(scroll, fg_color="transparent")
        self.frame_barberos.pack(fill="x", pady=(4, 12))

        self._cargar_tarjetas_barberos()

        # ── SECCION 3: Elegir servicio (tarjetas clickeables) ─────────────
        self._seccion(scroll, "3. SELECCIONAR SERVICIO")

        self.frame_servicios = ctk.CTkFrame(scroll, fg_color="transparent")
        self.frame_servicios.pack(fill="x", pady=(4, 12))

        self._cargar_tarjetas_servicios()

        # ── SECCION 4: Fecha y hora ───────────────────────────────────────
        self._seccion(scroll, "4. FECHA Y HORA")

        fila4 = ctk.CTkFrame(scroll, fg_color="transparent")
        fila4.pack(fill="x", pady=(4, 12))
        fila4.columnconfigure(0, weight=1)
        fila4.columnconfigure(1, weight=1)

        self._label(fila4, "Fecha (AAAA-MM-DD)", col=0, row=0)
        self._label(fila4, "Hora",               col=1, row=0)

        # Por defecto pongo la fecha de hoy
        self.entry_fecha = self._entry_col(fila4, date.today().isoformat(), col=0, row=1)
        self.entry_fecha.insert(0, date.today().isoformat())

        # Desplegable con las horas base — se actualiza segun el barbero y fecha
        horas_base = [f"{h:02d}:{m:02d}" for h in range(8, 19) for m in (0, 30)]
        self.opt_hora = ctk.CTkOptionMenu(
            fila4,
            values=horas_base,
            fg_color=CARD, button_color="#333333",
            button_hover_color="#444444",
            text_color=TEXT_W,
            font=ctk.CTkFont(size=13),
            dropdown_fg_color=CARD,
            dropdown_hover_color="#333333",
            dropdown_text_color=TEXT_W,
        )
        self.opt_hora.grid(row=1, column=1, sticky="ew", padx=(4, 0))
        self.opt_hora.set("09:00")

        # Boton para recalcular horas disponibles segun barbero y fecha
        ctk.CTkButton(
            scroll, text="Ver horas disponibles",
            font=ctk.CTkFont(size=11),
            fg_color="#2A2A2A", hover_color="#333333",
            text_color=TEXT_G, height=32,
            command=self._actualizar_horas,
        ).pack(anchor="w", pady=(0, 8))

        # ── SECCION 5: Observaciones ──────────────────────────────────────
        self._seccion(scroll, "5. OBSERVACIONES (opcional)")
        self.entry_obs = ctk.CTkTextbox(
            scroll, height=60, fg_color=CARD,
            border_color=BORDER, border_width=1,
            text_color=TEXT_W, font=ctk.CTkFont(size=13),
        )
        self.entry_obs.pack(fill="x", pady=(4, 12))

        # Mensaje de error o exito
        self.lbl_msg = ctk.CTkLabel(
            scroll, text="",
            font=ctk.CTkFont(size=12),
            text_color=ROJO,
        )
        self.lbl_msg.pack(pady=(0, 4))

        # ── Botones de accion ─────────────────────────────────────────────
        fila_btns = ctk.CTkFrame(self, fg_color="transparent")
        fila_btns.pack(fill="x", padx=24, pady=(8, 20))

        ctk.CTkButton(
            fila_btns, text="CANCELAR",
            font=ctk.CTkFont(size=13),
            fg_color="#2A2A2A", hover_color="#333333",
            text_color=TEXT_G, height=44, corner_radius=8,
            command=self.destroy,
        ).pack(side="left", expand=True, fill="x", padx=(0, 6))

        ctk.CTkButton(
            fila_btns, text="AGENDAR CITA",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=GOLD, hover_color=GOLD_HOVER,
            text_color="#0D0D0D", height=44, corner_radius=8,
            command=self._guardar,
        ).pack(side="left", expand=True, fill="x", padx=(6, 0))

    # ── Helpers de construccion ───────────────────────────────────────────────

    def _seccion(self, parent, texto):
        """Dibuja el titulo de una seccion con una linea separadora a la derecha."""
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(fill="x", pady=(8, 2))
        ctk.CTkLabel(
            f, text=texto,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=GOLD,
        ).pack(side="left")
        ctk.CTkFrame(f, fg_color=BORDER, height=1).pack(
            side="left", fill="x", expand=True, padx=(8, 0), pady=6
        )

    def _label(self, parent, texto, col=0, row=0):
        """Crea una etiqueta de campo usando grid (para formularios de dos columnas)."""
        ctk.CTkLabel(
            parent, text=texto,
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=TEXT_G,
        ).grid(row=row, column=col, sticky="w", padx=(0 if col == 0 else 4, 4), pady=(4, 0))

    def _label_full(self, parent, texto, row=0):
        """Etiqueta que ocupa las dos columnas (columnspan=2)."""
        ctk.CTkLabel(
            parent, text=texto,
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=TEXT_G,
        ).grid(row=row, column=0, columnspan=2, sticky="w", padx=(0, 4), pady=(8, 0))

    def _entry_col(self, parent, placeholder, col=0, row=1):
        """Entry posicionado en una columna especifica del grid."""
        e = ctk.CTkEntry(
            parent,
            placeholder_text=placeholder,
            placeholder_text_color="#444",
            fg_color=CARD, border_color=BORDER, border_width=1,
            text_color=TEXT_W, font=ctk.CTkFont(size=13),
            height=38,
        )
        e.grid(row=row, column=col, sticky="ew",
               padx=(0 if col == 0 else 4, 0), pady=(2, 0))
        return e

    def _entry_full(self, parent, placeholder, row=1):
        """Entry que ocupa las dos columnas del grid."""
        e = ctk.CTkEntry(
            parent,
            placeholder_text=placeholder,
            placeholder_text_color="#444",
            fg_color=CARD, border_color=BORDER, border_width=1,
            text_color=TEXT_W, font=ctk.CTkFont(size=13),
            height=38,
        )
        e.grid(row=row, column=0, columnspan=2, sticky="ew",
               padx=0, pady=(2, 0))
        return e

    def _entry(self, parent, placeholder):
        """Entry generico sin grilla — llamado internamente si se necesita."""
        return self._entry_col(parent, placeholder)

    # ── Tarjetas de barberos ──────────────────────────────────────────────────

    def _cargar_tarjetas_barberos(self):
        """Dibuja una tarjeta clickeable por cada barbero activo en la BD."""
        # Limpio las tarjetas anteriores si las habia
        for w in self.frame_barberos.winfo_children():
            w.destroy()

        empleados = self._modelo_emp.listar()

        if not empleados:
            ctk.CTkLabel(
                self.frame_barberos,
                text="No hay barberos registrados.",
                text_color=TEXT_G, font=ctk.CTkFont(size=12),
            ).pack(pady=8)
            return

        # Organizo las tarjetas en filas de 3
        fila = None
        for i, emp in enumerate(empleados):
            if i % 3 == 0:
                fila = ctk.CTkFrame(self.frame_barberos, fg_color="transparent")
                fila.pack(fill="x", pady=2)
                for c in range(3):
                    fila.columnconfigure(c, weight=1)

            col = i % 3
            tarjeta = ctk.CTkFrame(
                fila, fg_color=CARD, corner_radius=8,
                border_width=1, border_color=BORDER,
            )
            tarjeta.grid(row=0, column=col, padx=3, sticky="ew")

            # Circulo con la inicial del barbero
            inicial = emp.get("nombre", "?")[0].upper()
            circulo = ctk.CTkFrame(tarjeta, fg_color="#2A2A2A", corner_radius=18, width=36, height=36)
            circulo.pack(pady=(10, 4))
            circulo.pack_propagate(False)
            ctk.CTkLabel(
                circulo, text=inicial,
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=TEXT_W,
            ).pack(expand=True)

            ctk.CTkLabel(
                tarjeta, text=emp.get("nombre", ""),
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=TEXT_W,
            ).pack()
            ctk.CTkLabel(
                tarjeta, text=emp.get("especialidad", "").upper(),
                font=ctk.CTkFont(size=9),
                text_color=TEXT_G,
            ).pack(pady=(0, 8))

            # Guardo el dict del empleado en la tarjeta para recuperarlo al hacer clic
            tarjeta._emp = emp
            tarjeta.bind("<Button-1>", lambda e, t=tarjeta: self._seleccionar_barbero(t))
            # Propago el clic a los hijos para que funcione al hacer clic en cualquier parte
            for child in tarjeta.winfo_children():
                child.bind("<Button-1>", lambda e, t=tarjeta: self._seleccionar_barbero(t))

    def _seleccionar_barbero(self, tarjeta_sel):
        """Resalta la tarjeta del barbero elegido y guarda su seleccion."""
        # Quito el resalte de todas las tarjetas
        for fila in self.frame_barberos.winfo_children():
            for tarjeta in fila.winfo_children():
                tarjeta.configure(fg_color=CARD, border_color=BORDER)

        # Resalto la tarjeta elegida con borde dorado
        tarjeta_sel.configure(fg_color="#2E2A1A", border_color=GOLD)
        self._barbero_sel = tarjeta_sel._emp

        # Recalculo las horas disponibles con el nuevo barbero
        self._actualizar_horas()

    # ── Tarjetas de servicios ─────────────────────────────────────────────────

    def _cargar_tarjetas_servicios(self):
        """Dibuja una tarjeta clickeable por cada servicio activo en la BD."""
        # Limpio tarjetas anteriores
        for w in self.frame_servicios.winfo_children():
            w.destroy()

        servicios = self._modelo_servicio.listar(solo_activos=True)

        if not servicios:
            ctk.CTkLabel(
                self.frame_servicios,
                text="No hay servicios registrados.",
                text_color=TEXT_G, font=ctk.CTkFont(size=12),
            ).pack(pady=8)
            return

        # Organizo en filas de 3
        fila = None
        for i, srv in enumerate(servicios):
            if i % 3 == 0:
                fila = ctk.CTkFrame(self.frame_servicios, fg_color="transparent")
                fila.pack(fill="x", pady=2)
                for c in range(3):
                    fila.columnconfigure(c, weight=1)

            col = i % 3
            tarjeta = ctk.CTkFrame(
                fila, fg_color=CARD, corner_radius=8,
                border_width=1, border_color=BORDER,
            )
            tarjeta.grid(row=0, column=col, padx=3, sticky="ew")

            # Nombre y precio del servicio
            ctk.CTkLabel(
                tarjeta, text=srv["nombre"],
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=TEXT_W, wraplength=140,
            ).pack(padx=8, pady=(10, 2))
            ctk.CTkLabel(
                tarjeta, text=f"$ {srv['precio']:,.0f}",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=GOLD,
            ).pack(pady=(0, 8))

            # Guardo el dict completo del servicio para tener el id al guardar
            tarjeta._servicio = srv
            tarjeta.bind("<Button-1>", lambda e, t=tarjeta: self._seleccionar_servicio(t))
            for child in tarjeta.winfo_children():
                child.bind("<Button-1>", lambda e, t=tarjeta: self._seleccionar_servicio(t))

    def _seleccionar_servicio(self, tarjeta_sel):
        """Resalta la tarjeta del servicio elegido y guarda su dict."""
        # Quito el resalte de todas las tarjetas de servicios
        for fila in self.frame_servicios.winfo_children():
            for tarjeta in fila.winfo_children():
                tarjeta.configure(fg_color=CARD, border_color=BORDER)
        tarjeta_sel.configure(fg_color="#1A2A1A", border_color=VERDE)
        # Guardo el dict completo — necesito el id al crear la cita
        self._servicio_sel = tarjeta_sel._servicio

    # ── Horas disponibles ─────────────────────────────────────────────────────

    def _actualizar_horas(self):
        """Recalcula las horas libres del barbero para la fecha seleccionada."""
        fecha = self.entry_fecha.get().strip()
        emp_id = self._barbero_sel.get("id") if self._barbero_sel else None

        if not fecha:
            return

        try:
            # Consulto al modelo las horas que no estan ocupadas para ese barbero y fecha
            horas = self._modelo_cita.horarios_disponibles(fecha, emp_id)
            if not horas:
                horas = ["Sin horas disponibles"]
            self.opt_hora.configure(values=horas)
            self.opt_hora.set(horas[0])
        except Exception:
            pass  # si falla, dejo las horas por defecto sin mostrar error

    # ── Guardar cita ──────────────────────────────────────────────────────────

    def _guardar(self):
        """Valida el formulario y guarda la cita en la base de datos."""
        # Recojo todos los datos del formulario
        nombre   = self.entry_nombre.get().strip()
        cedula   = self.entry_cedula.get().strip()
        telefono = self.entry_telefono.get().strip()
        fecha    = self.entry_fecha.get().strip()
        hora     = self.opt_hora.get()
        obs      = self.entry_obs.get("1.0", "end").strip()

        # Valido los campos obligatorios antes de guardar
        if not nombre:
            self._mostrar_error("Ingresa el nombre del cliente.")
            return
        if not cedula:
            self._mostrar_error("Ingresa la cedula del cliente.")
            return
        if not self._barbero_sel:
            self._mostrar_error("Selecciona un barbero.")
            return
        if not self._servicio_sel:
            self._mostrar_error("Selecciona un servicio.")
            return
        if not fecha:
            self._mostrar_error("Ingresa la fecha.")
            return
        if hora == "Sin horas disponibles":
            self._mostrar_error("No hay horas disponibles para ese día.")
            return

        # Busco o creo el cliente usando la cedula como identificador principal
        try:
            cliente_id = self._modelo_cli.obtener_o_crear(nombre, cedula, telefono)
        except Exception as e:
            self._mostrar_error(f"Error al buscar cliente: {e}")
            return

        # Creo la cita — el modelo genera el codigo UUID automaticamente
        try:
            codigo = self._modelo_cita.crear(
                cliente_id   = cliente_id,
                empleado_id  = self._barbero_sel["id"],
                servicio_id  = self._servicio_sel["id"],
                fecha        = fecha,
                hora         = hora,
                observaciones= obs or None,
            )
        except Exception as e:
            self._mostrar_error(f"Error al guardar cita: {e}")
            return

        # Si todo salio bien, muestro el codigo y cierro el modal despues de 1.5s
        self.lbl_msg.configure(
            text=f"Cita creada exitosamente. Código: {codigo}",
            text_color=VERDE,
        )
        self.after(1500, self._cerrar_y_refrescar)

    def _cerrar_y_refrescar(self):
        """Cierra el modal y notifica al controlador para que refresque la agenda."""
        if self.on_cita_creada:
            self.on_cita_creada()
        self.destroy()

    def _mostrar_error(self, msg):
        """Muestra un mensaje de error en rojo en el formulario."""
        self.lbl_msg.configure(text=msg, text_color=ROJO)
