# Arquitectura del Sistema

Para estructurar el proyecto usé el patrón **MVC (Modelo-Vista-Controlador)**. Lo elegí porque en clase lo habíamos visto y me pareció que era el que mejor se adaptaba a lo que necesitaba: separar la lógica del negocio de la interfaz gráfica para que cualquier cambio en una parte no dañara las demás.

Al principio mezclar todo en un solo archivo me parecía más rápido, pero después de los primeros módulos me di cuenta de que era un error porque cada cambio pequeño rompía otras cosas. Ahí fue cuando reorganicé todo con MVC y el desarrollo se volvió mucho más manejable.

---

## Las tres capas

**Modelos:** se encargan de hablar con la base de datos. Cada tabla tiene su propio modelo (citas, clientes, empleados, pagos, etc.). Los modelos no saben nada de la interfaz, solo trabajan con los datos.

**Vistas:** son las pantallas que ve el usuario, construidas con CustomTkinter. Decidí cargarlas de forma dinámica con `importlib` para que el sistema no cargue todos los módulos al arrancar, solo los que el usuario va abriendo.

**Controladores:** conectan las vistas con los modelos. Reciben lo que hace el usuario, consultan o modifican los datos y le devuelven el resultado a la vista.

---

## Estructura de carpetas

```
ProyectoBarberia/
├── app/
│   ├── main.py              # Punto de entrada
│   ├── config.py            # Rutas y configuración general
│   ├── core/
│   │   ├── auth.py          # Login y permisos por rol
│   │   ├── database.py      # Conexión a SQLite
│   │   ├── schema.py        # Definición de las tablas
│   │   └── backup.py        # Respaldo automático de la BD
│   ├── models/              # Un modelo por entidad
│   ├── views/
│   │   ├── login_view.py
│   │   ├── dashboard_view.py
│   │   ├── components/      # Sidebar, header, tooltips, etc.
│   │   └── screens/         # Pantalla de cada módulo
│   ├── controllers/         # Un controlador por módulo
│   └── bot/                 # Bot de Telegram
├── data/                    # Base de datos (se genera sola)
├── docs/                    # Esta documentación
├── tests/                   # Pruebas con pytest
└── requirements.txt
```

---

## Flujo de la aplicación

El sistema arranca en `main.py`, muestra el login, y al autenticarse carga el dashboard con el sidebar. Desde ahí, cada vez que el usuario navega a un módulo se carga dinámicamente su vista y su controlador.

---

## Seguridad básica implementada

Las contraseñas se guardan cifradas con **bcrypt**, nunca en texto plano. El acceso a cada módulo está controlado por el rol del usuario, así que aunque alguien intente acceder directamente a un módulo que no le corresponde, el sistema lo bloquea.

La base de datos se respalda automáticamente cada vez que se abre el sistema, en la carpeta `data/backups/`.
