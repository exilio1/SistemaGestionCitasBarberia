from app.models.empleado_model import EmpleadoModel


def test_crear_empleado_y_obtener_por_id(temp_db):
    modelo = EmpleadoModel()

    empleado_id = modelo.crear("Carlos", "3002223344", "Corte clasico", 60.0)
    empleado = modelo.obtener_por_id(empleado_id)

    assert empleado is not None
    assert empleado["nombre"] == "Carlos"
    assert empleado["activo"] == 1
