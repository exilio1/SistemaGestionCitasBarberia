# -*- mode: python ; coding: utf-8 -*-
# Archivo de configuracion de PyInstaller para BarberStudio
# Lista todos los modulos que se cargan dinamicamente con importlib
# para que el ejecutable los incluya correctamente

import sys
from PyInstaller.utils.hooks import collect_all

# ── Modulos dinamicos del dashboard (importlib no los detecta solo) ───────────
modulos_ocultos = [
    # Vistas de pantallas
    'app.views.screens.panel_principal_view',
    'app.views.screens.agenda_view',
    'app.views.screens.facturacion_view',
    'app.views.screens.reportes_view',
    'app.views.screens.equipo_view',
    'app.views.screens.gastos_view',
    'app.views.screens.ayuda_view',
    'app.views.screens.citas_view',
    'app.views.screens.empleados_view',
    'app.views.screens.modal_nueva_cita',
    'app.views.screens.cliente_solicitar_view',
    'app.views.screens.pagos_view',
    'app.views.screens.factura_view',
    'app.views.screens.pago_barbero_view',
    # Controladores
    'app.controllers.panel_principal_controller',
    'app.controllers.agenda_controller',
    'app.controllers.facturacion_controller',
    'app.controllers.reportes_controller',
    'app.controllers.equipo_controller',
    'app.controllers.gastos_controller',
    'app.controllers.ayuda_controller',
    'app.controllers.citas_controller',
    'app.controllers.empleados_controller',
    'app.controllers.pagos_controller',
    'app.controllers.factura_controller',
    'app.controllers.pago_barbero_controller',
    'app.controllers.cliente_controller',
    'app.controllers.auth_controller',
    'app.controllers.registro_controller',
    # Modelos
    'app.models.usuario_model',
    'app.models.empleado_model',
    'app.models.cliente_model',
    'app.models.cita_model',
    'app.models.servicio_model',
    'app.models.pago_model',
    'app.models.factura_model',
    'app.models.gasto_model',
    # Servicios y core
    'app.services.agenda_service',
    'app.core.auth',
    'app.core.database',
    'app.core.backup',
    'app.core.schema',
    # Componentes de vistas
    'app.views.components.sidebar',
    'app.views.components.header',
    'app.views.components.tooltip',
    'app.views.components.calendario',
]

# Recopilo assets de customtkinter (temas, fuentes, imagenes)
ctk_datas, ctk_binaries, ctk_hidden = collect_all('customtkinter')

a = Analysis(
    ['app/main.py'],
    pathex=['.'],
    binaries=ctk_binaries,
    datas=ctk_datas,
    hiddenimports=modulos_ocultos + ctk_hidden,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='BarberStudio',
    debug=False,
    strip=False,
    upx=True,
    console=False,          # sin ventana de terminal
    argv_emulation=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name='BarberStudio',
)

# En macOS ademas empaqueta como .app nativo
if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name='BarberStudio.app',
        icon=None,
        bundle_identifier='com.barbersstudio.app',
        info_plist={
            'NSHighResolutionCapable': True,
            'CFBundleShortVersionString': '1.0.0',
            'CFBundleName': 'Barbers Studio',
        },
    )
