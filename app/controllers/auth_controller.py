from app.models.usuario_model import UsuarioModel
from app.core import auth as auth_core


class AuthController:
    def __init__(self, view, on_success, on_register=None):
        self._model      = UsuarioModel()
        self._view       = view
        self._on_success = on_success
        self._view.on_login_callback    = self.login
        self._view.on_registro_callback = on_register

    def login(self, email, password):
        if not email or not password:
            self._view.mostrar_error("Completa todos los campos.")
            return

        usuario = self._model.autenticar(email, password)
        if not usuario:
            self._view.mostrar_error("Correo o contraseña incorrectos.")
            return

        # ── Credenciales OK → verificar 2FA ──────────────────────────────
        totp_secret = usuario.get("totp_secret")

        if not totp_secret:
            # Primera vez: no tiene 2FA configurado → mostrar QR para configurar
            self._configurar_2fa(usuario)
        else:
            # Ya tiene 2FA → pedir el código de Google Authenticator
            self._verificar_2fa(usuario, totp_secret)

    # ── Primera configuración de 2FA (solo la primera vez) ───────────────────

    def _configurar_2fa(self, usuario):
        from app.views.components.popup_2fa import Popup2FA

        secret = auth_core.generar_totp_secret()
        uri    = auth_core.obtener_totp_uri(secret, usuario["correo"])

        def on_verificar(codigo: str) -> bool:
            # Si el código es correcto, guardamos el secreto y hacemos login
            if auth_core.verificar_totp(secret, codigo):
                auth_core.guardar_totp_secret(usuario["id"], secret)
                usuario["totp_secret"] = secret
                self._on_success(usuario)
                return True
            return False

        def on_cancelar():
            self._view.mostrar_error(
                "Debes configurar Google Authenticator para continuar."
            )

        Popup2FA(
            self._view,
            modo="setup",
            uri=uri,
            on_verificar=on_verificar,
            on_cancelar=on_cancelar,
        )

    # ── Verificación en cada login ────────────────────────────────────────────

    def _verificar_2fa(self, usuario, secret: str):
        from app.views.components.popup_2fa import Popup2FA

        def on_verificar(codigo: str) -> bool:
            if auth_core.verificar_totp(secret, codigo):
                self._on_success(usuario)
                return True
            return False

        def on_cancelar():
            self._view.mostrar_error("Inicio de sesión cancelado.")

        Popup2FA(
            self._view,
            modo="verificar",
            on_verificar=on_verificar,
            on_cancelar=on_cancelar,
        )
