
from datetime import date
from app.models.gasto_model import GastoModel
from app.views.screens.gastos_view import GastosView


class GastosController:
    def __init__(self, view, usuario):
        self._modelo = GastoModel()
        self._view = view
        self._usuario = usuario

        # Conecto el botón de registrar con el método correspondiente
        self._view.btn_registrar.configure(command=self._registrar)

        # Cargo los gastos del mes actual al abrir la pantalla
        self._refrescar()

    def _registrar(self):
        """Registra un nuevo gasto con los datos del formulario."""
        descripcion = self._view.entry_descripcion.get().strip()
        monto_texto = self._view.entry_monto.get().strip()
        fecha       = self._view.entry_fecha.get().strip()
        categoria   = self._view.opt_categoria.get()

        # Si el campo de fecha está vacío, uso la fecha de hoy
        if not fecha:
            fecha = date.today().isoformat()

        # Valido que los campos obligatorios no estén vacíos
        if not descripcion or not monto_texto:
            return

        # Convierto el monto a número — si falla, salgo sin hacer nada
        try:
            monto = float(monto_texto)
        except ValueError:
            return

        # Guardo el gasto registrando también quién lo ingresó
        usuario_id = self._usuario.get("id")
        self._modelo.crear(descripcion, categoria, monto, fecha, usuario_id)

        # Limpio los campos del formulario y recargo la lista
        self._view.entry_descripcion.delete(0, "end")
        self._view.entry_monto.delete(0, "end")
        self._refrescar()

    def _refrescar(self):
        """Carga los gastos del mes actual desde el primer día hasta hoy."""
        hoy = date.today()
        inicio = hoy.replace(day=1).isoformat()
        fin = hoy.isoformat()
        gastos = self._modelo.listar_por_periodo(inicio, fin)
        self._view.cargar_gastos(gastos)
