
from app.models.empleado_model import EmpleadoModel
from app.views.screens.empleados_view import EmpleadosView


class EmpleadosController:
    def __init__(self, view, usuario):
        self._modelo = EmpleadoModel()
        self._view = view
        self._usuario = usuario

        # Verifico que el usuario es administrador antes de habilitar los botones
        if usuario.get("rol") == "administrador":
            # Si es admin, conecto los botones con sus métodos
            self._view.btn_crear.configure(command=self._crear)
            self._view.btn_editar.configure(command=self._editar)
            self._view.btn_eliminar.configure(command=self._desactivar)
        else:
            # Si no es admin, desactivo todos los botones de gestión
            for btn in [self._view.btn_crear, self._view.btn_editar, self._view.btn_eliminar]:
                btn.configure(state="disabled")

        # Cargo la lista de empleados al abrir la pantalla
        self._refrescar()

    def _crear(self):
        """Crea un nuevo empleado con los datos del formulario."""
        nombre      = self._view.entry_nombre.get().strip()
        telefono    = self._view.entry_telefono.get().strip()
        especialidad = self._view.entry_especialidad.get().strip()
        pct_texto   = self._view.entry_porcentaje.get().strip()

        # El nombre es obligatorio
        if not nombre:
            self._view.mostrar_resultado("El nombre del empleado es obligatorio.", error=True)
            return

        # Convierto el porcentaje a número; si falla o está vacío, uso 60% por defecto
        try:
            porcentaje = float(pct_texto) if pct_texto else 60.0
        except ValueError:
            porcentaje = 60.0

        # Creo el empleado en la BD
        self._modelo.crear(nombre, telefono, especialidad, porcentaje)
        self._view.mostrar_resultado(f"Empleado '{nombre}' creado exitosamente.")

        # Limpio los campos del formulario
        self._limpiar_campos()

        # Recargo la tabla de empleados
        self._refrescar()

    def _editar(self):
        """Edita un empleado usando el ID escrito en el formulario."""
        id_texto = self._view.entry_id.get().strip()
        nombre = self._view.entry_nombre.get().strip()
        telefono = self._view.entry_telefono.get().strip()
        especialidad = self._view.entry_especialidad.get().strip()
        pct_texto = self._view.entry_porcentaje.get().strip()

        if not id_texto:
            self._view.mostrar_resultado("Ingresa el ID del empleado.", error=True)
            return

        if not nombre:
            self._view.mostrar_resultado("Ingresa el nuevo nombre del empleado.", error=True)
            return

        try:
            empleado_id = int(id_texto)
            porcentaje = float(pct_texto) if pct_texto else 60.0
        except ValueError:
            self._view.mostrar_resultado("Revisa el ID y el porcentaje.", error=True)
            return

        self._modelo.actualizar(
            empleado_id, nombre, telefono, especialidad, porcentaje
        )
        self._view.mostrar_resultado(f"Empleado ID {empleado_id} actualizado.")
        self._limpiar_campos()
        self._refrescar()

    def _desactivar(self):
        """Desactiva un empleado usando su ID."""
        id_texto = self._view.entry_id.get().strip()

        if not id_texto:
            self._view.mostrar_resultado("Ingresa el ID del empleado.", error=True)
            return

        try:
            # Convierto el texto a entero y desactivo el empleado
            empleado_id = int(id_texto)
            self._modelo.desactivar(empleado_id)
            self._view.mostrar_resultado(f"Empleado ID {empleado_id} desactivado.")
            self._limpiar_campos()
            self._refrescar()
        except ValueError:
            self._view.mostrar_resultado("El ID debe ser un número.", error=True)

    def _refrescar(self):
        """Recarga la lista de empleados activos en la tabla."""
        empleados = self._modelo.listar()
        self._view.cargar_empleados(empleados)

    def _limpiar_campos(self):
        """Limpia los campos del formulario."""
        for entry in [
            self._view.entry_id,
            self._view.entry_nombre,
            self._view.entry_telefono,
            self._view.entry_especialidad,
            self._view.entry_porcentaje,
        ]:
            entry.delete(0, "end")
