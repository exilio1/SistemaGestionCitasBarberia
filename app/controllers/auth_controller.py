from app.models.usuario_model import UsuarioModel
from app.views.login_view import LoginView


class AuthController:
    def __init__(self, view, on_success, on_register=None):
        self._model = UsuarioModel()
        self._view = view
        self._on_success = on_success
        self._view.on_login_callback = self.login
        self._view.on_registro_callback = on_register

    def login(self, email, password):
        if not email or not password:
            self._view.mostrar_error("Completa todos los campos.")
            return

        usuario = self._model.autenticar(email, password)
        if usuario:
            self._on_success(usuario)
        else:
            self._view.mostrar_error("Correo o contraseña incorrectos.")
