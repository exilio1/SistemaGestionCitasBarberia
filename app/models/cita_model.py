import uuid
from datetime import datetime, timedelta
from app.core.database import get_connection
from app.config import HORARIO_INICIO, HORARIO_FIN


class CitaModel:

    def crear(self, cliente_id, empleado_id, servicio_id, fecha, hora, observaciones=None):
        # Generar codigo unico de 8 caracteres
        codigo = str(uuid.uuid4())[:8].upper()
        conn = get_connection()
        conn.execute(
            "INSERT INTO citas (cliente_id, empleado_id, servicio_id, fecha, hora, estado, observaciones, codigo) VALUES (?, ?, ?, ?, ?, 'pendiente', ?, ?)",
            (cliente_id, empleado_id, servicio_id, fecha, hora, observaciones, codigo)
        )
        conn.commit()
        conn.close()
        return codigo

    def horarios_disponibles(self, fecha, empleado_id=None):
        # Generar todas las horas del horario de trabajo
        inicio = datetime.strptime(HORARIO_INICIO, "%H:%M")
        fin = datetime.strptime(HORARIO_FIN, "%H:%M")
        todas_las_horas = []
        hora_actual = inicio
        while hora_actual < fin:
            todas_las_horas.append(hora_actual.strftime("%H:%M"))
            hora_actual += timedelta(minutes=30)

        # Consultar horas ocupadas
        consulta = "SELECT hora FROM citas WHERE fecha = ? AND estado != 'cancelada'"
        parametros = [fecha]
        if empleado_id:
            consulta += " AND empleado_id = ?"
            parametros.append(empleado_id)

        conn = get_connection()
        filas = conn.execute(consulta, parametros).fetchall()
        conn.close()

        horas_ocupadas = []
        for fila in filas:
            horas_ocupadas.append(fila["hora"])

        # Retornar solo las horas libres
        horas_libres = []
        for h in todas_las_horas:
            if h not in horas_ocupadas:
                horas_libres.append(h)
        return horas_libres

    def obtener_por_codigo(self, codigo):
        conn = get_connection()
        fila = conn.execute(
            "SELECT c.*, s.nombre AS servicio, s.precio FROM citas c JOIN servicios s ON s.id = c.servicio_id WHERE c.codigo = ?",
            (codigo,)
        ).fetchone()
        conn.close()
        if fila:
            return dict(fila)
        return None

    def listar_por_rango(self, fecha_inicio, fecha_fin, empleado_id=None):
        consulta = "SELECT c.*, s.nombre AS servicio, s.precio FROM citas c JOIN servicios s ON s.id = c.servicio_id WHERE c.fecha BETWEEN ? AND ?"
        parametros = [fecha_inicio, fecha_fin]
        if empleado_id:
            consulta += " AND c.empleado_id = ?"
            parametros.append(empleado_id)
        consulta += " ORDER BY c.fecha, c.hora"

        conn = get_connection()
        filas = conn.execute(consulta, parametros).fetchall()
        conn.close()
        resultado = []
        for f in filas:
            resultado.append(dict(f))
        return resultado

    def confirmar(self, codigo):
        conn = get_connection()
        resultado = conn.execute(
            "UPDATE citas SET estado = 'confirmada' WHERE codigo = ? AND estado = 'pendiente'",
            (codigo,)
        )
        conn.commit()
        conn.close()
        return resultado.rowcount > 0

    def reprogramar(self, codigo, nueva_fecha, nueva_hora):
        conn = get_connection()
        resultado = conn.execute(
            "UPDATE citas SET fecha = ?, hora = ? WHERE codigo = ? AND estado IN ('pendiente', 'confirmada')",
            (nueva_fecha, nueva_hora, codigo)
        )
        conn.commit()
        conn.close()
        return resultado.rowcount > 0

    def cancelar(self, codigo):
        conn = get_connection()
        resultado = conn.execute(
            "UPDATE citas SET estado = 'cancelada' WHERE codigo = ? AND estado != 'completada'",
            (codigo,)
        )
        conn.commit()
        conn.close()
        return resultado.rowcount > 0

    def actualizar_estado(self, codigo, estado):
        conn = get_connection()
        conn.execute("UPDATE citas SET estado = ? WHERE codigo = ?", (estado, codigo))
        conn.commit()
        conn.close()
        return True

    def obtener_por_id(self, cita_id):
        conn = get_connection()
        fila = conn.execute(
            "SELECT c.*, s.nombre AS servicio, s.precio FROM citas c JOIN servicios s ON s.id = c.servicio_id WHERE c.id = ?",
            (cita_id,)
        ).fetchone()
        conn.close()
        if fila:
            return dict(fila)
        return None

    def listar_todas(self):
        conn = get_connection()
        filas = conn.execute(
            "SELECT c.*, s.nombre AS servicio, s.precio FROM citas c JOIN servicios s ON s.id = c.servicio_id ORDER BY c.fecha DESC, c.hora"
        ).fetchall()
        conn.close()
        resultado = []
        for f in filas:
            resultado.append(dict(f))
        return resultado
