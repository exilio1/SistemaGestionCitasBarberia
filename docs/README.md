# Barbers Studio

Barbers Studio es el proyecto que desarrollé para el curso de proyecto integrador. Es un sistema de escritorio hecho en Python para que una barbería pueda gestionar sus citas, pagos y empleados desde un solo programa.

La idea surgió porque la barbería con la que trabajé como caso de estudio manejaba todo en una libreta y por WhatsApp, lo que generaba problemas constantemente: citas dobles, clientes que llegaban a una hora que no era, y no había forma de saber cuánto se estaba ingresando realmente.

---

## ¿Qué puede hacer el sistema?

- Agendar y gestionar citas con los barberos
- Ver la agenda del día como un calendario por columnas
- Registrar pagos y generar facturas en PDF
- Ver reportes de ingresos y gastos
- Administrar el equipo de trabajo con sus porcentajes de ganancia
- Gestionar los servicios que ofrece la barbería
- Llevar un control de los gastos del negocio
- Recibir solicitudes de citas por Telegram con un bot

---

## Tecnologías que usé

| Tecnología | Para qué la usé |
|---|---|
| Python 3.12 | Lenguaje principal del proyecto |
| CustomTkinter | Para construir la interfaz gráfica |
| SQLite | Base de datos local del sistema |
| python-telegram-bot | Para el bot de Telegram |
| bcrypt | Para cifrar las contraseñas |
| ReportLab | Para generar los PDFs de facturas |
| PyInstaller | Para empaquetar el ejecutable final |

---

## Roles del sistema

Hay dos tipos de usuario. El **administrador** tiene acceso completo a todo, incluyendo reportes financieros y configuración del equipo. La **recepcionista** solo puede ver y gestionar la agenda y la facturación del día a día.

Esto lo decidí así porque no tenía sentido que una recepcionista pudiera ver los reportes de ingresos y los sueldos de los empleados.

---

> Proyecto desarrollado en el programa de Tecnología en Desarrollo de Software — Universidad Santiago de Cali.
