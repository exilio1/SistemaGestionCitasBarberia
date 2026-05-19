from app.models.servicio_model import ServicioModel
from app.views.screens.servicios_view import ServiciosView


class ServiciosController:
    def __init__(self, view, usuario):
        self._modelo  = ServicioModel()
        self._view    = view
        self._usuario = usuario

        # Solo el administrador puede modificar los servicios
        if usuario.get("rol") == "administrador":
            self._view.btn_crear.configure(command=self._crear)
            self._view.btn_editar.configure(command=self._editar)
            self._view.btn_desactivar.configure(command=self._desactivar)
            self._view.btn_activar.configure(command=self._activar)
        else:
            for btn in [
                self._view.btn_crear,
                self._view.btn_editar,
                self._view.btn_desactivar,
                self._view.btn_activar,
            ]:
                btn.configure(state="disabled")

        # Cargo el catalogo de servicios al abrir la pantalla
        self._refrescar()

    def _crear(self):
        """Crea un nuevo servicio con los datos del formulario."""
        nombre      = self._view.entry_nombre.get().strip()
        precio_txt  = self._view.entry_precio.get().strip()
        dur_txt     = self._view.entry_duracion.get().strip()
        descripcion = self._view.entry_descripcion.get().strip()

        if not nombre:
            self._view.mostrar_resultado("El nombre del servicio es obligatorio.", error=True)
            return

        if not precio_txt:
            self._view.mostrar_resultado("El precio es obligatorio.", error=True)
            return

        try:
            precio = float(precio_txt)
        except ValueError:
            self._view.mostrar_resultado("El precio debe ser un numero. Ej: 25000", error=True)
            return

        try:
            duracion = int(dur_txt) if dur_txt else 30
        except ValueError:
            self._view.mostrar_resultado("La duracion debe ser en minutos. Ej: 30", error=True)
            return

        # Verifico que no exista un servicio con el mismo nombre
        existente = self._modelo.obtener_por_nombre(nombre)
        if existente:
            self._view.mostrar_resultado(
                f"Ya existe un servicio llamado '{nombre}'. Usa Editar si quieres cambiarlo.",
                error=True
            )
            return

        self._modelo.crear(nombre, precio, descripcion, duracion)
        self._view.mostrar_resultado(f"Servicio '{nombre}' agregado exitosamente.")
        self._limpiar_campos()
        self._refrescar()

    def _editar(self):
        """Edita un servicio existente usando el ID del formulario."""
        id_txt      = self._view.entry_id.get().strip()
        nombre      = self._view.entry_nombre.get().strip()
        precio_txt  = self._view.entry_precio.get().strip()
        dur_txt     = self._view.entry_duracion.get().strip()
        descripcion = self._view.entry_descripcion.get().strip()

        if not id_txt:
            self._view.mostrar_resultado("Ingresa el ID del servicio a editar.", error=True)
            return

        if not nombre:
            self._view.mostrar_resultado("El nombre del servicio es obligatorio.", error=True)
            return

        if not precio_txt:
            self._view.mostrar_resultado("El precio es obligatorio.", error=True)
            return

        try:
            servicio_id = int(id_txt)
            precio      = float(precio_txt)
            duracion    = int(dur_txt) if dur_txt else 30
        except ValueError:
            self._view.mostrar_resultado("Revisa que el ID, precio y duracion sean numeros.", error=True)
            return

        self._modelo.actualizar(servicio_id, nombre, precio, descripcion, duracion)
        self._view.mostrar_resultado(f"Servicio ID {servicio_id} actualizado correctamente.")
        self._limpiar_campos()
        self._refrescar()

    def _desactivar(self):
        """Desactiva un servicio — deja de aparecer en el catalogo y en el bot."""
        id_txt = self._view.entry_id.get().strip()

        if not id_txt:
            self._view.mostrar_resultado("Ingresa el ID del servicio a desactivar.", error=True)
            return

        try:
            servicio_id = int(id_txt)
        except ValueError:
            self._view.mostrar_resultado("El ID debe ser un numero.", error=True)
            return

        self._modelo.desactivar(servicio_id)
        self._view.mostrar_resultado(f"Servicio ID {servicio_id} desactivado.")
        self._limpiar_campos()
        self._refrescar()

    def _activar(self):
        """Vuelve a activar un servicio que estaba desactivado."""
        id_txt = self._view.entry_id.get().strip()

        if not id_txt:
            self._view.mostrar_resultado("Ingresa el ID del servicio a activar.", error=True)
            return

        try:
            servicio_id = int(id_txt)
        except ValueError:
            self._view.mostrar_resultado("El ID debe ser un numero.", error=True)
            return

        self._modelo.activar(servicio_id)
        self._view.mostrar_resultado(f"Servicio ID {servicio_id} activado correctamente.")
        self._limpiar_campos()
        self._refrescar()

    def _refrescar(self):
        """Recarga el catalogo completo (activos e inactivos) en la tabla."""
        servicios = self._modelo.listar(solo_activos=False)
        self._view.cargar_servicios(servicios)

    def _limpiar_campos(self):
        """Limpia todos los campos del formulario."""
        for entry in [
            self._view.entry_id,
            self._view.entry_nombre,
            self._view.entry_precio,
            self._view.entry_duracion,
            self._view.entry_descripcion,
        ]:
            entry.delete(0, "end")
