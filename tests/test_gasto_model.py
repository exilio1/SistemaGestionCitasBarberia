from app.models.gasto_model import GastoModel


def test_crear_gasto_y_sumar_total_por_periodo(temp_db):
    modelo = GastoModel()

    gasto_id = modelo.crear("Compra de gel", "Insumos", 20000, "2026-05-18", usuario_id=None)
    total = modelo.total_por_periodo("2026-05-01", "2026-05-31")
    gastos = modelo.listar_por_periodo("2026-05-01", "2026-05-31")

    assert gasto_id is not None
    assert total == 20000
    assert gastos[0]["descripcion"] == "Compra de gel"


def test_actualizar_y_eliminar_gasto(temp_db):
    modelo = GastoModel()
    gasto_id = modelo.crear("Compra de gel", "Insumos", 20000, "2026-05-18")

    modelo.actualizar(gasto_id, "Compra de cuchillas", "Herramientas", 30000)
    actualizado = modelo.listar_por_periodo("2026-05-01", "2026-05-31")[0]
    modelo.eliminar(gasto_id)

    assert actualizado["descripcion"] == "Compra de cuchillas"
    assert actualizado["monto"] == 30000
    assert modelo.total_por_periodo("2026-05-01", "2026-05-31") == 0.0
