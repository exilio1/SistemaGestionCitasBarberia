"""
Gestor del bot de mensajería (Telegram / WhatsApp).
RF12 Confirmación | RF13 Recordatorio | RNF06: bot 24/7 | RNF08: tolerancia a fallos
Aquí decido qué bot arrancar según la configuración en config.py.
"""

from app.config import BOT_PROVIDER


def start_bot():
    """Arranca el bot configurado en BOT_PROVIDER.
    Si es 'telegram', importa y ejecuta el módulo del bot de Telegram.
    Si es 'whatsapp', lanza un error porque todavía no está implementado.
    """
    if BOT_PROVIDER == "telegram":
        # Importo aquí para no cargar el módulo si no se necesita
        from app.bot import telegram_bot
        telegram_bot.main()
    elif BOT_PROVIDER == "whatsapp":
        raise NotImplementedError("Integración WhatsApp Business API pendiente")
    else:
        raise ValueError(f"BOT_PROVIDER no reconocido: {BOT_PROVIDER}")
