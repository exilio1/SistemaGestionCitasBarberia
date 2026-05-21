# Módulo de Reportes

El módulo de reportes está disponible únicamente para el administrador. Permite consultar el desempeño del negocio en diferentes períodos de tiempo y exportar la información en PDF.

---

## Tipos de reporte

### Reporte de ingresos
Muestra el total de ingresos generados en el período seleccionado, desglosado por:
- Ingresos totales del negocio
- Ganancia del negocio (después de descontar los pagos a empleados)
- Total pagado a empleados

### Reporte por empleado
Permite ver el rendimiento individual de cada barbero:
- Número de citas atendidas
- Total facturado por ese barbero
- Ganancia que le corresponde al empleado
- Ganancia que generó para el negocio

### Reporte de servicios más solicitados
Lista los servicios ordenados por cantidad de veces que fueron solicitados en el período, lo que ayuda a identificar qué servicios son más populares.

### Reporte de gastos
Muestra el total de gastos registrados en el período, agrupados por categoría.

---

## Filtros disponibles

- **Por período:** se puede elegir una fecha de inicio y una fecha de fin
- **Por empleado:** filtrar los datos de un empleado específico
- **Por servicio:** ver estadísticas de un servicio particular

---

## Exportar reporte

Cada reporte se puede exportar a PDF con el botón "Exportar PDF". El archivo generado incluye:
- Encabezado con el nombre de la barbería
- Período consultado
- Tabla con todos los datos del reporte
- Totales y resumen al final

El PDF se guarda en la carpeta de documentos del sistema.

---

## ¿Por qué solo el administrador tiene acceso?

Los reportes contienen información financiera sensible del negocio como los ingresos, los márgenes de ganancia y los salarios de los empleados. Por eso se decidió restringir este módulo solo al administrador para que la información financiera no esté disponible para todos los usuarios del sistema.
