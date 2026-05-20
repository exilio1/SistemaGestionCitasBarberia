import bcrypt
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
