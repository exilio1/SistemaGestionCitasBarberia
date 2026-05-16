
from datetime import date, timedelta, datetime
from tkinter import messagebox
from app.models.pago_model import PagoModel
from app.models.gasto_model import GastoModel
from app.models.cita_model import CitaModel
from app.models.empleado_model import EmpleadoModel
from app.views.screens.reportes_view import ReportesView


class ReportesController:
    def __init__(self, view, usuario):
        # Instancio los modelos que necesito para generar el reporte
        self._modelo_pago  = PagoModel()
        self._modelo_gasto = GastoModel()
        self._modelo_cita  = CitaModel()
        self._modelo_emp   = EmpleadoModel()
        self._view         = view
        self._usuario      = usuario

        # Conecto el botón de generar con el método correspondiente
        self._view.btn_generar.configure(command=self._generar)

        # Cargo el mes actual por defecto al abrir
        self._cargar_mes_actual()

    # ── Cargar mes actual ─────────────────────────────────────────────────────

    def _cargar_mes_actual(self):
        """Pone las fechas del mes actual en los campos y genera el reporte."""
        hoy   = date.today()
        desde = hoy.replace(day=1).isoformat()
        hasta = hoy.isoformat()

        # Pongo las fechas en los campos de filtro de la vista
        self._view.entry_desde.insert(0, desde)
        self._view.entry_hasta.insert(0, hasta)

        self._generar_con_fechas(desde, hasta)

    # ── Generar reporte desde el formulario ───────────────────────────────────

    def _generar(self):
        """Lee las fechas del formulario y genera el reporte."""
        desde = self._view.entry_desde.get().strip()
        hasta = self._view.entry_hasta.get().strip()

        # Si faltan las fechas, no hago nada
        if not desde or not hasta:
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

        self._generar_con_fechas(fecha_desde.isoformat(), fecha_hasta.isoformat())

    # ── Calcular y mostrar reportes ───────────────────────────────────────────

    def _generar_con_fechas(self, desde, hasta):
        """Calcula todos los datos del reporte y los muestra en la vista."""

        # ── Datos de ingresos ─────────────────────────────────────────────
        ingresos = self._modelo_pago.ingresos_por_periodo(desde, hasta)
        total    = ingresos.get("total", 0) or 0
        ganancia = ingresos.get("negocio", 0) or 0

        # ── Citas del período ─────────────────────────────────────────────
        citas = self._modelo_cita.listar_por_rango(desde, hasta)
        n_citas = len(citas)

        try:
            fecha_ini = datetime.strptime(desde, "%Y-%m-%d").date()
            fecha_fin = datetime.strptime(hasta, "%Y-%m-%d").date()
            dias = (fecha_fin - fecha_ini).days + 1
        except Exception:
            dias = 1

        empleados = self._modelo_emp.listar()
        total_slots = max(len(empleados), 1) * 22 * max(dias, 1)
        ocupadas = len([c for c in citas if c.get("estado") != "cancelada"])
        ocupacion = round((ocupadas / total_slots) * 100, 1) if total_slots > 0 else 0

        # ── Ticket promedio ───────────────────────────────────────────────
        # Divido el total entre las citas que efectivamente se pagaron
        n_pagadas = len([c for c in citas if c.get("estado") == "completada"])
        ticket = (total / n_pagadas) if n_pagadas > 0 else 0

        # Actualizo los cuatro KPIs del encabezado
        self._view.actualizar_kpis(total, ticket, ocupacion, ganancia)

        # ── Gráfico de barras: últimos 7 días ─────────────────────────────
        etiquetas = []
        valores   = []

        try:
            fecha_ini = datetime.strptime(desde, "%Y-%m-%d").date()
            fecha_fin = datetime.strptime(hasta, "%Y-%m-%d").date()
            delta     = (fecha_fin - fecha_ini).days + 1

            # Si el rango es muy largo, muestro solo los últimos 7 días
            if delta > 7:
                fecha_ini = fecha_fin - timedelta(days=6)

            # Genero un punto por cada día del rango
            dia = fecha_ini
            while dia <= fecha_fin:
                # Calculo ingresos de ese día específico
                ing_dia = self._modelo_pago.ingresos_por_periodo(
                    dia.isoformat(), dia.isoformat()
                )
                nombres = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
                etiquetas.append(nombres[dia.weekday()])
                valores.append(ing_dia.get("total", 0) or 0)
                dia += timedelta(days=1)

            self._view.mostrar_grafico_barras(etiquetas, valores)

        except Exception:
            # Si hay algún error en las fechas, no muestro el gráfico
            self._view.mostrar_grafico_barras([], [])

        # ── Tabla de rendimiento por barbero ──────────────────────────────
        datos_barberos = self._modelo_pago.ganancias_por_empleado(desde, hasta)
        self._view.mostrar_tabla_barberos(datos_barberos)

        # ── Resumen de rentabilidad ───────────────────────────────────────
        # Resto los gastos del período a los ingresos para calcular la utilidad
        gastos  = self._modelo_gasto.total_por_periodo(desde, hasta)
        neto    = total - gastos
        signo   = "+" if neto >= 0 else ""
        resumen = (
            f"Ingresos totales:  ${total:>12,.0f}\n"
            f"Citas del período: {n_citas:>12}\n"
            f"Ocupación:        {ocupacion:>11.1f}%\n"
            f"Gastos del período: ${gastos:>11,.0f}\n"
            f"{'─'*38}\n"
            f"Rentabilidad neta: ${signo}{neto:>11,.0f}"
        )
        self._view.actualizar_periodo(desde, hasta)
        self._view.mostrar_resumen(resumen)
