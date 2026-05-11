"""
Configuración global del sistema.
Aquí centralizo todas las constantes que usa la aplicación:
rutas, horarios, porcentajes y configuración del bot.
"""

import os
from pathlib import Path

# Rutas base del proyecto — uso Path para que funcione en Windows y Mac
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
BACKUP_DIR = DATA_DIR / "backups"
# Ruta del archivo de la base de datos SQLite
DB_PATH = DATA_DIR / "barberia.db"

# Horario de operación de la barbería (formato HH:MM)
HORARIO_INICIO = "08:00"
HORARIO_FIN = "19:00"
# Días en los que la barbería está abierta
DIAS_OPERACION = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]

# Distribución de ganancias por defecto (el admin puede cambiar esto)
# El empleado se lleva el 60% y el negocio el 40% de cada servicio
PORCENTAJE_EMPLEADO = 60
PORCENTAJE_NEGOCIO = 40

# Qué proveedor de bot se usa — puede ser "telegram" o "whatsapp"
BOT_PROVIDER = "telegram"

# Cuántos minutos antes de la cita se le envía el recordatorio al cliente
REMINDER_MINUTES = 60

# Tiempo máximo de respuesta en segundos (para medir rendimiento)
MAX_RESPONSE_TIME = 2
