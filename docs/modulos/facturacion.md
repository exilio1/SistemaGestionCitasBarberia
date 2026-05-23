# Facturación

Desde este módulo se registran los pagos de las citas y se generan las facturas en PDF. También tiene una sección que muestra los servicios que ya terminaron pero que todavía no tienen pago registrado, lo cual me pareció importante incluir porque en la práctica la recepcionista no siempre sabe cuáles citas cobrar sin ir a revisar la agenda.

---

## Servicios sin cobrar

En la parte de arriba aparece una lista de citas completadas sin pago. Para cada una se muestra el código, el nombre del cliente, el servicio y el precio. El botón **"Cobrar"** llena automáticamente el formulario de pago con esos datos, así solo hay que elegir el método de pago y confirmar.

---

## Registrar un pago

El formulario tiene estos campos:

- **Código de la cita:** se puede escribir o usar el botón "Cobrar" de la lista de arriba
- **Monto:** se llena solo al cargar la cita
- **Método de pago:** efectivo, tarjeta débito, tarjeta crédito, transferencia u otro
- **Observaciones:** opcional

Al guardar el pago el sistema calcula automáticamente cuánto le corresponde al barbero y cuánto queda para el negocio, según el porcentaje configurado para ese empleado.

---

## Generar factura

Después de registrar el pago se puede generar la factura en PDF. El archivo incluye los datos del cliente, el servicio, el monto y la fecha. Los números de factura son consecutivos y se generan automáticamente.

---

## Indicadores del módulo

En la parte superior se muestran los totales del día y del mes para que la recepcionista tenga visibilidad de cuánto se ha recaudado sin tener que abrir el módulo de reportes.
