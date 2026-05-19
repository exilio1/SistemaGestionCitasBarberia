
from datetime import date
from app.models.cita_model import CitaModel
from app.models.pago_model import PagoModel
from app.models.gasto_model import GastoModel
from app.views.screens.panel_principal_view import PanelPrincipalView


class PanelPrincipalController:
    def __init__(self, view, usuario):
        # Instancio los tres modelos que necesito para los KPIs
        self._modelo_cita  = CitaModel()
        self._modelo_pago  = PagoModel()
        self._modelo_gasto = GastoModel()
        self._view   = view
        self._usuario = usuario

        # El callback de "ver agenda completa" lo asigna el DashboardView
        self._cargar_datos()

    def _cargar_datos(self):
        """Carga todos los datos del día actual y los muestra en la vista."""
        hoy = date.today().isoformat()

        # ── Citas de hoy ──────────────────────────────────────────────────
        citas_hoy = self._modelo_cita.listar_por_rango(hoy, hoy)
        total_citas = len(citas_hoy)
        self._view.actualizar_kpi("citas_hoy", str(total_citas))

        # ── Ingresos estimados (pagos del día) ────────────────────────────
        ingresos = self._modelo_pago.ingresos_por_periodo(hoy, hoy)
        total_ing = ingresos.get("total", 0) or 0
        # Formateo el número según su magnitud para que sea legible
        if total_ing >= 1_000_000:
            texto_ing = f"COP $ {total_ing/1_000_000:.1f}M"
        elif total_ing >= 1_000:
            texto_ing = f"COP $ {total_ing/1_000:.0f}k"
        else:
            texto_ing = f"COP $ {total_ing:,.0f}"
        self._view.actualizar_kpi("ingresos", texto_ing)

        # ── Ocupación % ───────────────────────────────────────────────────
        # Calculo cuántas horas están ocupadas de las disponibles en el día
        total_slots = 22  # aprox horas disponibles por día (8am-19pm cada 30 min)
        ocupadas = len([c for c in citas_hoy if c.get("estado") != "cancelada"])
        pct = int((ocupadas / total_slots) * 100) if total_slots > 0 else 0
        self._view.actualizar_kpi("ocupacion", f"{pct}%")

        # ── Gastos del día (solo para el administrador) ───────────────────
        if self._usuario.get("rol") == "administrador":
            gastos = self._modelo_gasto.total_por_periodo(hoy, hoy)
            if gastos >= 1_000:
                texto_gasto = f"COP$ {gastos/1_000:.0f}k"
            else:
                texto_gasto = f"COP$ {gastos:,.0f}"
            self._view.actualizar_kpi("gastos_hoy", texto_gasto)

        # ── Próximas citas (pendientes y confirmadas) ─────────────────────
        # Filtro solo las citas que siguen activas (no completadas ni canceladas)
        proximas = [
            c for c in citas_hoy
            if c.get("estado") in ("pendiente", "confirmada", "en_curso")
        ]
        self._view.cargar_proximas_citas(proximas)

        # ── Tendencia semanal ─────────────────────────────────────────────
        # Calculo cuántas citas hubo cada día de la semana actual
        from datetime import timedelta
        hoy_dt = date.today()
        lunes = hoy_dt - timedelta(days=hoy_dt.weekday())  # primer día de la semana
        datos_semana = []
        for i in range(7):
            dia = (lunes + timedelta(days=i)).isoformat()
            citas_dia = self._modelo_cita.listar_por_rango(dia, dia)
            datos_semana.append(len(citas_dia))

        self._view.mostrar_tendencia(datos_semana)
        total_semana = sum(datos_semana)
        self._view.mostrar_resumen_semanal(total_semana, 8.4)
