"""
Vista Dashboard — Pantalla principal despues del login.
Contiene el sidebar de navegacion y el area de contenido.
Carga el modulo correcto segun el boton que presione el usuario.
"""

import importlib
import customtkinter as ctk
from app.core.auth import tiene_permiso
from app.views.components.sidebar import Sidebar
from app.views.components.header import Header


# ── Mapa de modulos ───────────────────────────────────────────────────────────
# Cada entrada: nombre → (modulo_vista, clase_vista, modulo_ctrl, clase_ctrl)
# El nombre debe coincidir exactamente con los valores en MENUS_POR_ROL del sidebar.
# Uso importlib para cargar las clases de forma dinamica sin importarlas todas al inicio.

PANTALLAS = {
    # ── Modulos principales ───────────────────────────────────────────────
    "PanelPrincipal": (
        "app.views.screens.panel_principal_view",    "PanelPrincipalView",
        "app.controllers.panel_principal_controller", "PanelPrincipalController",
    ),
    "Agenda": (
        "app.views.screens.agenda_view",             "AgendaView",
        "app.controllers.agenda_controller",         "AgendaController",
    ),
    "Facturacion": (
        "app.views.screens.facturacion_view",        "FacturacionView",
        "app.controllers.facturacion_controller",    "FacturacionController",
    ),
    "Reportes": (
        "app.views.screens.reportes_view",           "ReportesView",
        "app.controllers.reportes_controller",       "ReportesController",
    ),
    "Equipo": (
        "app.views.screens.equipo_view",             "EquipoView",
        "app.controllers.equipo_controller",         "EquipoController",
    ),
    "Gastos": (
        "app.views.screens.gastos_view",             "GastosView",
        "app.controllers.gastos_controller",         "GastosController",
    ),
    "Ayuda": (
        "app.views.screens.ayuda_view",              "AyudaView",
        "app.controllers.ayuda_controller",          "AyudaController",
    ),

    "Servicios": (
        "app.views.screens.servicios_view",          "ServiciosView",
        "app.controllers.servicios_controller",      "ServiciosController",
    ),

    # ── Modulos secundarios (acceso interno, no aparecen en sidebar) ──────
    "Citas": (
        "app.views.screens.citas_view",              "CitasView",
        "app.controllers.citas_controller",          "CitasController",
    ),
    "Empleados": (
        "app.views.screens.empleados_view",          "EmpleadosView",
        "app.controllers.empleados_controller",      "EmpleadosController",
    ),
}


class DashboardView(ctk.CTkFrame):
    """Contenedor principal: sidebar izquierdo + area de contenido derecha."""

    def __init__(self, parent, usuario: dict, on_logout=None):
        super().__init__(parent, fg_color="#0D0D0D")
        self.usuario          = usuario
        self._on_logout       = on_logout   # callback para volver al login al cerrar sesion
        self._pantalla_actual = None        # referencia al modulo activo
        self._construir()

    def _construir(self):
        # ── Header superior ───────────────────────────────────────────────
        # La barra de encabezado muestra nombre del app, fecha y datos del usuario
        self._header = Header(self, self.usuario)
        self._header.pack(fill="x", padx=8, pady=(8, 0))

        # ── Cuerpo: sidebar + area de contenido ───────────────────────────
        cuerpo = ctk.CTkFrame(self, fg_color="transparent")
        cuerpo.pack(expand=True, fill="both", pady=8, padx=8)

        # Sidebar izquierdo con los botones de navegacion por rol
        self._sidebar = Sidebar(
            cuerpo, self.usuario, on_navigate=self._navegar
        )
        self._sidebar.pack(side="left", fill="y", padx=(0, 8))

        # Area central donde se insertan los modulos al navegar
        self._area = ctk.CTkFrame(cuerpo, fg_color="#111111", corner_radius=12)
        self._area.pack(side="left", expand=True, fill="both")

        # ── Pantalla inicial segun el rol ─────────────────────────────────
        self._sidebar.marcar_activo("PanelPrincipal")

    def _navegar(self, modulo: str):
        """Carga el modulo seleccionado en el area de contenido."""
        # Si el usuario hizo clic en logout, cierro la sesion
        if modulo == "logout":
            self._cerrar_sesion()
            return

        # Limpio la pantalla actual antes de intentar cargar otra
        if self._pantalla_actual:
            self._pantalla_actual.destroy()
            self._pantalla_actual = None

        if modulo and not tiene_permiso(self.usuario.get("rol", ""), modulo):
            self._pantalla_actual = ctk.CTkLabel(
                self._area,
                text="No tienes permiso para entrar a este módulo.",
                text_color="red",
            )
            self._pantalla_actual.pack(expand=True)
            return

        # Busco la configuracion del modulo en el diccionario PANTALLAS
        config = PANTALLAS.get(modulo)
        if not config:
            # Si el modulo no existe, muestro un mensaje de error en el area
            self._pantalla_actual = ctk.CTkLabel(
                self._area,
                text=f"Módulo '{modulo}' no encontrado.",
                text_color="red",
            )
            self._pantalla_actual.pack(expand=True)
            return

        vista_modulo, vista_clase, ctrl_modulo, ctrl_clase = config

        try:
            # Importo el modulo de la vista y creo la instancia de la clase
            mod_vista  = importlib.import_module(vista_modulo)
            ClaseVista = getattr(mod_vista, vista_clase)
            self._pantalla_actual = ClaseVista(self._area, usuario=self.usuario)
            self._pantalla_actual.pack(expand=True, fill="both")

            # Importo el modulo del controlador y lo conecto con la vista
            mod_ctrl  = importlib.import_module(ctrl_modulo)
            ClaseCtrl = getattr(mod_ctrl, ctrl_clase)
            ClaseCtrl(view=self._pantalla_actual, usuario=self.usuario)

            if modulo == "PanelPrincipal" and hasattr(self._pantalla_actual, "btn_ver_agenda"):
                self._pantalla_actual.btn_ver_agenda.configure(
                    command=lambda: self._navegar("Agenda")
                )

            if modulo == "Equipo" and hasattr(self._pantalla_actual, "btn_agregar"):
                self._pantalla_actual.btn_agregar.configure(
                    command=lambda: self._navegar("Empleados")
                )

        except Exception as e:
            # Si algo falla al cargar, muestro el error completo para depurar
            import traceback
            error_texto = f"Error al cargar '{modulo}':\n{e}\n\n{traceback.format_exc()}"
            self._pantalla_actual = ctk.CTkLabel(
                self._area,
                text=error_texto,
                text_color="red",
                wraplength=700,
                justify="left",
            )
            self._pantalla_actual.pack(expand=True, padx=20)

    def _cerrar_sesion(self):
        """Destruye el dashboard y vuelve a la pantalla de login."""
        self.destroy()
        if self._on_logout:
            self._on_logout()
