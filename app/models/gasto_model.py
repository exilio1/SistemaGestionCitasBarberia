from app.core.database import get_connection


class GastoModel:

    def crear(self, descripcion, categoria, monto, fecha_gasto, usuario_id=None):
        conn = get_connection()
        cursor = conn.execute(
            "INSERT INTO gastos (usuario_id, descripcion, categoria, monto, fecha_gasto) VALUES (?, ?, ?, ?, ?)",
            (usuario_id, descripcion, categoria, monto, fecha_gasto)
        )
        conn.commit()
        conn.close()
        return cursor.lastrowid

    def listar_por_periodo(self, fecha_inicio, fecha_fin):
        conn = get_connection()
        filas = conn.execute(
            "SELECT * FROM gastos WHERE fecha_gasto BETWEEN ? AND ? ORDER BY fecha_gasto",
            (fecha_inicio, fecha_fin)
        ).fetchall()
        conn.close()
        resultado = []
        for f in filas:
            resultado.append(dict(f))
        return resultado

    def total_por_periodo(self, fecha_inicio, fecha_fin):
        conn = get_connection()
        fila = conn.execute(
            "SELECT SUM(monto) AS total FROM gastos WHERE fecha_gasto BETWEEN ? AND ?",
            (fecha_inicio, fecha_fin)
        ).fetchone()
        conn.close()
        if fila["total"]:
            return fila["total"]
        return 0.0

    def actualizar(self, gasto_id, descripcion, categoria, monto):
        conn = get_connection()
        conn.execute(
            "UPDATE gastos SET descripcion = ?, categoria = ?, monto = ? WHERE id = ?",
            (descripcion, categoria, monto, gasto_id)
        )
        conn.commit()
        conn.close()
        return True

    def eliminar(self, gasto_id):
        conn = get_connection()
        conn.execute("DELETE FROM gastos WHERE id = ?", (gasto_id,))
        conn.commit()
        conn.close()
        return True
