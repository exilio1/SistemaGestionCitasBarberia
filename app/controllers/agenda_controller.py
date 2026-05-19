
from datetime import date, datetime
from tkinter import messagebox
from app.models.cita_model import CitaModel
from app.models.empleado_model import EmpleadoModel
from app.views.screens.agenda_view import AgendaView


class AgendaController:
    def __init__(self, view, usuario):
        # Instancio los modelos que necesito para cargar la agenda
        self._modelo_cita = CitaModel()
        self._modelo_emp  = EmpleadoModel()
        self._view        = view
        self._usuario     = usuario

        # Conecto los botones de la vista con los métodos de este controlador
        self._view.btn_buscar.configure(command=self._buscar)
        self._view.btn_nueva_cita.configure(command=self._abrir_modal)

        # Conecto los callbacks del popup de detalle de cita para que
        # la recepcionista pueda confirmar o iniciar desde la agenda
        self._view._on_confirmar = self._confirmar_desde_agenda
        self._view._on_iniciar   = self._iniciar_desde_agenda

        # Cargo el día actual automáticamente al abrir la pantalla
        self._buscar()

    # ── Buscar citas por fecha ────────────────────────────────────────────────

    def _buscar(self):
        """Lee la fecha del campo de búsqueda y recarga la grilla completa."""
        fecha = self._view.entry_fecha.get().strip()

        # Si el campo está vacío, uso la fecha de hoy por defecto
        if not fecha:
            fecha = date.today().isoformat()
            self._view.entry_fecha.delete(0, "end")
            self._view.entry_fecha.insert(0, fecha)

        try:
            fecha = datetime.strptime(fecha, "%Y-%m-%d").date().isoformat()
        except ValueError:
            messagebox.showerror(
                "Fecha inválida",
                "Escribe la fecha con este formato: AAAA-MM-DD",
            )
            return

        # Cargo los empleados activos para mostrar una columna por barbero
        empleados = self._modelo_emp.listar()

        # Cargo todas las citas de esa fecha (sin filtrar por empleado)
        citas = self._modelo_cita.listar_por_rango(fecha, fecha)

        self._view.actualizar_titulo_fecha(fecha)

        # Le paso los datos a la vista para que dibuje la grilla
        self._view.cargar_agenda(empleados, citas)

    # ── Confirmar cita desde el popup de la agenda ───────────────────────────

    def _confirmar_desde_agenda(self, codigo: str):
        """Confirma una cita pendiente al hacer clic en su celda de la agenda."""
        if self._modelo_cita.confirmar(codigo):
            messagebox.showinfo("Cita confirmada", f"Cita {codigo} confirmada correctamente.")
        else:
            messagebox.showerror("Error", f"No se pudo confirmar la cita {codigo}.")
        # Recargo la agenda para que la celda cambie de color a CONFIRMADA
        self._buscar()

    def _iniciar_desde_agenda(self, codigo: str):
        """Pone en curso una cita al hacer clic en su celda de la agenda."""
        self._modelo_cita.actualizar_estado(codigo, "en_curso")
        messagebox.showinfo("Servicio iniciado", f"Cita {codigo} marcada como en servicio.")
        self._buscar()

    # ── Abrir modal de nueva cita ─────────────────────────────────────────────

    def _abrir_modal(self):
        """Abre el diálogo para registrar una nueva cita desde la agenda."""
        from app.views.screens.modal_nueva_cita import ModalNuevaCita

        modal = ModalNuevaCita(self._view, self._usuario)

        # Cuando se guarda la cita en el modal, recargo la agenda automáticamente
        modal.on_cita_creada = self._buscar
        # grab_set() bloquea la ventana principal mientras el modal está abierto
        modal.grab_set()
