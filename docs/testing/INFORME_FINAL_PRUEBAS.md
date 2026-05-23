# Informe final de pruebas

## Proyecto

Sistema de Gestion Integral de Citas con Agendamiento y Control Operativo.

## Rol

Tester / aseguramiento de calidad.

## Objetivo

Validar por medio de pruebas automatizadas con Pytest que las funciones principales del sistema trabajan correctamente antes de la entrega final del proyecto.

Las pruebas se enfocaron principalmente en la logica del sistema, modelos, reglas de negocio, seguridad basica y tiempos de respuesta. La interfaz grafica no se probo de forma automatizada porque el alcance indicado para esta fase fue validar el comportamiento mediante Pytest.

## Herramientas utilizadas

- Python
- Pytest
- pytest-cov
- SQLite temporal para pruebas
- GitHub Actions para ejecucion automatica en el repositorio

## Comando principal de ejecucion

```bash
python -m pytest -q tests --cov=app.core --cov=app.models --cov-report=term-missing
```

## Resultado final

```text
35 passed
Cobertura total en app.core y app.models: 57%
```

## Modulos validados

- Autenticacion y permisos
- Autenticacion de doble factor 2FA con TOTP
- Usuarios
- Clientes
- Empleados
- Citas
- Servicios
- Pagos
- Facturas
- Gastos
- Seguridad basica
- Tiempo de respuesta menor a 3 segundos

## Seguridad validada

Se probaron los siguientes puntos:

- Las contrasenas se guardan con hash y no como texto plano.
- Usuarios inactivos no pueden autenticarse.
- Correos duplicados no son permitidos.
- Los permisos por rol restringen modulos administrativos.
- No se encontraron tokens reales de Telegram escritos directamente en el codigo fuente.
- El archivo `.env.example` no contiene token real.
- El 2FA genera una clave TOTP valida.
- El 2FA genera URI compatible con Google Authenticator.
- El 2FA acepta codigos correctos y rechaza codigos incorrectos.
- El secreto TOTP se guarda correctamente para el usuario.

## Tiempo de respuesta

Se validaron operaciones principales con un limite maximo de 3 segundos:

- Login de usuario.
- Creacion de cita.
- Registro de pago y generacion de factura.
- Consulta de ingresos y gastos del periodo.

Todas las operaciones medidas cumplieron el tiempo esperado.

## Observaciones

- Las pruebas usan una base de datos temporal para no afectar la informacion real del proyecto.
- Las pruebas se ejecutan tambien desde GitHub Actions cuando se suben cambios a la rama de testing.
- Las pruebas automatizadas no reemplazan completamente una revision visual de la interfaz, pero si permiten validar la logica principal del sistema.
- HSTS no aplica directamente porque el sistema es una aplicacion de escritorio y no un sitio web HTTP propio.

## Conclusion

El ciclo final de pruebas automatizadas fue aprobado. Las 35 pruebas ejecutadas con Pytest pasaron correctamente, incluyendo pruebas unitarias, seguridad, 2FA y tiempo de respuesta. Con esto se deja evidencia tecnica de que la logica principal del sistema funciona segun lo esperado para la entrega final.
