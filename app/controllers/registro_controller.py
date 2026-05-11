
from app.models.usuario_model import UsuarioModel
from app.views.registro_view import RegistroView


class RegistroController:
    def __init__(self, view):
        self._modelo_usuario = UsuarioModel()
        self._view = view
        # Conecto el callback del formulario con el método de registrar
        self._view.on_registro_callback = self._registrar

    def _registrar(self, nombre, correo, rol, password, confirmar, telefono=""):
        """Valida los datos del formulario y crea el usuario en la base de datos."""

        # Verifico que los campos obligatorios no estén vacíos
        if not nombre or not correo or not password:
            self._view.mostrar_error("Completa todos los campos obligatorios.")
            return

        # Solo permito los roles válidos del sistema
        if rol not in ("administrador", "recepcionista"):
            self._view.mostrar_error("Rol no válido.")
            return

        # Las dos contraseñas deben coincidir
        if password != confirmar:
            self._view.mostrar_error("Las contraseñas no coinciden.")
            return

        # La contraseña debe tener mínimo 6 caracteres por seguridad
        if len(password) < 6:
            self._view.mostrar_error("La contraseña debe tener mínimo 6 caracteres.")
            return

        try:
            # Todo válido — creo el usuario en la BD
            self._modelo_usuario.crear(nombre, correo, password, rol, telefono)
            self._view.mostrar_exito()
        except Exception:
            # Si la BD lanza error, es porque el correo ya está registrado
            self._view.mostrar_error("El correo ya está registrado en el sistema.")
