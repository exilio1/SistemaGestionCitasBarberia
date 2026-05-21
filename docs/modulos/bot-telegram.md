# Bot de Telegram

Barbers Studio incluye un bot de Telegram que permite a los clientes de la barbería solicitar citas, consultar el estado de su cita y cancelar o reprogramar desde su celular, sin necesidad de llamar o ir personalmente.

---

## ¿Cómo funciona?

El bot corre como un proceso en segundo plano mientras el sistema está abierto. Cuando un cliente le escribe al bot en Telegram, el sistema recibe el mensaje, lo procesa y responde automáticamente.

El bot se conecta directamente a la misma base de datos del sistema, por lo que las citas que se registran a través del bot aparecen inmediatamente en la agenda de la aplicación de escritorio.

---

## Comandos disponibles

| Comando | Descripción |
|---|---|
| `/start` | Inicia la conversación con el bot y muestra las opciones disponibles |
| `/agendar` | Inicia el flujo para solicitar una nueva cita |
| `/micita` | Consulta el estado de la cita activa del cliente |
| `/cancelar` | Cancela la cita activa del cliente |
| `/reprogramar` | Cambia la fecha u hora de la cita activa |

Si el cliente escribe cualquier mensaje fuera de un flujo activo, el bot responde con una guía de los comandos disponibles.

---

## Flujo para agendar una cita

1. El cliente escribe `/agendar` o presiona el botón correspondiente
2. El bot pregunta el nombre del cliente
3. El bot muestra los servicios disponibles con sus precios para que el cliente elija
4. El bot muestra los empleados (barberos) disponibles para el servicio elegido
5. El bot pide la fecha deseada (en formato DD/MM/AAAA)
6. El bot muestra los horarios disponibles para ese barbero en esa fecha
7. El cliente elige el horario
8. El bot confirma la cita y envía el código único de seguimiento

---

## Consultar el estado de una cita

Con el comando `/micita` el cliente puede ver en cualquier momento el estado de su cita más reciente: si está pendiente, confirmada, en curso o completada.

---

## Cancelar o reprogramar

Los comandos `/cancelar` y `/reprogramar` permiten al cliente hacer cambios en su cita sin necesidad de contactar a la recepcionista. El sistema actualiza el estado en tiempo real y el cambio se refleja inmediatamente en la agenda de la aplicación de escritorio.

---

## Configuración del bot

Para activar el bot, el administrador debe configurar el token de Telegram en el archivo de configuración del sistema. Este token se obtiene creando un bot a través de **@BotFather** en Telegram.

El bot se activa automáticamente cada vez que se abre el sistema de escritorio y se detiene cuando el sistema se cierra.

---

## Integración con la agenda

Las citas registradas por el bot llegan con estado "pendiente". La recepcionista las ve en la agenda con una indicación de que fueron creadas por Telegram y puede confirmarlas, reasignarlas o cancelarlas desde la aplicación de escritorio.
