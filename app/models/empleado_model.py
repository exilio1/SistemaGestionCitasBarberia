from app.core.database import get_connection


class EmpleadoModel:

    def crear(self, nombre, telefono, especialidad, porcentaje_ganancia=60.0):
        conn = get_connection()
        cursor = conn.execute(
            "INSERT INTO empleados (nombre, telefono, especialidad, porcentaje_ganancia) VALUES (?, ?, ?, ?)",
            (nombre, telefono, especialidad, porcentaje_ganancia)
        )
        conn.commit()
        conn.close()
        return cursor.lastrowid

    def listar(self):
        conn = get_connection()
        filas = conn.execute(
            "SELECT * FROM empleados WHERE activo = 1 ORDER BY nombre"
        ).fetchall()
        conn.close()
        resultado = []
        for f in filas:
            resultado.append(dict(f))
        return resultado

    def listar_todos(self):
        conn = get_connection()
        filas = conn.execute(
            "SELECT * FROM empleados ORDER BY activo DESC, nombre"
        ).fetchall()
        conn.close()
        resultado = []
        for f in filas:
            resultado.append(dict(f))
        return resultado

    def obtener_por_id(self, empleado_id):
        conn = get_connection()
        fila = conn.execute(
            "SELECT * FROM empleados WHERE id = ?", (empleado_id,)
        ).fetchone()
        conn.close()
        if fila:
            return dict(fila)
        return None

    def actualizar(self, empleado_id, nombre, telefono, especialidad, porcentaje_ganancia):
        conn = get_connection()
        conn.execute(
            "UPDATE empleados SET nombre = ?, telefono = ?, especialidad = ?, porcentaje_ganancia = ? WHERE id = ?",
            (nombre, telefono, especialidad, porcentaje_ganancia, empleado_id)
        )
        conn.commit()
        conn.close()
        return True

    def desactivar(self, empleado_id):
        conn = get_connection()
        conn.execute("UPDATE empleados SET activo = 0 WHERE id = ?", (empleado_id,))
        conn.commit()
        conn.close()
        return True

    def activar(self, empleado_id):
        conn = get_connection()
        conn.execute("UPDATE empleados SET activo = 1 WHERE id = ?", (empleado_id,))
        conn.commit()
        conn.close()
        return True
