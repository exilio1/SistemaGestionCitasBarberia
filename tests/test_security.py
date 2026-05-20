import re
import sqlite3
from pathlib import Path

import pytest

from app.core.auth import tiene_permiso
from app.models.usuario_model import UsuarioModel


def test_usuario_inactivo_no_puede_autenticarse(temp_db):
    modelo = UsuarioModel()
    usuario_id = modelo.crear("Admin", "admin@test.com", "Seguro123", "administrador")

    modelo.desactivar(usuario_id)
    usuario = modelo.autenticar("admin@test.com", "Seguro123")

    assert usuario is None


def test_no_permite_correos_duplicados(temp_db):
    modelo = UsuarioModel()
    modelo.crear("Admin", "admin@test.com", "Seguro123", "administrador")

    with pytest.raises(sqlite3.IntegrityError):
        modelo.crear("Admin 2", "admin@test.com", "Seguro123", "administrador")


def test_recepcionista_no_tiene_permisos_de_administracion():
    modulos_admin = ["Reportes", "Equipo", "Servicios", "Gastos", "Empleados"]

    for modulo in modulos_admin:
        assert tiene_permiso("recepcionista", modulo) is False


def test_env_example_no_incluye_token_real():
    contenido = Path(".env.example").read_text(encoding="utf-8")

    assert "TELEGRAM_BOT_TOKEN=" in contenido
    assert re.search(r"TELEGRAM_BOT_TOKEN=\s*$", contenido, re.MULTILINE)


def test_no_hay_token_telegram_hardcodeado_en_codigo_fuente():
    patron_token_telegram = re.compile(r"\b\d{8,}:[A-Za-z0-9_-]{20,}\b")
    rutas = list(Path("app").rglob("*.py")) + list(Path(".github").rglob("*.yml"))

    hallazgos = []
    for ruta in rutas:
        contenido = ruta.read_text(encoding="utf-8", errors="ignore")
        if patron_token_telegram.search(contenido):
            hallazgos.append(str(ruta))

    assert hallazgos == []
