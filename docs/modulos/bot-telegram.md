# Bot de Telegram

El bot fue una de las funcionalidades que más me gustó implementar. Permite que los clientes de la barbería puedan agendar, consultar, cancelar o reprogramar su cita directamente desde Telegram, sin tener que llamar ni ir personalmente.

El bot corre en segundo plano mientras el sistema está abierto y se conecta a la misma base de datos, así que todo lo que registra aparece inmediatamente en la agenda de escritorio.

---

## Comandos disponibles

| Comando | Qué hace |
|---|---|
| `/start` | Muestra el menú de opciones |
| `/agendar` | Inicia el proceso para pedir una cita |
| `/micita` | Consulta el estado de la cita activa |
| `/cancelar` | Cancela la cita activa |
| `/reprogramar` | Cambia la fecha u hora de la cita |

Si el cliente escribe cualquier cosa fuera de un flujo activo, el bot responde con una guía de los comandos disponibles para que no se quede sin saber qué hacer.

---

## Cómo funciona el flujo para agendar

1. El cliente escribe `/agendar`
2. El bot pide el nombre
3. Muestra los servicios disponibles con precios
4. Muestra los barberos disponibles para el servicio elegido
5. Pide la fecha deseada
6. Muestra los horarios disponibles para ese día
7. Confirma la cita y envía el código de seguimiento

---

## Consultar, cancelar o reprogramar

Con `/micita` el cliente puede ver el estado de su cita en cualquier momento. Con `/cancelar` y `/reprogramar` puede hacer cambios sin necesidad de hablar con nadie. El cambio se refleja inmediatamente en la agenda del sistema de escritorio.

---

## Configuración

Para activar el bot hay que configurar el token de Telegram en el sistema. Ese token se obtiene creando el bot con **@BotFather** en Telegram. El bot se activa solo cada vez que se abre el sistema y se apaga cuando el sistema se cierra.

---

## Cómo llegan las citas a la agenda

Las citas que llegan por Telegram aparecen con estado "pendiente" en la agenda de escritorio. La recepcionista las puede confirmar, reasignar o cancelar desde ahí igual que cualquier otra cita.
