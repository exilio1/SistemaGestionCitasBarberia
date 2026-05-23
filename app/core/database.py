import sqlite3
import os
from app.config import DB_PATH


def get_connection():
    # Crear la carpeta de datos si no existe
    os.makedirs(str(DB_PATH.parent), exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    # Crear las tablas al iniciar la aplicacion
    from app.core import schema
    conn = get_connection()
    conn.executescript(schema.CREATE_TABLES)
    # Migración: si la BD ya existía sin totp_secret se agrega sin borrar datos
    cols = [r[1] for r in conn.execute("PRAGMA table_info(usuarios)").fetchall()]
    if "totp_secret" not in cols:
        conn.execute("ALTER TABLE usuarios ADD COLUMN totp_secret TEXT DEFAULT NULL")
        conn.commit()
    conn.close()
