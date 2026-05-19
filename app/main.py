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
    Lanza el bot como proceso independiente para que tenga su propio
    event loop de asyncio sin conflictos con la interfaz grafica.

    - App empaquetada con PyInstaller: ejecuta el mismo binario con --bot-only
    - Modo desarrollo (python -m app.main): ejecuta el modulo del bot directamente
    """
    try:
        entorno = os.environ.copy()

        if getattr(sys, 'frozen', False):
            # Ejecutable empaquetado — el binario sabe manejar --bot-only
            cmd = [sys.executable, '--bot-only']
        else:
            # Modo desarrollo — lanzamos el modulo del bot como subproceso de Python
            cmd = [sys.executable, '-m', 'app.bot.telegram_bot']

        subprocess.Popen(
            cmd,
            env=entorno,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
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
