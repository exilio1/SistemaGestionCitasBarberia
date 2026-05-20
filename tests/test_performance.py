import time

from app.core.database import get_connection
from app.models.cita_model import CitaModel
from app.models.factura_model import FacturaModel
from app.models.gasto_model import GastoModel
from app.models.pago_model import PagoModel
from app.models.usuario_model import UsuarioModel


MAX_SECONDS = 3.0


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
    conn.commit()
    conn.close()
    return cliente_id, empleado_id, servicio_id


def test_login_responde_en_menos_de_3_segundos(temp_db):
    modelo = UsuarioModel()
    modelo.crear("Admin", "admin@test.com", "Seguro123", "administrador")

    inicio = time.perf_counter()
    usuario = modelo.autenticar("admin@test.com", "Seguro123")
    duracion = time.perf_counter() - inicio

    assert usuario is not None
    assert duracion < MAX_SECONDS


def test_crear_cita_responde_en_menos_de_3_segundos(temp_db):
    cliente_id, empleado_id, servicio_id = _crear_cita_base()
    modelo = CitaModel()

    inicio = time.perf_counter()
    codigo = modelo.crear(cliente_id, empleado_id, servicio_id, "2026-05-20", "10:00")
    duracion = time.perf_counter() - inicio

    assert codigo
    assert duracion < MAX_SECONDS


def test_registrar_pago_y_factura_responde_en_menos_de_3_segundos(temp_db):
    cliente_id, empleado_id, servicio_id = _crear_cita_base()
    codigo = CitaModel().crear(
        cliente_id, empleado_id, servicio_id, "2026-05-20", "10:00", estado="completada"
    )
    cita = CitaModel().obtener_por_codigo(codigo)

    inicio = time.perf_counter()
    pago = PagoModel().registrar(cita["id"], 50000, "efectivo", "2026-05-20")
    factura = FacturaModel().generar(pago["pago_id"], "Pago de corte")
    duracion = time.perf_counter() - inicio

    assert pago["total"] == 50000
    assert factura is not None
    assert duracion < MAX_SECONDS


def test_consultas_financieras_responden_en_menos_de_3_segundos(temp_db):
    cliente_id, empleado_id, servicio_id = _crear_cita_base()
    codigo = CitaModel().crear(
        cliente_id, empleado_id, servicio_id, "2026-05-20", "10:00", estado="completada"
    )
    cita = CitaModel().obtener_por_codigo(codigo)
    PagoModel().registrar(cita["id"], 50000, "efectivo", "2026-05-20")
    GastoModel().crear("Compra de gel", "Insumos", 20000, "2026-05-20")

    inicio = time.perf_counter()
    ingresos = PagoModel().ingresos_por_periodo("2026-05-01", "2026-05-31")
    gastos = GastoModel().total_por_periodo("2026-05-01", "2026-05-31")
    duracion = time.perf_counter() - inicio

    assert ingresos["total"] == 50000
    assert gastos == 20000
    assert duracion < MAX_SECONDS
