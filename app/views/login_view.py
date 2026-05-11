"""
Vista de Login — diseño split izquierda/derecha como en Figma.
Izquierda: imagen de fondo con logo y slogan.
Derecha: formulario de acceso.
"""

import customtkinter as ctk
from app.views.components.tooltip import ToolTip

# ── Paleta de colores ─────────────────────────────────────────────────────────
# Defino todos los colores aqui para cambiarlos facil en un solo lugar
GOLD        = "#C9A020"   # dorado principal (botones, acentos)
GOLD_HOVER  = "#A8841A"   # dorado mas oscuro para el hover
BG          = "#0D0D0D"   # fondo general muy oscuro
PANEL_IZQ   = "#111111"   # fondo del panel izquierdo
PANEL_DER   = "#161616"   # fondo del panel derecho (ligeramente mas claro)
CARD_BG     = "#1C1C1C"   # fondo de la caja de acceso rapido
FIELD_BG    = "#1F1F1F"   # fondo de los campos de texto
FIELD_BORDE = "#2A2A2A"   # borde de los campos
TEXT_GRAY   = "#777777"   # texto secundario gris
TEXT_BLANCO = "#F0F0F0"   # texto principal blanco suave
ROJO        = "#E74C3C"   # color para mensajes de error


class LoginView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=BG)
        # Callbacks que asigna el controlador cuando se crea la vista
        self.on_login_callback = None
        self.on_registro_callback = None
        # Controla si la contraseña se muestra en texto plano o con puntos
        self._pass_visible = False
        self._construir()

    def _construir(self):
        # ── Layout principal: dos columnas ────────────────────────────────
        # El panel derecho es mas ancho porque tiene el formulario
        self.columnconfigure(0, weight=4)   # panel izquierdo (mas ancho)
        self.columnconfigure(1, weight=5)   # panel derecho con formulario
        self.rowconfigure(0, weight=1)

        # ── Panel izquierdo — fondo oscuro con logo ───────────────────────
        panel_izq = ctk.CTkFrame(self, fg_color=PANEL_IZQ, corner_radius=0)
        panel_izq.grid(row=0, column=0, sticky="nsew")

        # Configuro tres filas para centrar el logo verticalmente
        panel_izq.rowconfigure(0, weight=1)
        panel_izq.rowconfigure(1, weight=1)
        panel_izq.rowconfigure(2, weight=1)
        panel_izq.columnconfigure(0, weight=1)

        # Texto pequeño encima del logo
        ctk.CTkLabel(
            panel_izq, text="BIENVENIDO",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=GOLD,
        ).grid(row=0, column=0, sticky="s", pady=(0, 4))

        # Contenedor del logo para apilar los dos textos
        logo_frame = ctk.CTkFrame(panel_izq, fg_color="transparent")
        logo_frame.grid(row=1, column=0)

        ctk.CTkLabel(
            logo_frame, text="BARBERS",
            font=ctk.CTkFont(size=48, weight="bold"),
            text_color=TEXT_BLANCO,
        ).pack()
        ctk.CTkLabel(
            logo_frame, text="STUDIO",
            font=ctk.CTkFont(size=48, weight="bold"),
            text_color=GOLD,
        ).pack()

        # Slogan debajo del logo
        ctk.CTkLabel(
            panel_izq, text='"Precisión en cada corte"',
            font=ctk.CTkFont(size=12),
            text_color=TEXT_GRAY,
        ).grid(row=2, column=0, sticky="n", pady=(8, 0))

        # Línea decorativa vertical que separa los paneles
        sep = ctk.CTkFrame(self, fg_color="#2A2A2A", width=1, corner_radius=0)
        sep.grid(row=0, column=0, sticky="nse")

        # ── Panel derecho — formulario de login ───────────────────────────
        panel_der = ctk.CTkFrame(self, fg_color=PANEL_DER, corner_radius=0)
        panel_der.grid(row=0, column=1, sticky="nsew")

        # Centro el formulario verticalmente dentro del panel
        panel_der.rowconfigure(0, weight=1)
        panel_der.columnconfigure(0, weight=1)

        formulario = ctk.CTkFrame(panel_der, fg_color="transparent")
        formulario.grid(row=0, column=0, padx=60)

        # Titulo del formulario
        ctk.CTkLabel(
            formulario, text="Bienvenido",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=TEXT_BLANCO,
        ).pack(anchor="w", pady=(0, 6))

        ctk.CTkLabel(
            formulario, text="Ingrese sus credenciales para acceder al portal.",
            font=ctk.CTkFont(size=13),
            text_color=TEXT_GRAY,
        ).pack(anchor="w", pady=(0, 28))

        # Campo correo electrónico
        ctk.CTkLabel(
            formulario, text="CORREO ELECTRÓNICO",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=TEXT_GRAY,
        ).pack(anchor="w")

        # Contenedor del campo para darle el estilo de borde personalizado
        campo_correo = ctk.CTkFrame(
            formulario, fg_color=FIELD_BG, corner_radius=8,
            border_width=1, border_color=FIELD_BORDE, height=48,
        )
        campo_correo.pack(fill="x", pady=(4, 18))
        campo_correo.pack_propagate(False)

        ctk.CTkLabel(
            campo_correo, text="", text_color=TEXT_GRAY,
            font=ctk.CTkFont(size=16),
        ).pack(side="left", padx=(14, 0))

        # Entry donde el usuario escribe su correo
        self.entry_email = ctk.CTkEntry(
            campo_correo, fg_color="transparent", border_width=0,
            placeholder_text="nombre@ejemplo.com",
            placeholder_text_color="#444444",
            text_color=TEXT_BLANCO, font=ctk.CTkFont(size=14),
        )
        self.entry_email.pack(side="left", fill="both", expand=True, padx=10)

        # Campo contraseña
        ctk.CTkLabel(
            formulario, text="CONTRASEÑA",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=TEXT_GRAY,
        ).pack(anchor="w")

        campo_pass = ctk.CTkFrame(
            formulario, fg_color=FIELD_BG, corner_radius=8,
            border_width=1, border_color=FIELD_BORDE, height=48,
        )
        campo_pass.pack(fill="x", pady=(4, 22))
        campo_pass.pack_propagate(False)

        ctk.CTkLabel(
            campo_pass, text="", text_color=TEXT_GRAY,
            font=ctk.CTkFont(size=15),
        ).pack(side="left", padx=(14, 0))

        # Contraseña oculta por defecto con puntos
        self.entry_pass = ctk.CTkEntry(
            campo_pass, fg_color="transparent", border_width=0,
            show="•", text_color=TEXT_BLANCO, font=ctk.CTkFont(size=14),
        )
        self.entry_pass.pack(side="left", fill="both", expand=True, padx=10)

        # Boton para mostrar/ocultar la contraseña
        self._btn_ver = ctk.CTkButton(
            campo_pass, text="Ver", width=44, height=30,
            fg_color="#2A2A2A", hover_color="#333333",
            text_color=TEXT_GRAY, font=ctk.CTkFont(size=11),
            corner_radius=6, command=self._toggle_pass,
        )
        self._btn_ver.pack(side="right", padx=8)

        # Mensaje de error — empieza vacío, lo llena el controlador si falla el login
        self.lbl_error = ctk.CTkLabel(
            formulario, text="",
            font=ctk.CTkFont(size=12),
            text_color=ROJO,
        )
        self.lbl_error.pack(pady=(0, 8))

        # Botón principal de inicio de sesión
        ctk.CTkButton(
            formulario, text="INICIAR SESIÓN",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=GOLD, hover_color=GOLD_HOVER,
            text_color="#0D0D0D", height=52, corner_radius=8,
            command=self._click_login,
        ).pack(fill="x", pady=(0, 20))
        self._tt_email = ToolTip(
            self.entry_email, "Escribe el correo que registraste en el sistema."
        )
        self._tt_pass = ToolTip(
            self.entry_pass, "Escribe tu contraseña para entrar al sistema."
        )

        # Caja de acceso rápido por rol (referencia visual para demos)
        caja_rapida = ctk.CTkFrame(
            formulario, fg_color="#1A1A1A", corner_radius=8,
            border_width=1, border_color="#2A2A2A",
        )
        caja_rapida.pack(fill="x", pady=(0, 20))

        fila_titulo = ctk.CTkFrame(caja_rapida, fg_color="transparent")
        fila_titulo.pack(fill="x", padx=14, pady=(10, 6))

        ctk.CTkLabel(
            fila_titulo, text="ACCESO RAPIDO POR ROL",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=GOLD,
        ).pack(side="left")

        # Muestro los correos de prueba para admin y secretaria
        for rol, correo in [("Admin:", "admin@barbers.com"), ("Recepcionista:", "recep@barbers.com")]:
            fila = ctk.CTkFrame(caja_rapida, fg_color="transparent")
            fila.pack(fill="x", padx=14, pady=1)
            ctk.CTkLabel(
                fila, text=rol, width=70,
                font=ctk.CTkFont(size=12),
                text_color=TEXT_GRAY, anchor="w",
            ).pack(side="left")
            ctk.CTkLabel(
                fila, text=correo,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#3A8FD4",
                fg_color="#1A2A3A", corner_radius=4,
            ).pack(side="left", padx=6, pady=2, ipadx=8, ipady=2)

        ctk.CTkFrame(caja_rapida, height=6, fg_color="transparent").pack()

        # Enlace para ir a la pantalla de registro
        pie = ctk.CTkFrame(formulario, fg_color="transparent")
        pie.pack()
        ctk.CTkLabel(
            pie, text="¿No tienes una cuenta?",
            font=ctk.CTkFont(size=13),
            text_color=TEXT_GRAY,
        ).pack(side="left")
        lbl_reg = ctk.CTkLabel(
            pie, text="  Registrarse",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=GOLD, cursor="hand2",
        )
        lbl_reg.pack(side="left")
        # Al hacer clic en el texto llamo al callback de registro
        lbl_reg.bind("<Button-1>", lambda e: self._click_registro())

        # Pie de página con links de utilidad (visual)
        ctk.CTkFrame(formulario, height=20, fg_color="transparent").pack()
        ctk.CTkLabel(
            formulario,
            text="Términos    Privacidad    Soporte",
            font=ctk.CTkFont(size=11),
            text_color="#444444",
        ).pack()

    # ── Métodos internos ──────────────────────────────────────────────────────

    def _toggle_pass(self):
        """Alterna entre mostrar la contraseña en texto o en puntos."""
        self._pass_visible = not self._pass_visible
        self.entry_pass.configure(show="" if self._pass_visible else "•")
        self._btn_ver.configure(text="Ocultar" if self._pass_visible else "Ver")

    def _click_login(self):
        """Llama al callback del controlador pasando correo y contraseña."""
        if self.on_login_callback:
            self.on_login_callback(self.entry_email.get(), self.entry_pass.get())

    def _click_registro(self):
        """Llama al callback para navegar a la pantalla de registro."""
        if self.on_registro_callback:
            self.on_registro_callback()

    def mostrar_error(self, mensaje):
        """Muestra un mensaje de error debajo de los campos."""
        self.lbl_error.configure(text=mensaje)
