"""
Componente Sidebar — Menu lateral de navegacion.
Muestra los modulos segun el rol del usuario:
  - administrador: Panel Principal, Agenda, Facturacion,
                   Reportes, Equipo, Gastos
  - recepcionista: Panel Principal, Agenda, Facturacion
"""

import customtkinter as ctk
from app.core.auth import tiene_permiso

# ── Colores ───────────────────────────────────────────────────────────────────
GOLD       = "#C9A020"
BG         = "#111111"
BTN_NORMAL = "transparent"   # fondo de boton inactivo
BTN_HOVER  = "#1F1F1F"       # fondo cuando el mouse pasa encima
BTN_ACTIVO = "#2E2A1A"       # fondo dorado oscuro para el boton seleccionado
TEXT_GRAY  = "#777777"
TEXT_WHITE = "#F0F0F0"
ROJO       = "#C0392B"       # color del boton cerrar sesion

# ── Menú base ──────────────────────────────────────────────────────────────────
MENUS_BASE = [
    ("Panel Principal", "PanelPrincipal"),
    ("Agenda",          "Agenda"),
    ("Facturación",     "Facturacion"),
    ("Reportes",        "Reportes"),
    ("Equipo",          "Equipo"),
    ("Gastos",          "Gastos"),
]

# ── Botones del footer (al fondo del sidebar) ─────────────────────────────────
# El admin tiene acceso al chatbot de Telegram ademas de cerrar sesion
FOOTER_POR_ROL = {
    "administrador": [
        ("Ayuda / FAQ",      "Ayuda"),
        ("Chatbot Telegram", None),    # None = no navega a ninguna pantalla
        ("Cerrar Sesion",    "logout"),
    ],
    "recepcionista": [
        ("Ayuda / FAQ",      "Ayuda"),
        ("Cerrar Sesion",    "logout"),
    ],
}


class Sidebar(ctk.CTkFrame):
    def __init__(self, parent, usuario: dict, on_navigate):
        # Ancho fijo de 220 px para el sidebar — no se puede encoger
        super().__init__(parent, width=220, fg_color=BG, corner_radius=12)
        self.pack_propagate(False)   # evito que se encoja aunque el contenido sea pequeno

        self.on_navigate    = on_navigate  # callback del DashboardView para cambiar modulo
        self._botones       = {}           # guarda referencia a cada boton del menu principal
        self._modulo_activo = None         # modulo que esta actualmente resaltado

        self._construir(usuario)

    # ── Construccion ──────────────────────────────────────────────────────────

    def _construir(self, usuario):
        """Dibuja el sidebar completo segun el rol del usuario."""
        rol = usuario.get("rol", "recepcionista")

        # ── Logo ──────────────────────────────────────────────────────────
        logo_frame = ctk.CTkFrame(self, fg_color="transparent")
        logo_frame.pack(fill="x", padx=16, pady=(20, 0))

        ctk.CTkLabel(
            logo_frame, text="BS",
            font=ctk.CTkFont(size=22),
            text_color=GOLD,
        ).pack(side="left")

        ctk.CTkLabel(
            logo_frame, text="  BARBERS",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=TEXT_WHITE,
        ).pack(side="left")

        ctk.CTkLabel(
            self, text="STUDIO",
            font=ctk.CTkFont(size=9),
            text_color=TEXT_GRAY,
        ).pack(anchor="w", padx=40, pady=(0, 4))

        # Separador horizontal
        ctk.CTkFrame(self, height=1, fg_color="#222222").pack(fill="x", padx=14, pady=(6, 12))

        # Etiqueta de seccion del menu
        ctk.CTkLabel(
            self, text="MENÚ",
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color=TEXT_GRAY,
        ).pack(anchor="w", padx=18, pady=(0, 4))

        # ── Botones del menu principal ────────────────────────────────────
        # Cargo solo los modulos que corresponden al rol del usuario
        opciones = [
            (texto, modulo)
            for texto, modulo in MENUS_BASE
            if tiene_permiso(rol, modulo)
        ]
        for texto, modulo in opciones:
            btn = ctk.CTkButton(
                self,
                text=texto,
                anchor="w",
                font=ctk.CTkFont(size=13),
                fg_color=BTN_NORMAL,
                hover_color=BTN_HOVER,
                text_color=TEXT_GRAY,
                corner_radius=8,
                height=42,
                # Uso m=modulo para capturar el valor correcto en el closure del for
                command=lambda m=modulo: self._navegar(m),
            )
            btn.pack(fill="x", padx=10, pady=2)
            # Guardo referencia para poder resaltar/quitar resalte despues
            self._botones[modulo] = btn

        # ── Spacer — empuja el footer hacia la parte inferior ─────────────
        ctk.CTkFrame(self, fg_color="transparent").pack(expand=True, fill="y")

        # Separador antes del footer
        ctk.CTkFrame(self, height=1, fg_color="#222222").pack(fill="x", padx=14, pady=(0, 8))

        # ── Botones del footer (logout, chatbot) ──────────────────────────
        acciones = FOOTER_POR_ROL.get(rol, [])
        for texto, modulo in acciones:
            # El boton de cerrar sesion tiene fondo rojizo para que resalte
            color = "#3A1A1A" if modulo == "logout" else BTN_NORMAL
            texto_color = ROJO if modulo == "logout" else TEXT_GRAY
            btn = ctk.CTkButton(
                self,
                text=texto,
                anchor="w",
                font=ctk.CTkFont(size=12),
                fg_color=color,
                hover_color=BTN_HOVER,
                text_color=texto_color,
                corner_radius=8,
                height=38,
                command=lambda m=modulo: self._navegar(m),
            )
            btn.pack(fill="x", padx=10, pady=2)

        # ── Perfil del usuario al pie del sidebar ─────────────────────────
        ctk.CTkFrame(self, height=1, fg_color="#222222").pack(fill="x", padx=14, pady=(8, 6))

        perfil = ctk.CTkFrame(self, fg_color="transparent")
        perfil.pack(fill="x", padx=14, pady=(0, 16))

        # Circulo dorado con la inicial del nombre del usuario
        inicial = usuario.get("nombre", "U")[0].upper()
        circulo = ctk.CTkFrame(perfil, fg_color=GOLD, corner_radius=18, width=36, height=36)
        circulo.pack(side="left", padx=(0, 8))
        circulo.pack_propagate(False)
        ctk.CTkLabel(
            circulo, text=inicial,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#0D0D0D",
        ).pack(expand=True)

        # Nombre y rol del usuario
        info = ctk.CTkFrame(perfil, fg_color="transparent")
        info.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(
            info,
            text=usuario.get("nombre", "")[:18],  # limito a 18 caracteres para que quepa
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=TEXT_WHITE, anchor="w",
        ).pack(anchor="w")
        ctk.CTkLabel(
            info,
            text=rol.capitalize(),
            font=ctk.CTkFont(size=10),
            text_color=TEXT_GRAY, anchor="w",
        ).pack(anchor="w")

    # ── Navegacion ────────────────────────────────────────────────────────────

    def _navegar(self, modulo):
        """Resalta el boton activo y notifica al dashboard para cargar el modulo."""
        # Si el modulo es None (como Chatbot Telegram), no hago nada
        if modulo is None:
            return

        # Quito el resalte del modulo anterior si habia uno
        if self._modulo_activo and self._modulo_activo in self._botones:
            self._botones[self._modulo_activo].configure(
                fg_color=BTN_NORMAL,
                text_color=TEXT_GRAY,
            )

        # Resalto el nuevo modulo con fondo dorado (solo si no es logout)
        if modulo != "logout":
            self._modulo_activo = modulo
            if modulo in self._botones:
                self._botones[modulo].configure(
                    fg_color=BTN_ACTIVO,
                    text_color=GOLD,
                )

        # Notifico al DashboardView para que cargue el modulo correspondiente
        if self.on_navigate:
            self.on_navigate(modulo)

    def marcar_activo(self, modulo):
        """Marca un boton como activo desde el exterior — lo usa el dashboard al inicio."""
        self._navegar(modulo)
