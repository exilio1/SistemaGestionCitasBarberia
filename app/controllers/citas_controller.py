
from datetime import date
from app.models.cita_model import CitaModel
from app.models.cliente_model import ClienteModel
from app.models.servicio_model import ServicioModel
from app.views.screens.citas_view import CitasView


class CitasController:
    def __init__(self, view, usuario):
        self._modelo_cita    = CitaModel()
        self._modelo_cliente = ClienteModel()
        self._modelo_servicio = ServicioModel()
        self._view    = view
        self._usuario = usuario

        # Conecto cada botón con su método correspondiente
        self._view.btn_agendar.configure(command=self._agendar)
        self._view.btn_confirmar.configure(command=self._confirmar)
        self._view.btn_iniciar.configure(command=self._iniciar_servicio)
        self._view.btn_finalizar.configure(command=self._finalizar_servicio)
        self._view.btn_reprogramar.configure(command=self._reprogramar)
        self._view.btn_cancelar.configure(command=self._cancelar)

        self._cargar_servicios()
        # Cargo las citas del día al abrir la pantalla
        self._refrescar()

    def _cargar_servicios(self):
        """Carga los servicios activos en la vista."""
        servicios = self._modelo_servicio.listar(solo_activos=True)
        self._view.cargar_servicios(servicios)

    # ── Agendar ───────────────────────────────────────────────────────────────

    def _agendar(self):
        """Crea una nueva cita en estado 'pendiente' con los datos del formulario."""
        cedula      = self._view.entry_cedula.get().strip()
        telefono    = self._view.entry_telefono.get().strip()
        nombre      = self._view.entry_nombre.get().strip()
        servicio_id = self._view.get_servicio_id()
        fecha       = self._view.entry_fecha.get().strip()
        hora        = self._view.entry_hora.get().strip()

        # La cédula es obligatoria — es el identificador único del cliente
        if not cedula:
            self._view.mostrar_resultado("Ingresa la cédula del cliente.", error=True)
            return

        # Verifico que todos los campos necesarios estén llenos
        if not all([nombre, fecha, hora]):
            self._view.mostrar_resultado("Completa todos los campos para agendar.", error=True)
            return

        if not servicio_id:
            self._view.mostrar_resultado("Selecciona un servicio válido.", error=True)
            return

        # Busco o creo el cliente usando la cédula como identificador principal
        cliente_id = self._modelo_cliente.obtener_o_crear(nombre, cedula, telefono)

        # Uso el empleado ID 1 por defecto (en la Agenda se usa la selección por tarjeta)
        empleado_id = 1

        # Verifico que la hora esté disponible antes de crear la cita
        horas_libres = self._modelo_cita.horarios_disponibles(fecha, empleado_id)
        if hora not in horas_libres:
            sugerencias = ", ".join(horas_libres[:3]) if horas_libres else "ninguna"
            self._view.mostrar_resultado(
                f"Hora no disponible. Opciones: {sugerencias}", error=True)
            return

        # Creo la cita con el servicio_id (FK al catálogo)
        codigo = self._modelo_cita.crear(cliente_id, empleado_id, servicio_id, fecha, hora)
        self._view.mostrar_resultado(f"Cita agendada. Código: {codigo}")
        self._limpiar()
        self._refrescar()

    # ── Confirmar ─────────────────────────────────────────────────────────────

    def _confirmar(self):
        """Cambia el estado de 'pendiente' a 'confirmada'.
        Disponible para recepcionista y administrador.
        """
        codigo = self._view.entry_codigo.get().strip().upper()

        if not codigo:
            self._view.mostrar_resultado("Ingresa el código de la cita a confirmar.", error=True)
            return

        if self._modelo_cita.confirmar(codigo):
            self._view.mostrar_resultado(f"Cita {codigo} confirmada correctamente.")
            self._refrescar()
        else:
            self._view.mostrar_resultado(
                "No se encontró la cita o ya no está en estado pendiente.", error=True)

    # ── Iniciar servicio ──────────────────────────────────────────────────────

    def _iniciar_servicio(self):
        """Cambia el estado de la cita a 'en_curso'.
        Se usa cuando el cliente llega y el barbero empieza a atenderlo.
        """
        codigo = self._view.entry_codigo.get().strip().upper()

        if not codigo:
            self._view.mostrar_resultado("Ingresa el código de la cita para iniciar el servicio.", error=True)
            return

        # Verifico que la cita exista y esté en un estado que permita iniciar
        cita = self._modelo_cita.obtener_por_codigo(codigo)
        if not cita:
            self._view.mostrar_resultado(f"No se encontró la cita '{codigo}'.", error=True)
            return

        # Solo se puede iniciar si está pendiente o confirmada
        if cita.get("estado") not in ("pendiente", "confirmada"):
            self._view.mostrar_resultado(
                f"La cita debe estar pendiente o confirmada para iniciar. "
                f"Estado actual: {cita.get('estado')}.", error=True)
            return

        # Cambio el estado a 'en_curso'
        self._modelo_cita.actualizar_estado(codigo, "en_curso")
        self._view.mostrar_resultado(f"Servicio iniciado para cita {codigo}.")
        self._refrescar()

    # ── Finalizar servicio ────────────────────────────────────────────────────

    def _finalizar_servicio(self):
        """Cambia el estado de la cita a 'completada'.
        Se usa cuando termina el servicio, antes de registrar el pago.
        """
        codigo = self._view.entry_codigo.get().strip().upper()

        if not codigo:
            self._view.mostrar_resultado("Ingresa el código de la cita para finalizar.", error=True)
            return

        # Verifico que la cita esté en curso antes de finalizarla
        cita = self._modelo_cita.obtener_por_codigo(codigo)
        if not cita:
            self._view.mostrar_resultado(f"No se encontró la cita '{codigo}'.", error=True)
            return

        if cita.get("estado") != "en_curso":
            self._view.mostrar_resultado(
                f"La cita debe estar en curso para finalizar. "
                f"Estado actual: {cita.get('estado')}.", error=True)
            return

        pago = getattr(self, "_modelo_pago", None)
        if pago is None:
            from app.models.pago_model import PagoModel
            self._modelo_pago = PagoModel()

        pago_registrado = self._modelo_pago.obtener_por_cita(cita["id"])
        if not pago_registrado:
            self._view.mostrar_resultado(
                "Para finalizar el servicio primero debes registrar el pago en Facturación.",
                error=True,
            )
            return

        # Cambio el estado a 'completada' solo cuando ya existe el pago
        self._modelo_cita.actualizar_estado(codigo, "completada")
        self._view.mostrar_resultado(
            f"Servicio finalizado para cita {codigo}.")
        self._refrescar()

    # ── Reprogramar ───────────────────────────────────────────────────────────

    def _reprogramar(self):
        """Cambia la fecha y hora de una cita pendiente o confirmada."""
        codigo      = self._view.entry_codigo.get().strip().upper()
        nueva_fecha = self._view.entry_fecha.get().strip()
        nueva_hora  = self._view.entry_hora.get().strip()

        if not codigo or not nueva_fecha or not nueva_hora:
            self._view.mostrar_resultado(
                "Ingresa el código, la nueva fecha y la nueva hora.", error=True)
            return

        cita = self._modelo_cita.obtener_por_codigo(codigo)
        if not cita:
            self._view.mostrar_resultado("No se encontró la cita.", error=True)
            return

        horas_libres = self._modelo_cita.horarios_disponibles(
            nueva_fecha, cita.get("empleado_id")
        )
        if nueva_hora not in horas_libres:
            sugerencias = ", ".join(horas_libres[:3]) if horas_libres else "ninguna"
            self._view.mostrar_resultado(
                f"Esa hora no está libre. Opciones: {sugerencias}", error=True
            )
            return

        if self._modelo_cita.reprogramar(codigo, nueva_fecha, nueva_hora):
            self._view.mostrar_resultado(f"Cita {codigo} reprogramada a {nueva_fecha} {nueva_hora}.")
            self._refrescar()
        else:
            self._view.mostrar_resultado(
                "No se pudo reprogramar. Verifica el código y el estado.", error=True)

    # ── Cancelar ──────────────────────────────────────────────────────────────

    def _cancelar(self):
        """Cancela una cita. No se puede cancelar si ya está completada."""
        codigo = self._view.entry_codigo.get().strip().upper()

        if not codigo:
            self._view.mostrar_resultado("Ingresa el código de la cita a cancelar.", error=True)
            return

        if self._modelo_cita.cancelar(codigo):
            self._view.mostrar_resultado(f"Cita {codigo} cancelada.")
            self._refrescar()
        else:
            self._view.mostrar_resultado(
                "No se pudo cancelar. La cita no existe o ya fue completada.", error=True)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _refrescar(self):
        """Recarga la lista de citas del día actual en la tabla de la vista."""
        hoy   = date.today().isoformat()
        citas = self._modelo_cita.listar_por_rango(hoy, hoy)
        self._view.cargar_citas(citas)

    def _limpiar(self):
        """Limpia todos los campos del formulario después de agendar."""
        for entry in [
            self._view.entry_codigo,
            self._view.entry_cedula,
            self._view.entry_telefono,
            self._view.entry_nombre,
            self._view.entry_fecha,
            self._view.entry_hora,
        ]:
            entry.delete(0, "end")
        # El OptionMenu de servicio vuelve al primer elemento (no se limpia como Entry)
