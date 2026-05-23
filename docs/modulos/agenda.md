# Agenda

La agenda fue el módulo que más tiempo me tomó desarrollar. Quería que se viera como un calendario real, con columnas por barbero y franjas horarias, no una simple lista de citas.

---

## Vista principal

La pantalla muestra una cuadrícula donde cada columna es un barbero y cada fila es una hora del día. Las citas aparecen como tarjetas dentro de esa cuadrícula con el nombre del cliente, el servicio y el estado actual.

Los colores de las tarjetas cambian según el estado:
- Pendiente
- Confirmada
- En curso
- Completada
- Cancelada

También hay un selector de fecha para navegar entre días y un campo de búsqueda para encontrar citas por nombre del cliente o código.

---

## Registrar una cita nueva

El botón **"Nueva Cita"** abre un formulario donde se elige el cliente, el barbero, el servicio y el horario. El sistema valida que ese horario esté disponible para el barbero seleccionado antes de guardar.

Si el cliente ya existe en la base de datos se puede buscar por nombre. Si es nuevo se puede registrar desde el mismo formulario.

---

## Gestionar una cita

Al hacer clic en cualquier cita se abre un panel con todos los detalles y las acciones disponibles según el estado:

| Estado | Acciones |
|---|---|
| Pendiente | Confirmar, Reprogramar, Cancelar |
| Confirmada | Iniciar servicio, Reprogramar, Cancelar |
| En curso | Finalizar servicio |
| Completada o Cancelada | Solo visualización |

### Reprogramar
Al reprogramar se muestra un calendario para elegir la nueva fecha y una cuadrícula de horarios disponibles para seleccionar la nueva hora. Decidí hacerlo con botones en lugar de campo de texto para evitar errores al escribir la hora.

### Cancelar
Antes de cancelar el sistema pide confirmación para evitar cancelaciones accidentales.
