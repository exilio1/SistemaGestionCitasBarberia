# Barbers Studio — Sistema de Gestión de Citas para Barbería

Barbers Studio es un sistema de escritorio desarrollado en Python para gestionar todo lo relacionado con el día a día de una barbería. La idea surgió porque muchas barberías pequeñas siguen manejando sus citas en libretas o por WhatsApp, lo que genera problemas de organización, pérdida de clientes y dificultad para llevar un control de los ingresos.

El sistema permite que el administrador y la recepcionista puedan registrar citas, llevar el control de pagos, generar reportes y administrar al equipo de trabajo, todo desde una sola aplicación sin necesidad de conexión a internet.

---

## ¿Para qué sirve?

- Registrar y gestionar citas de clientes con los barberos disponibles
- Consultar la agenda del día organizada por hora y empleado
- Registrar pagos y generar facturas de forma rápida
- Ver reportes de ingresos, gastos y rendimiento por período
- Administrar el equipo de trabajo y sus porcentajes de ganancia
- Gestionar los servicios que ofrece la barbería con sus precios
- Llevar un control de los gastos del negocio
- Recibir solicitudes de citas a través de un bot de Telegram

---

## Tecnologías usadas

| Tecnología | Uso |
|---|---|
| Python 3.12 | Lenguaje principal del sistema |
| CustomTkinter | Interfaz gráfica de escritorio |
| SQLite | Base de datos local del sistema |
| python-telegram-bot | Bot para solicitudes por Telegram |
| bcrypt | Cifrado de contraseñas |
| ReportLab | Generación de PDFs (facturas y reportes) |
| PyInstaller | Empaquetado del sistema como ejecutable |

---

## Roles del sistema

El sistema tiene dos tipos de usuario:

**Administrador:** tiene acceso completo a todos los módulos, incluyendo reportes financieros, gestión de empleados, servicios y gastos.

**Recepcionista:** puede gestionar citas, agenda y facturación, pero no tiene acceso a reportes ni configuración del equipo.

---

> Proyecto desarrollado como parte del programa de Tecnología en Desarrollo de Software — Universidad Santiago de Cali.
