# Módulo de Servicios

El módulo de servicios permite administrar el catálogo de servicios que ofrece la barbería. Desde aquí el administrador puede agregar nuevos servicios, actualizar precios o desactivar servicios que ya no se ofrecen.

---

## Lista de servicios

La pantalla muestra todos los servicios disponibles en una tabla con las siguientes columnas:

- **Nombre:** nombre del servicio (ej. Corte de cabello, Arreglo de barba, Coloración)
- **Descripción:** detalle de lo que incluye el servicio
- **Precio:** valor en pesos del servicio
- **Duración:** tiempo estimado en minutos
- **Estado:** activo o inactivo

---

## Agregar un servicio

El formulario para crear un nuevo servicio pide:

- **Nombre del servicio:** nombre claro y descriptivo
- **Descripción:** qué incluye el servicio, qué materiales se usan, etc.
- **Precio:** valor en pesos colombianos
- **Duración estimada:** cuántos minutos toma realizar el servicio. Este dato se usa en la agenda para calcular si hay disponibilidad de horario.

---

## Editar un servicio

Cualquier servicio puede editarse en cualquier momento. Si se cambia el precio de un servicio, ese cambio aplica solo para las citas nuevas. Las citas anteriores mantienen el precio que tenían cuando se registraron.

---

## Desactivar un servicio

Si la barbería deja de ofrecer algún servicio se puede desactivar. Los servicios inactivos no aparecen disponibles en el formulario de nueva cita, pero el historial de citas anteriores que usaron ese servicio se conserva intacto.

---

## Relación con los módulos de agenda y facturación

Los servicios están conectados directamente con el módulo de agenda (al registrar una cita se elige el servicio) y con el módulo de facturación (el precio del servicio se usa para calcular el pago y las ganancias del barbero y del negocio).
