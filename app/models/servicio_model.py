from app.core.database import get_connection


class ServicioModel:

    def listar(self, solo_activos=True):
        consulta = "SELECT * FROM servicios"
        if solo_activos:
            consulta += " WHERE activo = 1"
        consulta += " ORDER BY nombre"
        conn = get_connection()
        filas = conn.execute(consulta).fetchall()
        conn.close()
        resultado = []
        for f in filas:
            resultado.append(dict(f))
        return resultado

    def obtener_por_id(self, servicio_id):
        conn = get_connection()
        fila = conn.execute(
            "SELECT * FROM servicios WHERE id = ?", (servicio_id,)
        ).fetchone()
        conn.close()
        if fila:
            return dict(fila)
        return None

    def obtener_por_nombre(self, nombre):
        conn = get_connection()
        fila = conn.execute(
            "SELECT * FROM servicios WHERE nombre = ?", (nombre,)
        ).fetchone()
        conn.close()
        if fila:
            return dict(fila)
        return None

    def crear(self, nombre, precio, descripcion="", duracion_minutos=30):
        conn = get_connection()
        cursor = conn.execute(
            "INSERT INTO servicios (nombre, descripcion, precio, duracion_minutos, activo) VALUES (?, ?, ?, ?, 1)",
            (nombre, descripcion, precio, duracion_minutos)
        )
        conn.commit()
        conn.close()
        return cursor.lastrowid

    def actualizar(self, servicio_id, nombre, precio, descripcion="", duracion_minutos=30):
        conn = get_connection()
        conn.execute(
            "UPDATE servicios SET nombre = ?, descripcion = ?, precio = ?, duracion_minutos = ? WHERE id = ?",
            (nombre, descripcion, precio, duracion_minutos, servicio_id)
        )
        conn.commit()
        conn.close()

    def desactivar(self, servicio_id):
        conn = get_connection()
        conn.execute("UPDATE servicios SET activo = 0 WHERE id = ?", (servicio_id,))
        conn.commit()
        conn.close()

    def activar(self, servicio_id):
        conn = get_connection()
        conn.execute("UPDATE servicios SET activo = 1 WHERE id = ?", (servicio_id,))
        conn.commit()
        conn.close()
