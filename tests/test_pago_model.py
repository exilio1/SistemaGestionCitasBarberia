import pytest

from app.core.database import get_connection
from app.models.pago_model import PagoModel


def _crear_cita_base():
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
    return cita_id, empleado_id


def test_registrar_pago_calcula_ganancias(temp_db):
    cita_id, _ = _crear_cita_base()
    modelo = PagoModel()

    resultado = modelo.registrar(cita_id, 50000, "efectivo", "2026-05-18", pct_empleado=60)
    pago = modelo.obtener_por_cita(cita_id)

    assert resultado["empleado"] == 30000
    assert resultado["negocio"] == 20000
    assert resultado["total"] == 50000
    assert pago["monto"] == 50000


def test_no_permite_dos_pagos_para_la_misma_cita(temp_db):
    cita_id, _ = _crear_cita_base()
    modelo = PagoModel()
    modelo.registrar(cita_id, 50000, "efectivo", "2026-05-18")

    with pytest.raises(ValueError):
        modelo.registrar(cita_id, 50000, "efectivo", "2026-05-18")


def test_ingresos_por_periodo_filtra_totales(temp_db):
    cita_id, _ = _crear_cita_base()
    modelo = PagoModel()
    modelo.registrar(cita_id, 50000, "efectivo", "2026-05-18", pct_empleado=60)

    ingresos = modelo.ingresos_por_periodo("2026-05-01", "2026-05-31")

    assert ingresos == {"total": 50000, "empleados": 30000, "negocio": 20000}
