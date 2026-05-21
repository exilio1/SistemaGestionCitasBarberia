# Base de Datos

Usé **SQLite** como base de datos. La razón principal fue que es una base de datos que no necesita un servidor aparte, el archivo queda guardado localmente junto con el programa y es suficiente para el volumen de datos que maneja una barbería.

Al principio consideré usar MySQL pero me pareció innecesario para este tipo de sistema porque el negocio no necesita conexiones concurrentes desde varios equipos al mismo tiempo.

---

## Tablas

### usuarios
Los que pueden iniciar sesión en el sistema.

| Campo | Tipo | Descripción |
|---|---|---|
| id | INTEGER | Llave primaria |
| nombre | TEXT | Nombre completo |
| correo | TEXT | Correo para el login (único) |
| contrasena_hash | TEXT | Contraseña cifrada con bcrypt |
| rol | TEXT | `administrador` o `recepcionista` |
| telefono | TEXT | Contacto |
| activo | INTEGER | 1 activo / 0 desactivado |

---

### empleados
Los barberos del negocio.

| Campo | Tipo | Descripción |
|---|---|---|
| id | INTEGER | Llave primaria |
| nombre | TEXT | Nombre del barbero |
| telefono | TEXT | Contacto |
| especialidad | TEXT | Tipo de servicio principal |
| porcentaje_ganancia | REAL | % del servicio que le corresponde |
| activo | INTEGER | 1 activo / 0 desactivado |

---

### clientes
Personas que vienen a la barbería.

| Campo | Tipo | Descripción |
|---|---|---|
| id | INTEGER | Llave primaria |
| nombre | TEXT | Nombre del cliente |
| cedula | TEXT | Identificación (única) |
| telefono | TEXT | Contacto |
| correo | TEXT | Correo electrónico |

---

### servicios
Los servicios que ofrece la barbería.

| Campo | Tipo | Descripción |
|---|---|---|
| id | INTEGER | Llave primaria |
| nombre | TEXT | Nombre del servicio |
| descripcion | TEXT | Qué incluye |
| precio | REAL | Precio en pesos |
| duracion_minutos | INTEGER | Tiempo estimado |
| activo | INTEGER | Disponible o no |

---

### citas
El registro de todas las citas.

| Campo | Tipo | Descripción |
|---|---|---|
| id | INTEGER | Llave primaria |
| cliente_id | INTEGER | Referencia al cliente |
| empleado_id | INTEGER | Referencia al barbero |
| servicio_id | INTEGER | Referencia al servicio |
| fecha | TEXT | Fecha de la cita |
| hora | TEXT | Hora de la cita |
| estado | TEXT | pendiente / confirmada / en_curso / completada / cancelada |
| codigo | TEXT | Código único de seguimiento |

---

### pagos
Los pagos registrados por cada cita.

| Campo | Tipo | Descripción |
|---|---|---|
| id | INTEGER | Llave primaria |
| cita_id | INTEGER | Referencia a la cita |
| monto | REAL | Total pagado |
| metodo | TEXT | Forma de pago |
| ganancia_empleado | REAL | Lo que le toca al barbero |
| ganancia_negocio | REAL | Lo que queda para la barbería |

---

### facturas / gastos

**facturas:** se genera una por cada pago registrado, con número consecutivo.

**gastos:** registro de todos los egresos del negocio por categoría.

---

## Relaciones entre tablas

```
clientes ──┐
           ▼
empleados → citas → pagos → facturas
           ▲
servicios ─┘

usuarios → gastos
```

---

## Respaldos

Cada vez que arranca el sistema se crea un respaldo de la base de datos en `data/backups/` con la fecha en el nombre. Los respaldos de más de 7 días se eliminan solos para no ocupar mucho espacio.
