"""
View principal — ventana raíz de la aplicación.
Muestra LoginView primero; tras autenticarse carga el layout con sidebar.
RNF01: interfaz amigable | RNF05: menú según rol
"""

import customtkinter as ctk
from app.views.login_view import LoginView


class MainView(ctk.CTk):
    def __init__(self):
        super().__init__()
        # Configuro la ventana raiz con titulo, tamaño y minimo
        self.title("Gestión Barbería")
        self.geometry("1200x780")
        self.minsize(1000, 750)
        # Guarda referencia al frame actual para poder destruirlo al cambiar de pantalla
        self._current_frame: ctk.CTkFrame | None = None
        # La primera pantalla siempre es el login
        self.cargar_login()

    def _show(self, view_class, **kwargs):
        """Destruye el frame actual y muestra uno nuevo en su lugar."""
        # Si habia una pantalla antes, la elimino para liberar memoria
        if self._current_frame:
            self._current_frame.destroy()
        # Creo el nuevo frame y lo expando para que ocupe toda la ventana
        self._current_frame = view_class(self, **kwargs)
        self._current_frame.pack(expand=True, fill="both")

    def cargar_login(self):
        """Muestra la pantalla de login y conecta su controlador."""
        from app.controllers.auth_controller import AuthController
        self._show(LoginView)
        # El controlador de autenticacion recibe callbacks para navegar despues del login
        AuthController(
            view=self._current_frame,
            on_success=self.cargar_dashboard,
            on_register=self.cargar_registro,
        )

    def cargar_registro(self):
        """Muestra la pantalla de registro con un boton para volver al login."""
        from app.views.registro_view import RegistroView
        from app.controllers.registro_controller import RegistroController
        # Paso on_back para que el boton "volver" del registro funcione
        self._show(RegistroView, on_back=self.cargar_login)
        RegistroController(view=self._current_frame)

    def cargar_dashboard(self, usuario: dict):
        """Muestra el dashboard principal despues de que el usuario inicia sesion."""
        from app.views.dashboard_view import DashboardView
        # Paso el dict del usuario para que el dashboard sepa el rol y el nombre
        self._show(DashboardView, usuario=usuario, on_logout=self.cargar_login)
