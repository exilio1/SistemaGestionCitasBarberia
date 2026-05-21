# Arquitectura del Sistema

Barbers Studio está construido siguiendo el patrón de diseño **Modelo-Vista-Controlador (MVC)**. Se eligió este patrón porque separa claramente las responsabilidades de cada parte del código, lo que hace más fácil hacer cambios sin romper otras funcionalidades.

---

## Patrón MVC aplicado

### Modelo
Los modelos se encargan de toda la interacción con la base de datos. Cada entidad del negocio tiene su propio modelo: citas, clientes, empleados, pagos, facturas, gastos, servicios y usuarios. Los modelos no saben nada de la interfaz, solo trabajan con los datos.

### Vista
Las vistas son las pantallas que ve el usuario. Están construidas con CustomTkinter y se cargan de forma dinámica usando `importlib`, lo que evita que el sistema cargue todos los módulos al inicio y hace que arranque más rápido.

### Controlador
Los controladores conectan las vistas con los modelos. Reciben las acciones del usuario (un clic en un botón, por ejemplo), consultan o modifican los datos a través del modelo y actualizan la vista con el resultado.

---

## Estructura de carpetas

```
ProyectoBarberia/
├── app/
│   ├── main.py                  # Punto de entrada del sistema
│   ├── config.py                # Configuración general (rutas, constantes)
│   ├── core/
│   │   ├── auth.py              # Autenticación y permisos por rol
│   │   ├── database.py          # Conexión a SQLite
│   │   ├── schema.py            # Definición de tablas de la base de datos
│   │   └── backup.py            # Respaldo automático de la base de datos
│   ├── models/                  # Acceso a datos por entidad
│   ├── views/
│   │   ├── login_view.py        # Pantalla de inicio de sesión
│   │   ├── dashboard_view.py    # Contenedor principal con sidebar
│   │   ├── components/          # Componentes reutilizables (sidebar, header, etc.)
│   │   └── screens/             # Pantallas de cada módulo
│   ├── controllers/             # Controladores de cada módulo
│   ├── services/                # Lógica de negocio transversal
│   └── bot/                     # Bot de Telegram
├── data/                        # Base de datos SQLite (se crea al iniciar)
├── docs/                        # Documentación del proyecto (esta carpeta)
├── tests/                       # Pruebas automatizadas
└── requirements.txt             # Dependencias del proyecto
```

---

## Flujo de navegación

```
main.py
  └── App (CTk)
        ├── LoginView + AuthController
        │     └── RegistroView + RegistroController
        └── DashboardView
              ├── Sidebar (navegación por rol)
              ├── Header (info del usuario y fecha)
              └── Área de contenido (carga módulos dinámicamente)
                    ├── PanelPrincipalView + PanelPrincipalController
                    ├── AgendaView + AgendaController
                    ├── FacturacionView + FacturacionController
                    ├── ReportesView + ReportesController
                    ├── EquipoView + EquipoController
                    ├── ServiciosView + ServiciosController
                    └── GastosView + GastosController
```

---

## Carga dinámica de módulos

Una decisión importante del diseño fue cargar los módulos con `importlib.import_module()` en lugar de importarlos todos al inicio. Esto significa que cuando el usuario abre el sistema solo se carga lo necesario para mostrar el login y el panel principal. Los demás módulos se cargan únicamente cuando el usuario navega a ellos.

Esto reduce el tiempo de arranque del sistema y el consumo de memoria, especialmente cuando se empaqueta como ejecutable con PyInstaller.

---

## Seguridad

- Las contraseñas de los usuarios se almacenan cifradas con **bcrypt** (hash + salt), nunca en texto plano.
- El acceso a cada módulo está controlado por un sistema de permisos basado en el rol del usuario (administrador o recepcionista).
- La base de datos SQLite se guarda localmente y se respalda automáticamente en la carpeta `data/backups/`.
