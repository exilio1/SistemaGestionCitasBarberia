
from datetime import date
from app.models.cita_model import CitaModel
from app.models.cliente_model import ClienteModel
from app.models.servicio_model import ServicioModel
from app.views.screens.cliente_solicitar_view import ClienteSolicitarView


class ClienteController:
    def __init__(self, view, usuario):
        self._modelo_cita = CitaModel()
        self._modelo_cliente = ClienteModel()
        self._modelo_servicio = ServicioModel()
        self._view = view
        self._usuario = usuario

        # Conecto el botón de solicitar con el método correspondiente
        self._view.btn_solicitar.configure(command=self._solicitar_cita)
        self._cargar_servicios()

        # Cargo las citas del cliente al abrir la pantalla
        self._refrescar()

    def _cargar_servicios(self):
        """Carga el catálogo de servicios activos en la vista."""
        servicios = self._modelo_servicio.listar(solo_activos=True)
        self._view.cargar_servicios(servicios)

    def _solicitar_cita(self):
        """Crea una nueva cita para el cliente que está en sesión."""
        servicio_id  = self._view.get_servicio_id()
        fecha        = self._view.entry_fecha.get().strip()
        hora         = self._view.entry_hora.get().strip()

        # Valido que se llenaron los campos obligatorios
        if not fecha or not hora:
            self._view.mostrar_resultado(
                "Debes ingresar la fecha y la hora.", error=True)
            return

        if not servicio_id:
            self._view.mostrar_resultado(
                "Debes seleccionar un servicio válido.", error=True)
            return

        # Obtengo los datos del usuario en sesión para buscar su registro de cliente
        telefono = self._usuario.get("telefono", "")
        correo   = self._usuario.get("correo", "")
        nombre   = self._usuario.get("nombre", "")

        # Busco el registro del cliente primero por teléfono, luego por correo
        cliente = None
        if telefono:
            cliente = self._modelo_cliente.obtener_por_telefono(telefono)
        if not cliente and correo:
            cliente = self._modelo_cliente.obtener_por_correo(correo)

        # Si el cliente no existe en la tabla de clientes, lo creo
        if not cliente:
            if not telefono:
                self._view.mostrar_resultado(
                    "Error: tu perfil no tiene teléfono registrado.", error=True)
                return
            cliente_id = self._modelo_cliente.obtener_o_crear(nombre, "", telefono)
        else:
            cliente_id = cliente["id"]

        # Uso el primer empleado disponible (ID 1)
        empleado_id = 1

        # Verifico que la hora esté disponible antes de crear la cita
        horas_libres = self._modelo_cita.horarios_disponibles(fecha, empleado_id)
        if hora not in horas_libres:
            sugerencias = horas_libres[:4] if horas_libres else []
            self._view.mostrar_resultado(
                f"Hora no disponible. Horas libres: {sugerencias}", error=True)
            return

        # Creo la cita en estado pendiente
        codigo = self._modelo_cita.crear(cliente_id, empleado_id, servicio_id, fecha, hora)
        self._view.mostrar_resultado(
            f"Cita solicitada con éxito. Código: {codigo}\n"
            "Espera la confirmación del administrador.")

        # Limpio los campos y recargo la lista de citas
        self._view.entry_fecha.delete(0, "end")
        self._view.entry_hora.delete(0, "end")
        self._refrescar()

    def _refrescar(self):
        """Recarga las citas del cliente actual filtrando por su ID."""
        telefono = self._usuario.get("telefono", "")
        correo   = self._usuario.get("correo", "")

        # Busco el registro del cliente igual que en _solicitar_cita
        cliente = None
        if telefono:
            cliente = self._modelo_cliente.obtener_por_telefono(telefono)
        if not cliente and correo:
            cliente = self._modelo_cliente.obtener_por_correo(correo)

        if not cliente:
            # Si el cliente no tiene registro, muestro la lista vacía
            self._view.cargar_citas([])
            return

        # Obtengo todas las citas y filtro solo las de este cliente
        todas = self._modelo_cita.listar_por_rango("2020-01-01", "2099-12-31")
        mis_citas = [c for c in todas if c.get("cliente_id") == cliente["id"]]
        self._view.cargar_citas(mis_citas)
