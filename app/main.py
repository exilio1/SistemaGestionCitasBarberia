"""
Punto de entrada de la aplicación de escritorio.
Inicializa la BD y arranca el ciclo MVC:
  MainView → AuthController → DashboardView + Controllers por módulo
"""

import customtkinter as ctk
from app.core.backup import crear_backup_automatico
from app.core.database import init_db
from app.views.main_view import MainView


def main():
    # Primero inicializo la base de datos (crea las tablas si no existen)
    init_db()
    crear_backup_automatico()

    # Configuro el tema visual de la app: modo oscuro con colores azul
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    # Creo la ventana principal y arranco el loop de eventos
    ventana = MainView()
    ventana.mainloop()


# Solo ejecuto main() si este archivo se corre directamente
if __name__ == "__main__":
    main()
