
from app.models.factura_model import FacturaModel
from app.views.screens.factura_view import FacturaView


class FacturaController:
    def __init__(self, view, usuario):
        self._modelo = FacturaModel()
        self._view = view
        self._usuario = usuario

        # Conecto el botón de generar con el método correspondiente
        self._view.btn_generar.configure(command=self._generar)

        # Cargo las facturas existentes al abrir la pantalla
        self._refrescar()

    def _generar(self):
        """Genera una nueva factura para un pago existente."""
        pago_id_texto = self._view.entry_pago_id.get().strip()
        detalle = self._view.entry_detalle.get().strip()

        # Verifico que se ingresó el ID del pago
        if not pago_id_texto:
            self._view.mostrar_resultado("Debes ingresar el ID del pago.", error=True)
            return

        # El ID debe ser un número entero
        try:
            pago_id = int(pago_id_texto)
        except ValueError:
            self._view.mostrar_resultado("El ID del pago debe ser un número.", error=True)
            return

        # Intento generar la factura con el modelo
        numero = self._modelo.generar(pago_id, detalle)

        if numero:
            # Factura generada con éxito — limpio los campos y recargo la tabla
            self._view.mostrar_resultado(f"Factura generada: {numero}")
            self._view.entry_pago_id.delete(0, "end")
            self._view.entry_detalle.delete(0, "end")
            self._refrescar()
        else:
            # El modelo retorna None cuando ya existe una factura para ese pago
            self._view.mostrar_resultado(
                "No se pudo generar. El pago no existe o ya tiene factura.", error=True)

    def _refrescar(self):
        """Recarga la lista de facturas generadas."""
        facturas = self._modelo.listar()
        self._view.cargar_facturas(facturas)
