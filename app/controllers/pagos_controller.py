
from datetime import date
from app.models.pago_model import PagoModel
from app.models.cita_model import CitaModel
from app.models.factura_model import FacturaModel
from app.views.screens.pagos_view import PagosView


class PagosController:
    def __init__(self, view, usuario):
        self._modelo_pago    = PagoModel()
        self._modelo_cita    = CitaModel()
        self._modelo_factura = FacturaModel()
        self._view    = view
        self._usuario = usuario

        # Solo la recepcionista puede registrar pagos — el admin solo ve el historial
        if usuario.get("rol") != "administrador":
            self._view.btn_registrar.configure(command=self._registrar)

        # Cargo el historial de pagos del mes actual al abrir
        self._cargar_historial()

    def _registrar(self):
        """Registra el pago de una cita y calcula las ganancias automáticamente."""
        codigo    = self._view.entry_codigo.get().strip()
        monto_str = self._view.entry_monto.get().strip()
        metodo    = self._view.opt_metodo.get()

        # Verifico que los campos no estén vacíos
        if not codigo or not monto_str:
            return

        # Convierto el monto a número
        try:
            monto = float(monto_str)
        except ValueError:
            return

        # Busco la cita por su código para obtener el ID interno
        cita = self._modelo_cita.obtener_por_codigo(codigo)
        if not cita:
            # Si no existe, muestro el desglose en cero para indicar que falló
            self._view.mostrar_desglose(0, 0)
            return

        if self._modelo_pago.obtener_por_cita(cita["id"]):
            self._view.mostrar_desglose(0, 0)
            return

        # Marco la cita como completada
        self._modelo_cita.actualizar_estado(codigo, "completada")

        # Registro el pago — el modelo calcula automáticamente la distribución
        try:
            resultado = self._modelo_pago.registrar(
                cita_id=cita["id"],
                monto=monto,
                metodo=metodo,
                fecha=date.today().isoformat(),
            )
        except ValueError:
            self._view.mostrar_desglose(0, 0)
            return

        # Genero la factura automáticamente al registrar el pago (RF11)
        numero_factura = self._modelo_factura.generar(resultado["pago_id"])

        # Muestro el desglose de ganancias (barbero vs negocio) y el número de factura
        self._view.mostrar_desglose(
            resultado["empleado"], resultado["negocio"], numero_factura
        )

        # Limpio los campos del formulario
        self._view.entry_codigo.delete(0, "end")
        self._view.entry_monto.delete(0, "end")

        # Recargo el historial
        self._cargar_historial()

    def _cargar_historial(self):
        """Carga los pagos del mes actual desde el primer día hasta hoy."""
        hoy    = date.today()
        inicio = hoy.replace(day=1).isoformat()
        fin    = hoy.isoformat()
        pagos  = self._modelo_pago.listar_por_periodo(inicio, fin)
        self._view.mostrar_historial(pagos)
