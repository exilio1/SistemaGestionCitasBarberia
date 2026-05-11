import re
from datetime import date
from app.core.database import get_connection


def _solo_digitos(texto):
    return re.sub(r"\D", "", texto or "")


def formatear_cedula(cedula):
    digitos = _solo_digitos(cedula)
    if not digitos:
        return cedula
    resultado = ""
    for i, c in enumerate(reversed(digitos)):
        if i > 0 and i % 3 == 0:
            resultado = "." + resultado
        resultado = c + resultado
    return resultado


class ClienteModel:

    def obtener_o_crear(self, nombre, cedula="", telefono=""):
        ced = _solo_digitos(cedula)
        tel = _solo_digitos(telefono)
        hoy = date.today().isoformat()

        conn = get_connection()

        # Buscar por cedula primero
        if ced:
            fila = conn.execute(
                "SELECT id FROM clientes WHERE cedula = ?", (ced,)
            ).fetchone()
            if fila:
                conn.close()
                return fila["id"]

        # Buscar por telefono como segunda opcion
        if tel:
            fila = conn.execute(
                "SELECT id FROM clientes WHERE telefono = ?", (tel,)
            ).fetchone()
            if fila:
                conn.close()
                return fila["id"]

        # Crear el cliente si no existe
        cursor = conn.execute(
            "INSERT INTO clientes (nombre, cedula, telefono, fecha_creacion) VALUES (?, ?, ?, ?)",
            (nombre, ced or None, tel or None, hoy)
        )
        conn.commit()
        conn.close()
        return cursor.lastrowid

    def actualizar_nombre(self, cedula, nuevo_nombre):
        ced = _solo_digitos(cedula)
        conn = get_connection()
        conn.execute("UPDATE clientes SET nombre = ? WHERE cedula = ?", (nuevo_nombre, ced))
        conn.commit()
        conn.close()

    def obtener_por_cedula(self, cedula):
        ced = _solo_digitos(cedula)
        conn = get_connection()
        fila = conn.execute("SELECT * FROM clientes WHERE cedula = ?", (ced,)).fetchone()
        conn.close()
        if fila:
            return dict(fila)
        return None

    def obtener_por_telefono(self, telefono):
        tel = _solo_digitos(telefono)
        conn = get_connection()
        fila = conn.execute("SELECT * FROM clientes WHERE telefono = ?", (tel,)).fetchone()
        conn.close()
        if fila:
            return dict(fila)
        return None

    def obtener_por_correo(self, correo):
        conn = get_connection()
        fila = conn.execute("SELECT * FROM clientes WHERE correo = ?", (correo,)).fetchone()
        conn.close()
        if fila:
            return dict(fila)
        return None

    def crear_completo(self, nombre, cedula="", telefono="", correo=""):
        ced = _solo_digitos(cedula)
        tel = _solo_digitos(telefono)
        hoy = date.today().isoformat()
        try:
            conn = get_connection()
            cursor = conn.execute(
                "INSERT INTO clientes (nombre, cedula, telefono, correo, fecha_creacion) VALUES (?, ?, ?, ?, ?)",
                (nombre, ced or None, tel or None, correo or None, hoy)
            )
            conn.commit()
            conn.close()
            return cursor.lastrowid
        except Exception:
            return None

    def listar(self):
        conn = get_connection()
        filas = conn.execute("SELECT * FROM clientes ORDER BY nombre").fetchall()
        conn.close()
        resultado = []
        for f in filas:
            resultado.append(dict(f))
        return resultado
