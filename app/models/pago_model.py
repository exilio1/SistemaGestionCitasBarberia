from app.core.database import get_connection
from app.config import PORCENTAJE_EMPLEADO


class PagoModel:

    def registrar(self, cita_id, monto, metodo, fecha, pct_empleado=None):
        if pct_empleado is None:
            pct_empleado = PORCENTAJE_EMPLEADO

        pct_negocio = 100 - pct_empleado
        ganancia_empleado = round(monto * pct_empleado / 100, 2)
        ganancia_negocio = round(monto * pct_negocio / 100, 2)

        conn = get_connection()
        pago_existente = conn.execute(
            "SELECT id FROM pagos WHERE cita_id = ?", (cita_id,)
        ).fetchone()

        if pago_existente:
            conn.close()
            raise ValueError("La cita ya tiene un pago registrado.")

        cursor = conn.execute(
            "INSERT INTO pagos (cita_id, monto, metodo, fecha, ganancia_empleado, ganancia_negocio) VALUES (?, ?, ?, ?, ?, ?)",
            (cita_id, monto, metodo, fecha, ganancia_empleado, ganancia_negocio)
        )
        pago_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return {
            "pago_id": pago_id,
            "empleado": ganancia_empleado,
            "negocio": ganancia_negocio,
            "total": monto
        }

    def obtener_por_cita(self, cita_id):
        conn = get_connection()
        fila = conn.execute(
            "SELECT * FROM pagos WHERE cita_id = ?", (cita_id,)
        ).fetchone()
        conn.close()
        if fila:
            return dict(fila)
        return None

    def listar_por_periodo(self, fecha_inicio, fecha_fin):
        conn = get_connection()
        filas = conn.execute(
            "SELECT * FROM pagos WHERE fecha BETWEEN ? AND ? ORDER BY fecha",
            (fecha_inicio, fecha_fin)
        ).fetchall()
        conn.close()
        resultado = []
        for f in filas:
            resultado.append(dict(f))
        return resultado

    def ingresos_por_periodo(self, fecha_inicio, fecha_fin, empleado_id=None):
        consulta = "SELECT SUM(p.monto) AS total, SUM(p.ganancia_empleado) AS empleados, SUM(p.ganancia_negocio) AS negocio FROM pagos p JOIN citas c ON c.id = p.cita_id WHERE p.fecha BETWEEN ? AND ?"
        parametros = [fecha_inicio, fecha_fin]
        if empleado_id:
            consulta += " AND c.empleado_id = ?"
            parametros.append(empleado_id)

        conn = get_connection()
        fila = conn.execute(consulta, parametros).fetchone()
        conn.close()

        # Si no hay datos, SUM retorna None, entonces ponemos 0
        total = fila["total"] if fila["total"] else 0
        empleados = fila["empleados"] if fila["empleados"] else 0
        negocio = fila["negocio"] if fila["negocio"] else 0
        return {"total": total, "empleados": empleados, "negocio": negocio}

    def ganancias_por_empleado(self, fecha_inicio, fecha_fin):
        conn = get_connection()
        empleados = conn.execute(
            "SELECT * FROM empleados WHERE activo = 1"
        ).fetchall()
        conn.close()

        resultado = []
        for emp in empleados:
            conn = get_connection()
            fila = conn.execute(
                "SELECT COUNT(p.id) AS total_citas, SUM(p.monto) AS total_facturado, SUM(p.ganancia_empleado) AS total_empleado, SUM(p.ganancia_negocio) AS total_negocio FROM pagos p JOIN citas c ON c.id = p.cita_id WHERE c.empleado_id = ? AND p.fecha BETWEEN ? AND ?",
                (emp["id"], fecha_inicio, fecha_fin)
            ).fetchone()
            conn.close()

            total_citas = fila["total_citas"] if fila["total_citas"] else 0
            total_facturado = fila["total_facturado"] if fila["total_facturado"] else 0
            total_empleado = fila["total_empleado"] if fila["total_empleado"] else 0
            total_negocio = fila["total_negocio"] if fila["total_negocio"] else 0

            resultado.append({
                "empleado_id": emp["id"],
                "nombre_empleado": emp["nombre"],
                "especialidad": emp["especialidad"],
                "total_citas": total_citas,
                "total_facturado": total_facturado,
                "total_empleado": total_empleado,
                "total_negocio": total_negocio
            })

        return resultado
