from app.models.servicio_model import ServicioModel


def test_crear_servicio_y_obtener_por_nombre(temp_db):
    modelo = ServicioModel()

    servicio_id = modelo.crear("Corte clasico", 25000, "Corte de cabello", 30)
    servicio = modelo.obtener_por_nombre("Corte clasico")

    assert servicio["id"] == servicio_id
    assert servicio["precio"] == 25000
    assert servicio["activo"] == 1


def test_desactivar_servicio_lo_oculta_de_lista_activa(temp_db):
    modelo = ServicioModel()
    servicio_id = modelo.crear("Barba", 15000, "Arreglo de barba", 20)

    modelo.desactivar(servicio_id)
    activos = modelo.listar(solo_activos=True)
    todos = modelo.listar(solo_activos=False)

    assert all(servicio["id"] != servicio_id for servicio in activos)
    assert any(servicio["id"] == servicio_id for servicio in todos)
