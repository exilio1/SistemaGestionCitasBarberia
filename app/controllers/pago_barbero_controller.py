
from datetime import date
from app.models.pago_model import PagoModel
from app.views.screens.pago_barbero_view import PagoBarberoView


class PagoBarberoController:
    def __init__(self, view, usuario):
        self._modelo = PagoModel()
        self._view = view
        self._usuario = usuario

        # Conecto el botón de consultar con el método correspondiente
        self._view.btn_consultar.configure(command=self._consultar)

        # Cargo el mes actual por defecto al abrir la pantalla
        self._cargar_mes_actual()

    def _cargar_mes_actual(self):
        """Carga las ganancias del mes actual al abrir la pantalla."""
        hoy = date.today()
        inicio = hoy.replace(day=1).isoformat()
        fin = hoy.isoformat()

        # Pongo las fechas en los campos de filtro
        self._view.entry_desde.insert(0, inicio)
        self._view.entry_hasta.insert(0, fin)

        # Cargo los datos inmediatamente
        self._consultar_con_fechas(inicio, fin)

    def _consultar(self):
        """Lee las fechas del formulario y consulta las ganancias del período."""
        desde = self._view.entry_desde.get().strip()
        hasta = self._view.entry_hasta.get().strip()

        # Valido que se hayan ingresado las fechas
        if not desde or not hasta:
            self._view.mostrar_resumen("Debes ingresar el período de consulta.")
            return

        self._consultar_con_fechas(desde, hasta)

    def _consultar_con_fechas(self, desde, hasta):
        """Consulta las ganancias de cada empleado en el período dado."""
        # Obtengo los datos del modelo — un dict por empleado
        datos = self._modelo.ganancias_por_empleado(desde, hasta)

        # Calculo el total que se debe pagar a todos los empleados sumando sus ganancias
        total_pagar = sum(
            (empleado.get("total_empleado") or 0) for empleado in datos
        )

        # Muestro el resumen en la parte superior de la pantalla
        resumen = f"Período: {desde} al {hasta}  |  Total a pagar a barberos: ${total_pagar:,.0f}"
        self._view.mostrar_resumen(resumen)

        # Cargo la tabla con el detalle por empleado
        self._view.cargar_ganancias(datos)
