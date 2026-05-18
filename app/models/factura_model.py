from datetime import date
from app.core.database import get_connection


class FacturaModel:

    def generar(self, pago_id, detalle=""):
        hoy = date.today().strftime("%Y%m%d")
        numero = f"FAC-{hoy}-{pago_id:04d}"

        try:
            conn = get_connection()
            pago = conn.execute(
                "SELECT id FROM pagos WHERE id = ?", (pago_id,)
            ).fetchone()

            if not pago:
                conn.close()
                return None

            conn.execute(
                "INSERT INTO facturas (pago_id, numero_factura, fecha_emision, detalle) VALUES (?, ?, date('now'), ?)",
                (pago_id, numero, detalle)
            )
            conn.commit()
            conn.close()
            return numero
        except Exception:
            return None

    def obtener_por_pago(self, pago_id):
        conn = get_connection()
        fila = conn.execute(
            "SELECT * FROM facturas WHERE pago_id = ?", (pago_id,)
        ).fetchone()
        conn.close()
        if fila:
            return dict(fila)
        return None

    def obtener_por_numero(self, numero_factura):
        conn = get_connection()
        fila = conn.execute(
            "SELECT * FROM facturas WHERE numero_factura = ?", (numero_factura,)
        ).fetchone()
        conn.close()
        if fila:
            return dict(fila)
        return None

    def listar(self):
        conn = get_connection()
        filas = conn.execute(
            "SELECT f.id, f.numero_factura, f.fecha_emision, f.detalle, p.monto, p.metodo, s.nombre AS servicio, c.fecha AS fecha_cita, cl.nombre AS nombre_cliente, cl.telefono AS telefono_cliente FROM facturas f JOIN pagos p ON p.id = f.pago_id JOIN citas c ON c.id = p.cita_id JOIN servicios s ON s.id = c.servicio_id JOIN clientes cl ON cl.id = c.cliente_id ORDER BY f.fecha_emision DESC"
        ).fetchall()
        conn.close()
        resultado = []
        for f in filas:
            resultado.append(dict(f))
        return resultado
