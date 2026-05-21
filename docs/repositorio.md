# Repositorio

El código fuente del proyecto está disponible en GitHub.

🔗 **https://github.com/exilio1/SistemaGestionCitasBarberia**

---

## Qué hay en el repositorio

- Todo el código fuente en la carpeta `app/`
- La configuración de PyInstaller para empaquetar el ejecutable (`barber_studio.spec`)
- Las pruebas automatizadas en `tests/`
- Esta documentación en `docs/`
- El archivo `requirements.txt` con todas las dependencias

---

## Ramas

| Rama | Descripción |
|---|---|
| `main` | Versión estable. Solo se actualiza cuando hay algo listo para producción |
| `develop` | Rama de desarrollo. Aquí se integran los cambios antes de pasar a main |
| `testing` | Rama para pruebas. Las pruebas automáticas se ejecutan aquí |

---

## Versiones empaquetadas

Los ejecutables para Windows y macOS están en la sección **Releases** del repositorio. Se generan automáticamente con GitHub Actions cuando se publica una nueva versión.

---

## Integración continua

Hay dos workflows configurados en GitHub Actions:

- **pytest.yml:** corre las pruebas automáticamente con cada push a `develop` o `testing`
- **empaquetar.yml:** genera los ejecutables para Windows y macOS cuando se activa manualmente al publicar una versión
