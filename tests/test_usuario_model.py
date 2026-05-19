from app.models.usuario_model import UsuarioModel


def test_crear_y_autenticar_usuario_correcto(temp_db):
    modelo = UsuarioModel()
    modelo.crear("Admin", "admin@test.com", "Seguro123", "administrador")

    usuario = modelo.autenticar("admin@test.com", "Seguro123")

    assert usuario is not None
    assert usuario["correo"] == "admin@test.com"
    assert usuario["rol"] == "administrador"


def test_autenticar_rechaza_password_incorrecta(temp_db):
    modelo = UsuarioModel()
    modelo.crear("Admin", "admin@test.com", "Seguro123", "administrador")

    usuario = modelo.autenticar("admin@test.com", "Incorrecta123")

    assert usuario is None
