from app.core.database import get_connection
from app.models.factura_model import FacturaModel
from app.models.pago_model import PagoModel


def _crear_pago_base():
    conn = get_connection()
    cliente_id = conn.execute(
        "INSERT INTO clientes (nombre, cedula, telefono) VALUES (?, ?, ?)",
        ("Ana Perez", "1234567890", "3001112233"),
    ).lastrowid
    empleado_id = conn.execute(
        "INSERT INTO empleados (nombre, telefono, especialidad, porcentaje_ganancia) VALUES (?, ?, ?, ?)",
        ("Carlos", "3002223344", "Corte clasico", 60.0),
    ).lastrowid
    servicio_id = conn.execute(
        "INSERT INTO servicios (nombre, descripcion, precio, duracion_minutos) VALUES (?, ?, ?, ?)",
        ("Corte", "Corte de cabello", 50000, 30),
    ).lastrowid
    cita_id = conn.execute(
        "INSERT INTO citas (cliente_id, empleado_id, servicio_id, fecha, hora, codigo) VALUES (?, ?, ?, ?, ?, ?)",
        (cliente_id, empleado_id, servicio_id, "2026-05-18", "10:00", "ABC12345"),
    ).lastrowid
    conn.commit()
    conn.close()
    return PagoModel().registrar(cita_id, 50000, "efectivo", "2026-05-18")["pago_id"]


def test_generar_factura_para_pago_existente(temp_db):
    pago_id = _crear_pago_base()
    modelo = FacturaModel()

    numero = modelo.generar(pago_id, "Pago de corte")
    factura = modelo.obtener_por_pago(pago_id)

    assert numero is not None
    assert numero.startswith("FAC-")
    assert factura["numero_factura"] == numero


def test_generar_factura_retorna_none_si_pago_no_existe(temp_db):
    assert FacturaModel().generar(9999) is None
