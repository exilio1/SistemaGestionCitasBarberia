"""
Cola de solicitudes del bot cuando no hay conexión a internet.
RNF08: tolerancia a fallos — encola los mensajes y los procesa al reconectar.
Los mensajes pendientes se guardan en un archivo JSON local.
"""

import json
from pathlib import Path

# Ruta del archivo donde se guarda la cola de mensajes pendientes
QUEUE_FILE = Path("data/bot_queue.json")


def enqueue(mensaje: dict):
    """Agrega un mensaje a la cola cuando no se puede procesar en ese momento."""
    queue = _load()
    queue.append(mensaje)
    _save(queue)


def flush_queue(process_fn):
    """Procesa y vacía la cola al restablecer la conexión.
    Llama process_fn por cada mensaje pendiente.
    Si algún mensaje falla, lo conserva en la cola para el próximo intento.
    """
    queue = _load()
    pendientes = []
    for item in queue:
        try:
            # Intento procesar cada mensaje
            process_fn(item)
        except Exception:
            # Si falla, lo vuelvo a dejar pendiente para el próximo intento
            pendientes.append(item)
    # Guardo solo los mensajes que fallaron (los exitosos ya no se guardan)
    _save(pendientes)


def _load() -> list:
    """Carga la cola desde el archivo JSON. Retorna lista vacía si no existe el archivo."""
    if QUEUE_FILE.exists():
        return json.loads(QUEUE_FILE.read_text())
    return []


def _save(data: list):
    """Guarda la cola en el archivo JSON, creando la carpeta si no existe."""
    QUEUE_FILE.parent.mkdir(parents=True, exist_ok=True)
    QUEUE_FILE.write_text(json.dumps(data, indent=2))
