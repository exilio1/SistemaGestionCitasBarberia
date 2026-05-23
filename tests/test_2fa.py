import pyotp

from app.core.auth import (
    generar_totp_secret,
    guardar_totp_secret,
    obtener_totp_uri,
    verificar_totp,
)
from app.models.usuario_model import UsuarioModel


def test_generar_totp_secret_crea_clave_valida():
    secret = generar_totp_secret()

    assert isinstance(secret, str)
    assert len(secret) >= 16
    assert pyotp.TOTP(secret).now()


def test_obtener_totp_uri_genera_enlace_para_authenticator():
    secret = generar_totp_secret()

    uri = obtener_totp_uri(secret, "admin@test.com")

    assert uri.startswith("otpauth://totp/")
    assert "admin%40test.com" in uri or "admin@test.com" in uri
    assert "Barbers%20Studio" in uri or "Barbers Studio" in uri


def test_verificar_totp_acepta_codigo_correcto():
    secret = generar_totp_secret()
    codigo = pyotp.TOTP(secret).now()

    assert verificar_totp(secret, codigo) is True


def test_verificar_totp_rechaza_codigo_incorrecto():
    secret = generar_totp_secret()

    assert verificar_totp(secret, "000000") is False
    assert verificar_totp(secret, "") is False


def test_guardar_totp_secret_en_usuario(temp_db):
    modelo = UsuarioModel()
    usuario_id = modelo.crear("Admin", "admin@test.com", "Seguro123", "administrador")
    secret = generar_totp_secret()

    guardar_totp_secret(usuario_id, secret)
    usuario = modelo.obtener_por_id(usuario_id)

    assert usuario["totp_secret"] == secret
