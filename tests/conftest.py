import pytest

from app.core import database


@pytest.fixture()
def temp_db(tmp_path, monkeypatch):
    """Crea una base SQLite temporal para no tocar la base real del proyecto."""
    db_path = tmp_path / "barberia_test.db"
    monkeypatch.setattr(database, "DB_PATH", db_path)
    database.init_db()
    return db_path
