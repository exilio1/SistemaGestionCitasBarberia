import bcrypt
from app.core.database import get_connection


class UsuarioModel:

    def crear(self, nombre, correo, password, rol, telefono=""):
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        conn = get_connection()
        cursor = conn.execute(
            "INSERT INTO usuarios (nombre, correo, contrasena_hash, rol, telefono) VALUES (?, ?, ?, ?, ?)",
            (nombre, correo, hashed, rol, telefono)
        )
        conn.commit()
        conn.close()
        return cursor.lastrowid

    def autenticar(self, correo, password):
        conn = get_connection()
        fila = conn.execute(
            "SELECT * FROM usuarios WHERE correo = ? AND activo = 1", (correo,)
        ).fetchone()
        conn.close()
        if fila and bcrypt.checkpw(password.encode(), fila["contrasena_hash"].encode()):
            return dict(fila)
        return None

    def obtener_por_id(self, usuario_id):
        conn = get_connection()
        fila = conn.execute(
            "SELECT * FROM usuarios WHERE id = ?", (usuario_id,)
        ).fetchone()
        conn.close()
        if fila:
            return dict(fila)
        return None

    def listar(self):
        conn = get_connection()
        filas = conn.execute(
            "SELECT * FROM usuarios WHERE activo = 1 ORDER BY nombre"
        ).fetchall()
        conn.close()
        resultado = []
        for f in filas:
            resultado.append(dict(f))
        return resultado

    def desactivar(self, usuario_id):
        conn = get_connection()
        conn.execute("UPDATE usuarios SET activo = 0 WHERE id = ?", (usuario_id,))
        conn.commit()
        conn.close()
        return True
