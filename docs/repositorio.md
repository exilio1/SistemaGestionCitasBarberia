# Repositorio del Proyecto

El código fuente de Barbers Studio está disponible públicamente en GitHub.

---

## Repositorio principal

🔗 **https://github.com/CristianMarin19/imaginacms-iTasks**

El repositorio contiene:
- Todo el código fuente del sistema (carpeta `app/`)
- Los archivos de configuración de PyInstaller para el empaquetado
- Las pruebas automatizadas (carpeta `tests/`)
- Esta documentación (carpeta `docs/`)
- El archivo `requirements.txt` con todas las dependencias

---

## Ramas del repositorio

| Rama | Descripción |
|---|---|
| `main` | Versión estable del sistema. Solo se actualiza cuando hay una versión lista para producción. |
| `develop` | Rama de desarrollo principal. Aquí se integran los cambios antes de pasar a main. |
| `testing` | Rama para pruebas. Las pruebas automáticas se ejecutan al hacer push aquí. |

---

## Versiones publicadas

Las versiones empaquetadas del sistema (ejecutables para Windows y macOS) están disponibles en la sección **Releases** del repositorio en GitHub.

Cada release incluye:
- `BarberStudio-Windows.zip` — ejecutable para Windows
- `BarberStudio-macOS.zip` — ejecutable para macOS

El empaquetado se realiza automáticamente con GitHub Actions cuando se publica una nueva versión.

---

## Integración continua

El repositorio tiene configurados dos workflows de GitHub Actions:

**pytest.yml:** se ejecuta automáticamente cada vez que se hace push a las ramas `develop` o `testing`. Corre todas las pruebas del sistema y notifica si alguna falla.

**empaquetar.yml:** se activa manualmente cuando hay una nueva versión lista. Genera los ejecutables para Windows y macOS y los sube automáticamente como assets del release.

---

## Cómo contribuir

Si quieres proponer un cambio o reportar un error:
1. Crear un fork del repositorio
2. Crear una rama desde `develop` con un nombre descriptivo
3. Hacer los cambios y crear un pull request hacia `develop`
4. Describir qué cambió y por qué en la descripción del pull request
