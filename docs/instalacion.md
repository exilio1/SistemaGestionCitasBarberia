# Instalación del Sistema

Barbers Studio es una aplicación de escritorio. Para ejecutarla en un computador se puede hacer de dos formas: usando el ejecutable empaquetado (la forma más sencilla) o corriendo el código fuente directamente con Python.

---

## Opción 1 — Ejecutable empaquetado (recomendada para usuarios finales)

Esta opción no requiere instalar Python ni ninguna dependencia. Solo se descarga el archivo y se ejecuta.

1. Descargar el archivo `BarberStudio-macOS.zip` o `BarberStudio-Windows.zip` desde la sección de Releases del repositorio en GitHub.
2. Descomprimir el archivo descargado.
3. Abrir la carpeta `BarberStudio` y ejecutar el archivo `BarberStudio`.
4. En macOS, si el sistema bloquea la app por seguridad, ir a **Preferencias del Sistema → Seguridad y Privacidad** y permitir la ejecución.

La primera vez que se abre el sistema, se crea automáticamente la base de datos con un usuario administrador por defecto.

---

## Opción 2 — Ejecutar desde el código fuente

Esta opción es para desarrolladores que quieran modificar o estudiar el sistema.

### Requisitos previos

- Python 3.11 o superior
- Git instalado
- pip (viene incluido con Python)

### Pasos

**1. Clonar el repositorio**

```bash
git clone https://github.com/CristianMarin19/imaginacms-iTasks
cd ProyectoBarberia
```

**2. Crear un entorno virtual**

```bash
python -m venv venv
```

**3. Activar el entorno virtual**

En macOS / Linux:
```bash
source venv/bin/activate
```

En Windows:
```bash
venv\Scripts\activate
```

**4. Instalar las dependencias**

```bash
pip install -r requirements.txt
```

**5. Ejecutar el sistema**

```bash
python -m app.main
```

---

## Dependencias principales

El archivo `requirements.txt` incluye todas las librerías necesarias. Las más importantes son:

```
customtkinter
python-telegram-bot
bcrypt
reportlab
pillow
pyinstaller
```

---

## Primera ejecución

Al abrir el sistema por primera vez se inicializa la base de datos SQLite automáticamente. Si es la primera vez que se usa, se puede registrar un usuario administrador desde la pantalla de inicio de sesión usando el botón "Registrarse".

> **Nota:** la base de datos se guarda en la carpeta `data/` dentro del directorio del sistema. No eliminar esta carpeta porque contiene toda la información del negocio.
