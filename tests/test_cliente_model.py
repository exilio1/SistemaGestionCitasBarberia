from app.models.cliente_model import ClienteModel, formatear_cedula


def test_formatear_cedula_agrega_puntos_de_miles():
    assert formatear_cedula("1234567890") == "1.234.567.890"


def test_obtener_o_crear_reutiliza_cliente_por_cedula(temp_db):
    modelo = ClienteModel()

    cliente_id = modelo.obtener_o_crear("Ana Perez", "1234567890", "3001112233")
    cliente_repetido_id = modelo.obtener_o_crear("Ana Perez", "1234567890", "3001112233")

    assert cliente_id == cliente_repetido_id
