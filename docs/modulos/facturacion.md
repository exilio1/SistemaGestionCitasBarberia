# Módulo de Facturación

El módulo de facturación permite registrar los pagos de las citas completadas y generar facturas en formato PDF. También muestra una sección con los servicios que ya fueron finalizados pero que todavía no tienen pago registrado.

---

## Servicios pendientes de cobro

En la parte superior del módulo aparece una lista de citas que ya están en estado "completada" pero que aún no tienen un pago registrado. Esto es muy útil para que la recepcionista no tenga que ir a la agenda a buscar cuáles citas cobrar.

Cada fila de la lista muestra:
- Código de la cita
- Nombre del cliente
- Servicio realizado
- Precio del servicio
- Botón **"Cobrar"** que llena automáticamente el formulario de pago

---

## Registrar un pago

El formulario de registro de pago tiene los siguientes campos:

- **Código de la cita:** se puede escribir manualmente o usar el botón "Cobrar" de la lista de pendientes
- **Monto:** precio del servicio (se llena automáticamente al cargar la cita)
- **Método de pago:** efectivo, tarjeta débito, tarjeta crédito, transferencia u otro
- **Observaciones:** notas adicionales opcionales

Al registrar el pago, el sistema calcula automáticamente:
- La ganancia del empleado según el porcentaje configurado
- La ganancia del negocio (lo que queda después del pago al barbero)

---

## Generar factura

Después de registrar un pago, el sistema ofrece la opción de generar una factura en PDF. La factura incluye:

- Número de factura consecutivo
- Datos de la barbería
- Datos del cliente
- Detalle del servicio realizado
- Monto total y método de pago
- Fecha de emisión

El archivo PDF se guarda automáticamente y se puede imprimir o compartir directamente.

---

## Indicadores del módulo

En la parte superior se muestran tres indicadores rápidos:
- Total recaudado en el día
- Total recaudado en el mes
- Número de facturas generadas en el período
