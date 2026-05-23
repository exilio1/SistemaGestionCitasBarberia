import bcrypt
import pyotp
from app.core.database import get_connection


def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())


def login(email, password):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM usuarios WHERE correo = ? AND activo = 1", (email,)
    ).fetchone()
    conn.close()

    if row and verify_password(password, row["contrasena_hash"]):
        return dict(row)
    return None


# Permisos por rol
PERMISOS = {
    "administrador": {
        "PanelPrincipal", "Agenda", "Facturacion",
        "Reportes", "Equipo", "Servicios", "Gastos", "Ayuda", "Empleados",
    },
    "recepcionista": {
        "PanelPrincipal", "Agenda", "Facturacion", "Ayuda",
    },
}


def tiene_permiso(rol, modulo):
    return modulo in PERMISOS.get(rol, set())


# ── Autenticación de Doble Factor — TOTP (Google Authenticator) ───────────────

def generar_totp_secret() -> str:
    """Genera una clave secreta aleatoria en base32 para el usuario."""
    return pyotp.random_base32()


def obtener_totp_uri(secret: str, correo: str) -> str:
    """
    Devuelve el URI otpauth:// que se convierte en código QR.
    Google Authenticator escanea ese QR y queda vinculado al usuario.
    """
    return pyotp.TOTP(secret).provisioning_uri(
        name=correo, issuer_name="Barbers Studio"
    )


def verificar_totp(secret: str, codigo: str) -> bool:
    """
    Verifica el código de 6 dígitos ingresado por el usuario.
    valid_window=1 acepta el código del período anterior y siguiente
    para compensar pequeñas diferencias de reloj entre dispositivos.
    """
    if not secret or not codigo:
        return False
    return pyotp.TOTP(secret).verify(codigo.strip(), valid_window=1)


def guardar_totp_secret(usuario_id: int, secret: str) -> None:
    """Guarda la clave secreta TOTP del usuario en la base de datos."""
    conn = get_connection()
    conn.execute(
        "UPDATE usuarios SET totp_secret = ? WHERE id = ?",
        (secret, usuario_id),
    )
    conn.commit()
    conn.close()
