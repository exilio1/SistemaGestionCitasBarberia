
from datetime import date, datetime
from tkinter import messagebox
from app.models.pago_model import PagoModel
from app.models.cita_model import CitaModel
from app.models.factura_model import FacturaModel
from app.views.screens.facturacion_view import FacturacionView


class FacturacionController:
    def __init__(self, view, usuario):
        # Instancio los modelos que necesito para esta pantalla
        self._modelo_pago    = PagoModel()
        self._modelo_cita    = CitaModel()
        self._modelo_factura = FacturaModel()
        self._view   = view
        self._usuario = usuario

        # Conecto el botón de filtrar fechas
        self._view.btn_filtrar.configure(command=self._filtrar)

        # El botón de generar factura está disponible para todos los roles
        self._view.btn_generar_factura.configure(command=self._generar_factura)

        # El botón de registrar pago solo existe en la vista de la recepcionista
        if hasattr(self._view, "btn_registrar"):
            self._view.btn_registrar.configure(command=self._registrar_pago)

        # Cargo los datos del mes actual al abrir la pantalla
        self._cargar_mes_actual()

    # ── Cargar mes actual ─────────────────────────────────────────────────────

    def _cargar_mes_actual(self):
        """Carga los pagos y facturas del mes en curso al abrir la pantalla."""
        hoy   = date.today()
        desde = hoy.replace(day=1).isoformat()  # primer día del mes
        hasta = hoy.isoformat()

        # Pongo las fechas en los campos de filtro para que el usuario las vea
        self._view.entry_desde.insert(0, desde)
        self._view.entry_hasta.insert(0, hasta)

        self._cargar(desde, hasta)

    # ── Filtrar por fechas ────────────────────────────────────────────────────

    def _filtrar(self):
        """Lee las fechas del formulario y recarga los datos del período."""
        desde = self._view.entry_desde.get().strip()
        hasta = self._view.entry_hasta.get().strip()

        if not desde or not hasta:
            self._view.mostrar_msg_pago("Ingresa las fechas para filtrar.", error=True)
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

        self._cargar(fecha_desde.isoformat(), fecha_hasta.isoformat())

    # ── Cargar datos ──────────────────────────────────────────────────────────

    def _cargar(self, desde, hasta):
        """Carga pagos y facturas del período y actualiza los KPIs del encabezado."""
        # Obtengo los pagos del período
        pagos = self._modelo_pago.listar_por_periodo(desde, hasta)

        # Enriquezco cada pago con el código de su cita para mostrarlo en la tabla
        pagos_enriquecidos = []
        for p in pagos:
            cita = self._modelo_cita.obtener_por_id(p.get("cita_id"))
            p_copia = dict(p)
            p_copia["codigo_cita"] = cita.get("codigo", "") if cita else ""
            pagos_enriquecidos.append(p_copia)

        self._view.mostrar_pagos(pagos_enriquecidos)

        # Calculo los KPIs — ingresos de hoy y del mes
        hoy    = date.today().isoformat()
        ing_hoy = self._modelo_pago.ingresos_por_periodo(hoy, hoy)
        ing_mes = self._modelo_pago.ingresos_por_periodo(desde, hasta)

        # Cuento las citas pendientes de cobro (completadas o confirmadas sin pago)
        citas_hoy = self._modelo_cita.listar_por_rango(hoy, hoy)
        pendientes = len([c for c in citas_hoy if c.get("estado") in ("pendiente", "confirmada")])

        total_hoy = ing_hoy.get("total", 0) or 0
        total_mes = ing_mes.get("total", 0) or 0

        # Actualizo los tres KPIs del encabezado
        self._view.actualizar_kpi_hoy(f"${total_hoy:,.0f}")
        self._view.actualizar_kpi_mes(f"${total_mes:,.0f}")
        self._view.actualizar_kpi_pendientes(pendientes)
        self._view.actualizar_rango(desde, hasta)

        # Cargo también las facturas del período
        try:
            facturas = self._modelo_factura.listar()
            self._view.mostrar_facturas(facturas)
        except Exception:
            self._view.mostrar_facturas([])

    # ── Registrar pago ────────────────────────────────────────────────────────

    def _registrar_pago(self):
        """Registra el pago de una cita. Solo disponible para la recepcionista."""
        codigo     = self._view.entry_codigo.get().strip().upper()
        monto_txt  = self._view.entry_monto.get().strip()
        metodo     = self._view.opt_metodo.get()

        # Valido los campos obligatorios
        if not codigo:
            self._view.mostrar_msg_pago("Ingresa el código de la cita.", error=True)
            return
        if not monto_txt:
            self._view.mostrar_msg_pago("Ingresa el monto.", error=True)
            return

        # Convierto el monto a número
        try:
            monto = float(monto_txt)
        except ValueError:
            self._view.mostrar_msg_pago("El monto debe ser un número.", error=True)
            return

        # Busco la cita para obtener su ID interno
        cita = self._modelo_cita.obtener_por_codigo(codigo)
        if not cita:
            self._view.mostrar_msg_pago(f"No se encontró la cita '{codigo}'.", error=True)
            return

        if cita.get("estado") not in ("confirmada", "en_curso", "pendiente"):
            self._view.mostrar_msg_pago(
                f"La cita está en estado '{cita.get('estado')}' y no se puede cobrar.",
                error=True,
            )
            return

        pago_existente = self._modelo_pago.obtener_por_cita(cita["id"])
        if pago_existente:
            self._view.mostrar_msg_pago(
                "Esa cita ya tiene un pago registrado.", error=True
            )
            return

        # Registro el pago y obtengo el desglose de ganancias
        fecha_hoy = date.today().isoformat()
        try:
            resultado = self._modelo_pago.registrar(
                cita_id=cita["id"],
                monto=monto,
                metodo=metodo,
                fecha=fecha_hoy,
            )
        except ValueError as e:
            self._view.mostrar_msg_pago(str(e), error=True)
            return

        # Marco la cita como completada ahora que se cobró
        self._modelo_cita.actualizar_estado(codigo, "completada")

        pago_creado = self._modelo_pago.obtener_por_cita(cita["id"])
        numero_factura = None
        if pago_creado:
            numero_factura = self._modelo_factura.generar(
                pago_creado["id"],
                f"Pago automático de la cita {codigo}",
            )

        # Muestro el desglose de ganancias al usuario
        emp = resultado.get("empleado", 0)
        neg = resultado.get("negocio", 0)
        msg = (
            f"Pago registrado: ${monto:,.0f}  |  "
            f"Barbero: ${emp:,.0f}  |  Negocio: ${neg:,.0f}"
        )
        if numero_factura:
            msg += f"  |  Factura: {numero_factura}"
        self._view.mostrar_msg_pago(msg, error=False)

        # Limpio los campos y recargo la tabla
        self._view.entry_codigo.delete(0, "end")
        self._view.entry_monto.delete(0, "end")
        self._filtrar()

    # ── Generar factura ───────────────────────────────────────────────────────

    def _generar_factura(self):
        """Genera una factura para el pago indicado por ID."""
        pago_id_txt = self._view.entry_pago_id.get().strip()
        detalle     = self._view.entry_detalle.get().strip()

        # El ID es obligatorio
        if not pago_id_txt:
            self._view.mostrar_msg_factura("Ingresa el ID del pago.", error=True)
            return

        # El ID debe ser un número entero
        try:
            pago_id = int(pago_id_txt)
        except ValueError:
            self._view.mostrar_msg_factura("El ID del pago debe ser un número entero.", error=True)
            return

        # Genero la factura a través del modelo
        try:
            numero = self._modelo_factura.generar(pago_id, detalle)
            if not numero:
                self._view.mostrar_msg_factura(
                    "No se pudo generar la factura. Verifica el pago o si ya existe una factura.",
                    error=True,
                )
                return

            self._view.mostrar_msg_factura(f"Factura generada: {numero}", error=False)

            # Limpio los campos y recargo la tabla de facturas
            self._view.entry_pago_id.delete(0, "end")
            self._view.entry_detalle.delete(0, "end")
            self._filtrar()

        except Exception as e:
            self._view.mostrar_msg_factura(f"Error: {e}", error=True)
