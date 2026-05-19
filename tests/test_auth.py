from app.core.auth import hash_password, tiene_permiso, verify_password


def test_hash_password_no_guarda_texto_plano():
    password = "Prueba123"

    hashed = hash_password(password)

    assert hashed != password


def test_verify_password_acepta_password_correcta():
    password = "Prueba123"
    hashed = hash_password(password)

    assert verify_password(password, hashed) is True


def test_administrador_tiene_permiso_reportes():
    assert tiene_permiso("administrador", "Reportes") is True


def test_recepcionista_no_tiene_permiso_reportes():
    assert tiene_permiso("recepcionista", "Reportes") is False
