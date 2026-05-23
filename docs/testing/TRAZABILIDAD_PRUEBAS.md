# Trazabilidad de pruebas

## Resumen

Esta trazabilidad relaciona los casos probados con los modulos principales del sistema. Todos los casos listados fueron ejecutados con Pytest y terminaron en estado aprobado.

| Caso | Modulo | Archivo de prueba | Validacion principal | Estado |
|---|---|---|---|---|
| CP001 | Autenticacion | `tests/test_auth.py` | Hash de contrasena no queda en texto plano | Aprobado |
| CP002 | Autenticacion | `tests/test_auth.py` | Verificacion de contrasena correcta | Aprobado |
| CP003 | Permisos | `tests/test_auth.py` | Administrador accede a reportes | Aprobado |
| CP004 | Permisos | `tests/test_auth.py` | Recepcionista no accede a reportes | Aprobado |
| CP005 | Clientes | `tests/test_cliente_model.py` | Formato de cedula | Aprobado |
| CP006 | Clientes | `tests/test_cliente_model.py` | Reutilizacion de cliente por cedula | Aprobado |
| CP007 | Usuarios | `tests/test_usuario_model.py` | Crear y autenticar usuario correcto | Aprobado |
| CP008 | Usuarios | `tests/test_usuario_model.py` | Rechazar contrasena incorrecta | Aprobado |
| CP009 | Empleados | `tests/test_empleado_model.py` | Crear empleado y consultar por ID | Aprobado |
| CP010 | Citas | `tests/test_cita_model.py` | Crear cita pendiente | Aprobado |
| CP011 | Citas | `tests/test_cita_model.py` | Confirmar cita pendiente | Aprobado |
| CP012 | Citas | `tests/test_cita_model.py` | Cancelar cita no completada | Aprobado |
| CP013 | Servicios | `tests/test_servicio_model.py` | Crear servicio y consultar por nombre | Aprobado |
| CP014 | Servicios | `tests/test_servicio_model.py` | Desactivar servicio y ocultarlo de activos | Aprobado |
| CP015 | Pagos | `tests/test_pago_model.py` | Registrar pago y calcular ganancias | Aprobado |
| CP016 | Pagos | `tests/test_pago_model.py` | Evitar doble pago en la misma cita | Aprobado |
| CP017 | Pagos | `tests/test_pago_model.py` | Consultar ingresos por periodo | Aprobado |
| CP018 | Facturas | `tests/test_factura_model.py` | Generar factura para pago existente | Aprobado |
| CP019 | Facturas | `tests/test_factura_model.py` | No generar factura para pago inexistente | Aprobado |
| CP020 | Gastos | `tests/test_gasto_model.py` | Crear gasto y sumar total por periodo | Aprobado |
| CP021 | Gastos | `tests/test_gasto_model.py` | Actualizar y eliminar gasto | Aprobado |
| CP022 | Seguridad | `tests/test_security.py` | Usuario inactivo no puede autenticarse | Aprobado |
| CP023 | Seguridad | `tests/test_security.py` | No permitir correos duplicados | Aprobado |
| CP024 | Seguridad | `tests/test_security.py` | Restringir permisos administrativos a recepcionista | Aprobado |
| CP025 | Seguridad | `tests/test_security.py` | `.env.example` no contiene token real | Aprobado |
| CP026 | Seguridad | `tests/test_security.py` | No hay token Telegram hardcodeado | Aprobado |
| CP027 | Rendimiento | `tests/test_performance.py` | Login menor a 3 segundos | Aprobado |
| CP028 | Rendimiento | `tests/test_performance.py` | Crear cita menor a 3 segundos | Aprobado |
| CP029 | Rendimiento | `tests/test_performance.py` | Pago y factura menor a 3 segundos | Aprobado |
| CP030 | Rendimiento | `tests/test_performance.py` | Consultas financieras menor a 3 segundos | Aprobado |
| CP031 | 2FA | `tests/test_2fa.py` | Generar secreto TOTP valido | Aprobado |
| CP032 | 2FA | `tests/test_2fa.py` | Generar URI para Google Authenticator | Aprobado |
| CP033 | 2FA | `tests/test_2fa.py` | Aceptar codigo TOTP correcto | Aprobado |
| CP034 | 2FA | `tests/test_2fa.py` | Rechazar codigo TOTP incorrecto | Aprobado |
| CP035 | 2FA | `tests/test_2fa.py` | Guardar secreto TOTP en usuario | Aprobado |

## Resultado

```text
35 passed
```

## Observacion final

La trazabilidad se mantiene en formato Markdown para que pueda verse directamente desde GitHub dentro de la carpeta `docs/testing`.
