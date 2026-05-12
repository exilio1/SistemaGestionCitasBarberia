
from datetime import date, datetime
from tkinter import messagebox
from app.models.empleado_model import EmpleadoModel
from app.models.pago_model import PagoModel
from app.models.gasto_model import GastoModel
from app.views.screens.equipo_view import EquipoView


class EquipoController:
    def __init__(self, view, usuario):
        # Instancio los tres modelos que necesita esta pantalla
        self._modelo_emp   = EmpleadoModel()
        self._modelo_pago  = PagoModel()
        self._modelo_gasto = GastoModel()
        self._view         = view
        self._usuario      = usuario

        # Conecto los botones con sus métodos
        self._view.btn_calcular.configure(command=self._calcular_pago)
        self._view.btn_gasto.configure(command=self._registrar_gasto)
        self._view.set_accion_estado(self._cambiar_estado_empleado)

        # Cargo los empleados al abrir la pantalla
        self._cargar_empleados()

        # Pongo el mes actual como período por defecto en el panel de pagos
        hoy   = date.today()
        desde = hoy.replace(day=1).isoformat()
        hasta = hoy.isoformat()
        self._view.entry_desde.insert(0, desde)
        self._view.entry_hasta.insert(0, hasta)

    # ── Cargar empleados ──────────────────────────────────────────────────────

    def _cargar_empleados(self):
        """Obtiene los empleados activos e inactivos y los muestra en la tabla."""
        empleados = self._modelo_emp.listar_todos()
        self._view.cargar_empleados(empleados)

    # ── Calcular pago a barbero ───────────────────────────────────────────────

    def _calcular_pago(self):
        """Consulta las ganancias por empleado en el período indicado en los campos."""
        desde = self._view.entry_desde.get().strip()
        hasta = self._view.entry_hasta.get().strip()

        # Valido que se hayan ingresado las fechas
        if not desde or not hasta:
            self._view.mostrar_pago_barbero([])
            return

        try:
            fecha_desde = datetime.strptime(desde, "%Y-%m-%d").date()
            fecha_hasta = datetime.strptime(hasta, "%Y-%m-%d").date()
        except ValueError:
            messagebox.showerror(
                "Fecha inválida",
                "Escribe las fechas con este formato: AAAA-MM-DD",
            )
            return

        if fecha_desde > fecha_hasta:
            messagebox.showerror(
                "Rango inválido",
                "La fecha desde no puede ser mayor que la fecha hasta.",
            )
            return

        # Consulto el modelo y mando los datos a la vista
        datos = self._modelo_pago.ganancias_por_empleado(
            fecha_desde.isoformat(), fecha_hasta.isoformat()
        )
        self._view.actualizar_periodo_pago(
            fecha_desde.isoformat(), fecha_hasta.isoformat()
        )
        self._view.mostrar_pago_barbero(datos)

    def _cambiar_estado_empleado(self, empleado_id, activo_actual):
        """Activa o desactiva un empleado desde la tabla."""
        if activo_actual:
            self._modelo_emp.desactivar(empleado_id)
        else:
            self._modelo_emp.activar(empleado_id)
        self._cargar_empleados()

    # ── Registrar gasto rápido ────────────────────────────────────────────────

    def _registrar_gasto(self):
        """Registra un gasto rápido desde el panel de Equipo."""
        descripcion = self._view.entry_gasto_desc.get().strip()
        monto_txt   = self._view.entry_gasto_monto.get().strip()
        categoria   = self._view.opt_gasto_cat.get()

        # Valido que los campos no estén vacíos
        if not descripcion:
            self._view.mostrar_msg_gasto("Ingresa la descripción del gasto.", error=True)
            return
        if not monto_txt:
            self._view.mostrar_msg_gasto("Ingresa el monto.", error=True)
            return

        # Convierto el monto a número — valido que sea un valor válido
        try:
            monto = float(monto_txt)
        except ValueError:
            self._view.mostrar_msg_gasto("El monto debe ser un número.", error=True)
            return

        # Guardo el gasto con la fecha de hoy y el ID del usuario que lo registra
        fecha_hoy  = date.today().isoformat()
        usuario_id = self._usuario.get("id")
        self._modelo_gasto.crear(descripcion, categoria, monto, fecha_hoy, usuario_id)

        # Muestro confirmación y limpio los campos
        self._view.mostrar_msg_gasto(
            f"Gasto registrado: {descripcion} — ${monto:,.0f}", error=False
        )
        self._view.entry_gasto_desc.delete(0, "end")
        self._view.entry_gasto_monto.delete(0, "end")
