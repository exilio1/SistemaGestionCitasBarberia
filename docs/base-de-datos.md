# Base de Datos

El sistema usa **SQLite** como motor de base de datos. Se eligió SQLite porque es una base de datos que no necesita un servidor separado, el archivo de datos queda guardado localmente junto con el sistema, y es más que suficiente para el volumen de datos de una barbería pequeña o mediana.

---

## Tablas del sistema

### usuarios
Almacena los usuarios que pueden iniciar sesión en el sistema.

| Campo | Tipo | Descripción |
|---|---|---|
| id | INTEGER | Identificador único |
| nombre | TEXT | Nombre completo del usuario |
| correo | TEXT | Correo electrónico (único, se usa para login) |
| contrasena_hash | TEXT | Contraseña cifrada con bcrypt |
| rol | TEXT | `administrador` o `recepcionista` |
| telefono | TEXT | Teléfono de contacto |
| activo | INTEGER | 1 = activo, 0 = desactivado |
| fecha_creacion | TEXT | Fecha de registro |

---

### empleados
Registra los barberos y empleados del negocio.

| Campo | Tipo | Descripción |
|---|---|---|
| id | INTEGER | Identificador único |
| nombre | TEXT | Nombre del empleado |
| telefono | TEXT | Teléfono de contacto |
| especialidad | TEXT | Especialidad principal (por defecto: Corte de cabello) |
| porcentaje_ganancia | REAL | Porcentaje del pago que le corresponde al barbero |
| activo | INTEGER | 1 = activo, 0 = desactivado |
| fecha_creacion | TEXT | Fecha de registro |

---

### clientes
Guarda la información de los clientes de la barbería.

| Campo | Tipo | Descripción |
|---|---|---|
| id | INTEGER | Identificador único |
| nombre | TEXT | Nombre del cliente |
| cedula | TEXT | Número de identificación (único) |
| telefono | TEXT | Teléfono de contacto |
| correo | TEXT | Correo electrónico |
| fecha_creacion | TEXT | Fecha de registro |

---

### servicios
Catálogo de servicios que ofrece la barbería.

| Campo | Tipo | Descripción |
|---|---|---|
| id | INTEGER | Identificador único |
| nombre | TEXT | Nombre del servicio |
| descripcion | TEXT | Descripción del servicio |
| precio | REAL | Precio del servicio |
| duracion_minutos | INTEGER | Duración estimada en minutos |
| activo | INTEGER | 1 = disponible, 0 = desactivado |

---

### citas
Registro de todas las citas del negocio.

| Campo | Tipo | Descripción |
|---|---|---|
| id | INTEGER | Identificador único |
| cliente_id | INTEGER | Referencia al cliente |
| empleado_id | INTEGER | Referencia al empleado (barbero) |
| servicio_id | INTEGER | Referencia al servicio |
| fecha | TEXT | Fecha de la cita (YYYY-MM-DD) |
| hora | TEXT | Hora de la cita (HH:MM) |
| estado | TEXT | `pendiente`, `confirmada`, `en_curso`, `completada`, `cancelada` |
| observaciones | TEXT | Notas adicionales |
| codigo | TEXT | Código único de la cita |
| fecha_creacion | TEXT | Fecha de registro |

---

### pagos
Registro de los pagos realizados por cada cita.

| Campo | Tipo | Descripción |
|---|---|---|
| id | INTEGER | Identificador único |
| cita_id | INTEGER | Referencia a la cita pagada |
| monto | REAL | Monto total pagado |
| metodo | TEXT | Método de pago (efectivo, tarjeta, etc.) |
| fecha | TEXT | Fecha del pago |
| estado | TEXT | Estado del pago |
| ganancia_empleado | REAL | Monto que le corresponde al barbero |
| ganancia_negocio | REAL | Monto que queda para el negocio |

---

### facturas
Facturas generadas a partir de pagos registrados.

| Campo | Tipo | Descripción |
|---|---|---|
| id | INTEGER | Identificador único |
| pago_id | INTEGER | Referencia al pago |
| numero_factura | TEXT | Número único de factura |
| fecha_emision | TEXT | Fecha de emisión |
| detalle | TEXT | Detalle adicional de la factura |

---

### gastos
Control de gastos del negocio.

| Campo | Tipo | Descripción |
|---|---|---|
| id | INTEGER | Identificador único |
| usuario_id | INTEGER | Usuario que registró el gasto |
| descripcion | TEXT | Descripción del gasto |
| categoria | TEXT | Categoría del gasto |
| monto | REAL | Monto del gasto |
| fecha_gasto | TEXT | Fecha en que ocurrió el gasto |

---

## Diagrama de relaciones

```
clientes ──────┐
               ▼
empleados ─► citas ──► pagos ──► facturas
               ▲
servicios ─────┘

usuarios ──► gastos
```

---

## Respaldo automático

Cada vez que se inicia el sistema se genera un respaldo de la base de datos en la carpeta `data/backups/`. Los archivos de respaldo tienen la fecha y hora en el nombre para poder identificarlos fácilmente. Los respaldos más viejos de 7 días se eliminan automáticamente para no ocupar demasiado espacio.
