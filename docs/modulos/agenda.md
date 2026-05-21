# Módulo de Agenda

La agenda es el corazón del sistema. Desde aquí se pueden ver y gestionar todas las citas del día en un formato de calendario por columnas, donde cada columna representa un empleado (barbero) y cada fila representa una franja horaria.

---

## Vista principal

La pantalla de agenda muestra:

- Un **selector de fecha** para navegar entre días
- Una **cuadrícula de citas** organizada por empleado y hora
- Cada cita aparece como una tarjeta con el nombre del cliente, el servicio y el estado actual
- Las citas tienen colores distintos según su estado:
  - 🟡 **Pendiente** — cita registrada pero sin confirmar
  - 🔵 **Confirmada** — cita confirmada y lista para atender
  - 🟣 **En curso** — el servicio está siendo ejecutado en este momento
  - 🟢 **Completada** — el servicio ya terminó
  - 🔴 **Cancelada** — la cita fue cancelada

---

## Registrar una nueva cita

Para registrar una cita se usa el botón **"Nueva Cita"**. El formulario pide:

- Nombre del cliente (se puede buscar si ya existe en el sistema)
- Empleado que va a realizar el servicio
- Servicio a realizar
- Fecha y hora de la cita
- Observaciones adicionales (opcional)

El sistema valida automáticamente que el horario elegido esté disponible para el empleado seleccionado.

---

## Gestionar una cita existente

Al hacer clic sobre cualquier cita de la agenda se abre un panel de detalle con toda la información de esa cita y las acciones disponibles según su estado actual:

| Estado actual | Acciones disponibles |
|---|---|
| Pendiente | Confirmar, Reprogramar, Cancelar |
| Confirmada | Iniciar servicio, Reprogramar, Cancelar |
| En curso | Finalizar servicio |
| Completada | Solo visualización |
| Cancelada | Solo visualización |

### Reprogramar una cita
Al elegir reprogramar, el sistema muestra un selector de fecha y una cuadrícula de horarios disponibles para el empleado. El usuario selecciona el nuevo horario y confirma el cambio.

### Cancelar una cita
Antes de cancelar, el sistema pide confirmación para evitar cancelaciones accidentales.

---

## Búsqueda de citas

En la parte superior hay un campo de búsqueda que permite filtrar las citas por nombre del cliente o código de la cita.
