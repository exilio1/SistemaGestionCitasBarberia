# Instalación

El sistema se puede usar de dos formas: descargando el ejecutable directamente o corriendo el código fuente con Python. La primera opción es para el cliente final y la segunda es para quien quiera revisar o modificar el código.

---

## Con el ejecutable (para usuarios finales)

Esta es la forma más sencilla. No necesita instalar Python ni nada adicional.

1. Descargar el archivo `BarberStudio-Windows.zip` o `BarberStudio-macOS.zip` desde la sección Releases del repositorio en GitHub
2. Descomprimir el archivo
3. Abrir la carpeta `BarberStudio` y ejecutar el programa
4. En macOS puede que aparezca un aviso de seguridad la primera vez — hay que ir a **Preferencias del Sistema → Seguridad y Privacidad** y permitir la ejecución

La primera vez que se abre el sistema se crea automáticamente la base de datos vacía y se puede registrar el primer usuario administrador.

---

## Desde el código fuente (para desarrolladores)

### Requisitos
- Python 3.11 o superior
- Git
- pip

### Pasos

Clonar el repositorio:
```bash
git clone https://github.com/exilio1/SistemaGestionCitasBarberia
cd SistemaGestionCitasBarberia
```

Crear y activar el entorno virtual:
```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

Instalar dependencias:
```bash
pip install -r requirements.txt
```

Ejecutar:
```bash
python -m app.main
```

---

## Primera vez que se abre

Al iniciar por primera vez el sistema crea la base de datos automáticamente en la carpeta `data/`. Desde la pantalla de inicio de sesión se puede registrar el usuario administrador usando el enlace "Registrarse".

> La carpeta `data/` no se debe borrar porque ahí está toda la información del negocio.
