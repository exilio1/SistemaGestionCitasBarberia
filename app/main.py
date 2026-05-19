"""
Punto de entrada de la aplicación de escritorio.
Inicializa la BD y arranca el ciclo MVC:
  MainView → AuthController → DashboardView + Controllers por módulo
El bot de Telegram arranca automaticamente en un hilo de fondo.
"""

import threading
import customtkinter as ctk
from app.core.backup import crear_backup_automatico
from app.core.database import init_db
from app.views.main_view import MainView


def _iniciar_bot():
    """
    Arranca el bot de Telegram en un hilo separado para no bloquear la app.
    Si no hay token configurado o la libreria no esta instalada, no hace nada
    y la app sigue funcionando normal.
    """
    try:
        from app.bot.telegram_bot import main as bot_main
        bot_main()
    except Exception:
        # Sin token o sin libreria telegram — la app funciona igual sin el bot
        pass


def main():
    # Primero inicializo la base de datos (crea las tablas si no existen)
    init_db()
    crear_backup_automatico()

    # Arranco el bot en un hilo daemon — se cierra solo cuando se cierra la app
    hilo_bot = threading.Thread(target=_iniciar_bot, daemon=True)
    hilo_bot.start()

    # Configuro el tema visual de la app: modo oscuro con colores azul
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    # Creo la ventana principal y arranco el loop de eventos
    ventana = MainView()
    ventana.mainloop()


# Solo ejecuto main() si este archivo se corre directamente
if __name__ == "__main__":
    main()
