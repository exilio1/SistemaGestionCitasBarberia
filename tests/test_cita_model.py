from app.core.database import get_connection
from app.models.cita_model import CitaModel


def _crear_datos_base():
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
        ("Corte", "Corte de cabello", 25000, 30),
    ).lastrowid
    conn.commit()
    conn.close()
    return cliente_id, empleado_id, servicio_id


def test_crear_cita_pendiente(temp_db):
    cliente_id, empleado_id, servicio_id = _crear_datos_base()
    modelo = CitaModel()

    codigo = modelo.crear(cliente_id, empleado_id, servicio_id, "2026-05-15", "10:00")
    cita = modelo.obtener_por_codigo(codigo)

    assert codigo
    assert cita["estado"] == "pendiente"
    assert cita["hora"] == "10:00"


def test_confirmar_cita_pendiente(temp_db):
    cliente_id, empleado_id, servicio_id = _crear_datos_base()
    modelo = CitaModel()
    codigo = modelo.crear(cliente_id, empleado_id, servicio_id, "2026-05-15", "10:00")

    confirmada = modelo.confirmar(codigo)
    cita = modelo.obtener_por_codigo(codigo)

    assert confirmada is True
    assert cita["estado"] == "confirmada"


def test_cancelar_cita_no_completada(temp_db):
    cliente_id, empleado_id, servicio_id = _crear_datos_base()
    modelo = CitaModel()
    codigo = modelo.crear(cliente_id, empleado_id, servicio_id, "2026-05-15", "10:00")

    cancelada = modelo.cancelar(codigo)
    cita = modelo.obtener_por_codigo(codigo)

    assert cancelada is True
    assert cita["estado"] == "cancelada"
