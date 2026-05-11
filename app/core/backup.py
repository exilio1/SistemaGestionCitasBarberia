"""
Respaldos automáticos de la base de datos.
RNF07: seguridad y protección de datos — aquí hago una copia del archivo .db
"""

import shutil
from datetime import datetime
from app.config import DB_PATH, BACKUP_DIR


def crear_backup() -> str:
    """Crea una copia de seguridad del archivo de la base de datos.
    El nombre del archivo incluye la fecha y hora para no sobrescribir backups anteriores.
    Retorna la ruta donde se guardó el backup.
    """
    # Creo la carpeta de backups si no existe
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    # El timestamp queda en formato YYYYMMDD_HHMMSS para ordenar fácil
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = BACKUP_DIR / f"barberia_{timestamp}.db"

    # Copio el archivo de la BD al destino con metadatos (copy2 preserva fechas)
    shutil.copy2(DB_PATH, destino)
    return str(destino)


def crear_backup_automatico():
    """Crea un respaldo diario automático si no existe el de hoy."""
    if not DB_PATH.exists():
        return None

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    nombre_hoy = datetime.now().strftime("barberia_%Y%m%d.db")
    destino = BACKUP_DIR / nombre_hoy

    if destino.exists():
        return str(destino)

    shutil.copy2(DB_PATH, destino)
    return str(destino)
