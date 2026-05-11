"""
Vista de Registro — Solo para Administrador y Recepcionista.
Los clientes gestionan sus citas por el chatbot de Telegram,
no necesitan cuenta en el sistema.
"""

import customtkinter as ctk
from app.views.components.tooltip import ToolTip

# ── Paleta de colores ─────────────────────────────────────────────────────────
# Misma paleta del login para mantener consistencia visual
GOLD        = "#C9A020"
GOLD_HOVER  = "#A8841A"
BG          = "#0D0D0D"
PANEL_IZQ   = "#111111"
FIELD_BG    = "#1F1F1F"
FIELD_BORDE = "#2A2A2A"
ROL_ACTIVO  = "#2E2A1A"   # fondo dorado oscuro para el boton de rol seleccionado
TEXT_GRAY   = "#777777"
TEXT_BLANCO = "#F0F0F0"
ROJO        = "#E74C3C"


class RegistroView(ctk.CTkFrame):
    def __init__(self, parent, on_back=None):
        super().__init__(parent, fg_color=BG)
        # Callback que asigna el controlador para procesar el registro
        self.on_registro_callback = None
        # Callback para volver al login (lo pasa MainView como parametro)
        self.on_back = on_back
        # Por defecto el rol seleccionado es administrador
        self._rol_seleccionado = "administrador"
        self._pass_visible = False
        self._construir()

    def _construir(self):
        # ── Layout split igual al login ────────────────────────────────────
        self.columnconfigure(0, weight=4)
        self.columnconfigure(1, weight=5)
        self.rowconfigure(0, weight=1)

        # Panel izquierdo con logo (igual al login)
        panel_izq = ctk.CTkFrame(self, fg_color=PANEL_IZQ, corner_radius=0)
        panel_izq.grid(row=0, column=0, sticky="nsew")
        panel_izq.rowconfigure(0, weight=1)
        panel_izq.rowconfigure(1, weight=1)
        panel_izq.rowconfigure(2, weight=1)
        panel_izq.columnconfigure(0, weight=1)

        ctk.CTkLabel(
            panel_izq, text="BIENVENIDO",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=GOLD,
        ).grid(row=0, column=0, sticky="s", pady=(0, 4))

        logo = ctk.CTkFrame(panel_izq, fg_color="transparent")
        logo.grid(row=1, column=0)
        ctk.CTkLabel(logo, text="BARBERS",
                     font=ctk.CTkFont(size=48, weight="bold"),
                     text_color=TEXT_BLANCO).pack()
        ctk.CTkLabel(logo, text="STUDIO",
                     font=ctk.CTkFont(size=48, weight="bold"),
                     text_color=GOLD).pack()

        ctk.CTkLabel(
            panel_izq, text='"Precisión en cada corte"',
            font=ctk.CTkFont(size=12), text_color=TEXT_GRAY,
        ).grid(row=2, column=0, sticky="n", pady=(8, 0))

        # Panel derecho — formulario con scroll porque tiene muchos campos
        panel_der = ctk.CTkFrame(self, fg_color="#161616", corner_radius=0)
        panel_der.grid(row=0, column=1, sticky="nsew")
        panel_der.rowconfigure(0, weight=1)
        panel_der.columnconfigure(0, weight=1)

        # Scrollable para que todos los campos quepan aunque la ventana sea pequeña
        scroll = ctk.CTkScrollableFrame(panel_der, fg_color="transparent")
        scroll.grid(row=0, column=0, sticky="nsew", padx=60, pady=20)

        # Titulo del formulario
        ctk.CTkLabel(
            scroll, text="Registro de Nuevo\nUsuario",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=TEXT_BLANCO, justify="left",
        ).pack(anchor="w", pady=(0, 4))

        ctk.CTkLabel(
            scroll,
            text="Ingrese los detalles para habilitar un nuevo perfil\nadministrativo o de recepción.",
            font=ctk.CTkFont(size=13), text_color=TEXT_GRAY, justify="left",
        ).pack(anchor="w", pady=(0, 22))

        # NOMBRE COMPLETO
        self._etiqueta("NOMBRE COMPLETO", scroll)
        f_nombre = self._campo(scroll)
        ctk.CTkLabel(f_nombre, text="", text_color=TEXT_GRAY,
                     font=ctk.CTkFont(size=14)).pack(side="left", padx=(14, 0))
        self.entry_nombre = ctk.CTkEntry(
            f_nombre, fg_color="transparent", border_width=0,
            placeholder_text="Ej. Juan Pérez", placeholder_text_color="#444",
            text_color=TEXT_BLANCO, font=ctk.CTkFont(size=14),
        )
        self.entry_nombre.pack(side="left", fill="both", expand=True, padx=10)

        # CORREO ELECTRÓNICO
        self._etiqueta("CORREO ELECTRÓNICO", scroll)
        f_correo = self._campo(scroll)
        ctk.CTkLabel(f_correo, text="", text_color=TEXT_GRAY,
                     font=ctk.CTkFont(size=16)).pack(side="left", padx=(14, 0))
        self.entry_correo = ctk.CTkEntry(
            f_correo, fg_color="transparent", border_width=0,
            placeholder_text="xxxxx@barbers.com", placeholder_text_color="#444",
            text_color=TEXT_BLANCO, font=ctk.CTkFont(size=14),
        )
        self.entry_correo.pack(side="left", fill="both", expand=True, padx=10)
        self._tt_correo = ToolTip(
            self.entry_correo, "Usa un correo único para este usuario."
        )

        # ROL EN EL SISTEMA — botones tipo toggle para elegir entre admin y recepcionista
        self._etiqueta("ROL EN EL SISTEMA", scroll)
        fila_rol = ctk.CTkFrame(scroll, fg_color="transparent")
        fila_rol.pack(fill="x", pady=(4, 18))
        fila_rol.columnconfigure(0, weight=1)
        fila_rol.columnconfigure(1, weight=1)

        # Boton administrador (activo por defecto)
        self._btn_admin = ctk.CTkButton(
            fila_rol, text="ADMINISTRADOR",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=ROL_ACTIVO, hover_color="#3A341F",
            text_color=GOLD, corner_radius=8,
            border_width=1, border_color=GOLD,
            command=lambda: self._elegir_rol("administrador"),
        )
        self._btn_admin.grid(row=0, column=0, padx=(0, 6), sticky="ew", ipady=10)

        # Boton recepcionista (inactivo por defecto)
        self._btn_recep = ctk.CTkButton(
            fila_rol, text="RECEPCIONISTA",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=FIELD_BG, hover_color="#2E2A1A",
            text_color=TEXT_GRAY, corner_radius=8,
            border_width=1, border_color=FIELD_BORDE,
            command=lambda: self._elegir_rol("recepcionista"),
        )
        self._btn_recep.grid(row=0, column=1, padx=(6, 0), sticky="ew", ipady=10)

        # CONTRASEÑA
        self._etiqueta("CONTRASEÑA", scroll)
        f_pass = self._campo(scroll)
        ctk.CTkLabel(f_pass, text="", text_color=TEXT_GRAY,
                     font=ctk.CTkFont(size=14)).pack(side="left", padx=(14, 0))
        self.entry_pass = ctk.CTkEntry(
            f_pass, fg_color="transparent", border_width=0,
            show="•", text_color=TEXT_BLANCO, font=ctk.CTkFont(size=14),
        )
        self.entry_pass.pack(side="left", fill="both", expand=True, padx=10)
        self._tt_pass = ToolTip(
            self.entry_pass, "La contraseña debe tener mínimo 6 caracteres."
        )
        # Boton ver/ocultar contraseña
        self._btn_ver = ctk.CTkButton(
            f_pass, text="Ver", width=44, height=30,
            fg_color="#2A2A2A", hover_color="#333333",
            text_color=TEXT_GRAY, font=ctk.CTkFont(size=11),
            corner_radius=6, command=self._toggle_pass,
        )
        self._btn_ver.pack(side="right", padx=8)

        # CONFIRMAR CONTRASEÑA
        self._etiqueta("CONFIRMAR", scroll)
        f_conf = self._campo(scroll)
        ctk.CTkLabel(f_conf, text="", text_color=TEXT_GRAY,
                     font=ctk.CTkFont(size=14)).pack(side="left", padx=(14, 0))
        self.entry_confirmar = ctk.CTkEntry(
            f_conf, fg_color="transparent", border_width=0,
            show="•", text_color=TEXT_BLANCO, font=ctk.CTkFont(size=14),
        )
        self.entry_confirmar.pack(side="left", fill="both", expand=True, padx=10)

        # Label para mostrar errores o mensajes de exito
        self.lbl_error = ctk.CTkLabel(
            scroll, text="", font=ctk.CTkFont(size=12), text_color=ROJO,
        )
        self.lbl_error.pack(pady=(4, 0))

        # Botón principal para crear la cuenta
        ctk.CTkButton(
            scroll, text="CREAR CUENTA",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=GOLD, hover_color=GOLD_HOVER,
            text_color="#0D0D0D", height=52, corner_radius=8,
            command=self._click_registrar,
        ).pack(fill="x", pady=(12, 6))

        # Enlace para volver al login
        ctk.CTkButton(
            scroll, text="¿Ya tienes una cuenta?  INICIAR SESIÓN",
            font=ctk.CTkFont(size=12),
            fg_color="transparent", hover_color="#1A1A1A",
            text_color=TEXT_GRAY, height=36,
            command=self._volver,
        ).pack(pady=(0, 10))

    # ── Helpers de construccion ───────────────────────────────────────────────

    def _etiqueta(self, texto, parent):
        """Crea una etiqueta dorada encima de un campo del formulario."""
        ctk.CTkLabel(
            parent, text=texto,
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=GOLD,
        ).pack(anchor="w")

    def _campo(self, parent):
        """Crea un contenedor con estilo para un campo de texto."""
        f = ctk.CTkFrame(
            parent, fg_color=FIELD_BG, corner_radius=8,
            border_width=1, border_color=FIELD_BORDE, height=48,
        )
        f.pack(fill="x", pady=(4, 16))
        f.pack_propagate(False)
        return f

    def _elegir_rol(self, rol):
        """Actualiza los botones de rol para resaltar el seleccionado."""
        self._rol_seleccionado = rol
        # Si eligieron administrador, resalto ese boton y apago el otro
        if rol == "administrador":
            self._btn_admin.configure(fg_color=ROL_ACTIVO, text_color=GOLD, border_color=GOLD)
            self._btn_recep.configure(fg_color=FIELD_BG, text_color=TEXT_GRAY, border_color=FIELD_BORDE)
        else:
            self._btn_recep.configure(fg_color=ROL_ACTIVO, text_color=GOLD, border_color=GOLD)
            self._btn_admin.configure(fg_color=FIELD_BG, text_color=TEXT_GRAY, border_color=FIELD_BORDE)

    def _toggle_pass(self):
        """Muestra u oculta la contraseña con el boton Ver/Ocultar."""
        self._pass_visible = not self._pass_visible
        self.entry_pass.configure(show="" if self._pass_visible else "•")
        self._btn_ver.configure(text="Ocultar" if self._pass_visible else "Ver")

    def _click_registrar(self):
        """Recolecta todos los datos del formulario y llama al controlador."""
        if self.on_registro_callback:
            self.on_registro_callback(
                self.entry_nombre.get(),
                self.entry_correo.get(),
                self._rol_seleccionado,
                self.entry_pass.get(),
                self.entry_confirmar.get(),
                "",   # telefono vacio (no aplica para usuarios admin/recep)
            )

    def _volver(self):
        """Ejecuta el callback para regresar al login."""
        if self.on_back:
            self.on_back()

    def mostrar_error(self, mensaje):
        """Muestra un mensaje de error en rojo en el formulario."""
        self.lbl_error.configure(text=mensaje, text_color=ROJO)

    def mostrar_exito(self):
        """Muestra un mensaje de confirmacion cuando el registro fue exitoso."""
        self.lbl_error.configure(text="Usuario creado exitosamente.", text_color=GOLD)
