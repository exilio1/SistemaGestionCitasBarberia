"""
Punto de entrada de la aplicación de escritorio.
Inicializa la BD y arranca el ciclo MVC:
  MainView → AuthController → DashboardView + Controllers por módulo

El bot de Telegram corre como proceso separado para evitar conflictos
con el event loop de asyncio dentro de la app empaquetada con PyInstaller.
Si se lanza con --bot-only arranca solo el bot sin la interfaz grafica.
"""

import os
import sys
import subprocess
import customtkinter as ctk
from app.core.backup import crear_backup_automatico
from app.core.database import init_db
from app.views.main_view import MainView


def _correr_solo_bot():
    """
    Modo bot-only: arranca el bot de Telegram sin la interfaz grafica.
    Se usa cuando el ejecutable se lanza con el argumento --bot-only.
    """
    init_db()
    from app.bot.telegram_bot import main as bot_main
    bot_main()


def _lanzar_proceso_bot():
    """
    Lanza el bot como proceso independiente usando el mismo ejecutable
    con el argumento --bot-only. Asi cada proceso tiene su propio
    event loop de asyncio y no hay conflictos con la interfaz grafica.
    """
    try:
        # Heredamos todas las variables de entorno del proceso principal
        # para que el bot tenga acceso al token de Telegram
        entorno = os.environ.copy()
        subprocess.Popen(
            [sys.executable, '--bot-only'],
            env=entorno,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        # Si el bot no puede iniciar la app sigue funcionando normal
        pass


def main():
    # Si se llama con --bot-only solo arranca el bot y termina
    if '--bot-only' in sys.argv:
        _correr_solo_bot()
        return

    # Inicializo la base de datos (crea las tablas si no existen)
    init_db()
    crear_backup_automatico()

    # Lanzo el bot como proceso separado antes de abrir la ventana
    _lanzar_proceso_bot()

    # Configuro el tema visual: modo oscuro con acentos en azul
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    # Creo la ventana principal y arranco el loop de eventos
    ventana = MainView()
    ventana.mainloop()


if __name__ == "__main__":
    main()
