"""
Punto de entrada del bot de Telegram — Barbers Studio.

Para correr el bot (en una terminal separada a la app):
    venv/bin/python -m app.bot.telegram_bot

El bot comparte la misma base de datos SQLite con la app de escritorio.
Las citas que el bot crea aparecen automáticamente en la Agenda del sistema.
"""

import os
import sys
import logging
from dotenv import load_dotenv


def _cargar_env():
    """
    Busca el archivo .env en la ubicacion correcta segun si es app empaquetada
    con PyInstaller o codigo fuente corriendo en desarrollo.
    """
    if getattr(sys, 'frozen', False):
        # App empaquetada — el ejecutable esta dentro del .app o carpeta dist
        exe = sys.executable
        if sys.platform == 'darwin':
            # Estructura: BarberStudio.app/Contents/MacOS/BarberStudio
            # El .env esta junto al .app, tres niveles arriba del ejecutable
            app_bundle = os.path.dirname(os.path.dirname(os.path.dirname(exe)))
            env_path = os.path.join(os.path.dirname(app_bundle), '.env')
        else:
            # Windows: BarberStudio/BarberStudio.exe
            # El .env esta en la misma carpeta que el .exe
            env_path = os.path.join(os.path.dirname(exe), '.env')
        if os.path.exists(env_path):
            load_dotenv(env_path)
            return
    # Modo desarrollo — busca el .env en el directorio actual
    load_dotenv()

# Importo los manejadores de eventos de la librería python-telegram-bot
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
)

# Importo todos los handlers y constantes de estado desde el módulo handlers
from app.bot.handlers import (
    # /start
    start,
    # /agendar — 9 pasos incluyendo cédula con confirmación
    agendar_start,
    nombre_recibido,
    cedula_recibida,
    confirmar_cedula,
    telefono_recibido,
    servicio_recibido,
    barbero_recibido,
    fecha_recibida,
    hora_recibida,
    confirmar_cita,
    salir_flujo,
    # /cancelar
    cancelar_start,
    codigo_cancelar_recibido,
    # /reprogramar
    reprogramar_start,
    codigo_reprog_recibido,
    fecha_reprog_recibida,
    hora_reprog_recibida,
    # /micita
    micita_start,
    codigo_micita_recibido,
    # Constantes de estado que usa el ConversationHandler para saber en qué paso voy
    NOMBRE, CEDULA, CONFIRMAR_CEDULA, TELEFONO, SERVICIO, BARBERO, FECHA, HORA, CONFIRMAR,
    CODIGO_CANCELAR,
    CODIGO_REPROG, FECHA_REPROG, HORA_REPROG,
    CODIGO_MICITA,
)

# ── Configuración de logs ─────────────────────────────────────────────────────
# Configuro el sistema de logs para ver qué hace el bot en tiempo real
logging.basicConfig(
    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def main():
    # Cargo las variables de entorno desde el .env (busca en la ubicacion correcta)
    _cargar_env()
    token = os.getenv("TELEGRAM_BOT_TOKEN")

    # Verifico que el token esté configurado correctamente
    if not token or token == "pon_aqui_tu_token_de_botfather":
        print()
        print("ERROR: No se encontró el token del bot.")
        print("Abre el archivo .env y reemplaza la línea:")
        print("  TELEGRAM_BOT_TOKEN=pon_aqui_tu_token_de_botfather")
        print("con tu token real de BotFather.")
        print()
        return

    # Creo la aplicación del bot y registro los comandos del menu de Telegram
    app = Application.builder().token(token).build()

    # ── Flujo /agendar (9 pasos) ─────────────────────────────────────────────
    # El ConversationHandler guía al usuario por estos pasos:
    # nombre → cédula → [confirmar cédula] → teléfono
    # → servicio → barbero → fecha → hora → confirmar
    # allow_reentry=True permite reiniciar el flujo en cualquier momento.
    # Sin esto, si el usuario queda atascado en un paso (por ejemplo en el
    # calendario) y escribe /agendar de nuevo, el bot lo ignora completamente.
    conv_agendar = ConversationHandler(
        entry_points=[CommandHandler("agendar", agendar_start)],
        states={
            NOMBRE:           [MessageHandler(filters.TEXT & ~filters.COMMAND, nombre_recibido)],
            CEDULA:           [MessageHandler(filters.TEXT & ~filters.COMMAND, cedula_recibida)],
            CONFIRMAR_CEDULA: [CallbackQueryHandler(confirmar_cedula)],
            TELEFONO:         [MessageHandler(filters.TEXT & ~filters.COMMAND, telefono_recibido)],
            SERVICIO:         [CallbackQueryHandler(servicio_recibido)],
            BARBERO:          [CallbackQueryHandler(barbero_recibido)],
            FECHA:            [CallbackQueryHandler(fecha_recibida)],
            HORA:             [CallbackQueryHandler(hora_recibida)],
            CONFIRMAR:        [CallbackQueryHandler(confirmar_cita)],
        },
        fallbacks=[CommandHandler("salir", salir_flujo)],
        per_message=False,
        allow_reentry=True,
    )

    # ── Flujo /cancelar (1 paso) ──────────────────────────────────────────────
    conv_cancelar = ConversationHandler(
        entry_points=[CommandHandler("cancelar", cancelar_start)],
        states={
            CODIGO_CANCELAR: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, codigo_cancelar_recibido)
            ],
        },
        fallbacks=[CommandHandler("salir", salir_flujo)],
        allow_reentry=True,
    )

    # ── Flujo /reprogramar (3 pasos) ─────────────────────────────────────────
    conv_reprogramar = ConversationHandler(
        entry_points=[CommandHandler("reprogramar", reprogramar_start)],
        per_message=False,
        states={
            CODIGO_REPROG: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, codigo_reprog_recibido)
            ],
            FECHA_REPROG: [CallbackQueryHandler(fecha_reprog_recibida)],
            HORA_REPROG: [CallbackQueryHandler(hora_reprog_recibida)],
        },
        fallbacks=[CommandHandler("salir", salir_flujo)],
        allow_reentry=True,
    )

    # ── Flujo /micita (1 paso) ────────────────────────────────────────────────
    conv_micita = ConversationHandler(
        entry_points=[CommandHandler("micita", micita_start)],
        states={
            CODIGO_MICITA: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, codigo_micita_recibido)
            ],
        },
        fallbacks=[CommandHandler("salir", salir_flujo)],
        allow_reentry=True,
    )

    # Registro todos los handlers en la aplicación del bot
    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_agendar)
    app.add_handler(conv_cancelar)
    app.add_handler(conv_reprogramar)
    app.add_handler(conv_micita)

    # Registro los comandos del menu de Telegram (aparecen al tocar el icono "/" en el chat)
    # Esto hace que el boton de menu siempre este disponible para el cliente
    async def _registrar_comandos(app):
        from telegram import BotCommand
        await app.bot.set_my_commands([
            BotCommand("start",        "Inicio — ver todos los comandos"),
            BotCommand("agendar",      "Reservar una nueva cita"),
            BotCommand("cancelar",     "Cancelar tu cita"),
            BotCommand("reprogramar",  "Cambiar la fecha u hora de tu cita"),
            BotCommand("micita",       "Consultar el estado de tu cita"),
            BotCommand("salir",        "Cancelar la operacion actual"),
        ])

    app.post_init = _registrar_comandos

    # Arranco el bot en modo polling (se queda escuchando mensajes)
    print()
    print("Bot de Barbers Studio iniciado.")
    print("Presiona Ctrl+C para detener.")
    print()
    app.run_polling(allowed_updates=["message", "callback_query"])


def run():
    """Alias sencillo para arrancar el bot desde otros módulos."""
    main()


if __name__ == "__main__":
    main()
