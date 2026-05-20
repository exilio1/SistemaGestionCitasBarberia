"""
Handlers del bot de Telegram — Barbers Studio.

Flujo completo de /agendar:
  nombre → cédula → [confirmar cédula] → teléfono
  → servicio → barbero → fecha (calendario) → hora → confirmar cita
"""

import calendar as _cal
from datetime import date, datetime
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
)
from telegram.ext import ContextTypes, ConversationHandler

from app.models.cliente_model import formatear_cedula
from app.services.agenda_service import (
    obtener_servicios,
    obtener_empleados,
    agendar_cita,
    horarios_disponibles,
    horarios_disponibles_cualquiera,
    cancelar_cita,
    reprogramar_cita,
    obtener_cita,
)

# ── Estados de /agendar (9 pasos) ─────────────────────────────────────────────
(
    NOMBRE,
    CEDULA,
    CONFIRMAR_CEDULA,
    TELEFONO,
    SERVICIO,
    BARBERO,
    FECHA,
    HORA,
    CONFIRMAR,
) = range(9)

# ── Estados de los otros flujos ───────────────────────────────────────────────
CODIGO_CANCELAR              = 10
CODIGO_REPROG, FECHA_REPROG, HORA_REPROG = 20, 21, 22
CODIGO_MICITA                = 30

# ── Teclado persistente que aparece siempre en la parte inferior del chat ─────
# El usuario puede presionar cualquiera de estos botones en cualquier momento
TECLADO_INICIO = ReplyKeyboardMarkup(
    [
        ["/agendar", "/micita"],
        ["/cancelar", "/reprogramar"],
        ["/start"],
    ],
    resize_keyboard=True,  # lo hace compacto para no ocupar mucho espacio
)

# Nombres de los meses en español para el calendario
_MESES = {
    1: "Enero", 2: "Febrero", 3: "Marzo",    4: "Abril",
    5: "Mayo",  6: "Junio",   7: "Julio",    8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre",
}


# ── Helper: calendario inline ─────────────────────────────────────────────────

def _teclado_calendario(anio: int, mes: int) -> InlineKeyboardMarkup:
    """
    Genera un teclado inline con el calendario del mes indicado.
    Los días pasados aparecen con guion y no son seleccionables.
    Incluye flechas para navegar entre meses.
    """
    hoy = date.today()
    filas = []

    # ── Titulo del mes ────────────────────────────────────────────────────
    filas.append([
        InlineKeyboardButton(
            f"-- {_MESES[mes]} {anio} --",
            callback_data="noop",
        )
    ])

    # ── Encabezado de dias de la semana ───────────────────────────────────
    filas.append([
        InlineKeyboardButton(d, callback_data="noop")
        for d in ["Lu", "Ma", "Mi", "Ju", "Vi", "Sa", "Do"]
    ])

    # ── Dias del mes ──────────────────────────────────────────────────────
    # monthrange devuelve (dia_semana_del_1, total_dias) donde lunes=0
    primer_dia, total_dias = _cal.monthrange(anio, mes)

    fila_actual = [
        InlineKeyboardButton(" ", callback_data="noop")
        for _ in range(primer_dia)  # espacios vacíos antes del primer día
    ]

    for dia in range(1, total_dias + 1):
        fecha_dia = date(anio, mes, dia)
        if fecha_dia < hoy:
            # Dia pasado — no seleccionable
            fila_actual.append(InlineKeyboardButton("·", callback_data="noop"))
        else:
            # Dia disponible — callback con la fecha completa
            fila_actual.append(InlineKeyboardButton(
                str(dia),
                callback_data=f"cal_{anio}_{mes:02d}_{dia:02d}",
            ))

        if len(fila_actual) == 7:
            filas.append(fila_actual)
            fila_actual = []

    # Completo la ultima fila si quedaron dias sueltos
    if fila_actual:
        while len(fila_actual) < 7:
            fila_actual.append(InlineKeyboardButton(" ", callback_data="noop"))
        filas.append(fila_actual)

    # ── Navegacion anterior / siguiente ───────────────────────────────────
    if mes == 1:
        mes_ant, anio_ant = 12, anio - 1
    else:
        mes_ant, anio_ant = mes - 1, anio

    if mes == 12:
        mes_sig, anio_sig = 1, anio + 1
    else:
        mes_sig, anio_sig = mes + 1, anio

    nav = []
    # Solo muestro "Anterior" si ese mes aun no ha pasado
    if date(anio_ant, mes_ant, 1) >= date(hoy.year, hoy.month, 1):
        nav.append(InlineKeyboardButton(
            "◀ Anterior",
            callback_data=f"cal_nav_{anio_ant}_{mes_ant:02d}",
        ))
    else:
        nav.append(InlineKeyboardButton(" ", callback_data="noop"))

    nav.append(InlineKeyboardButton(
        "Siguiente ▶",
        callback_data=f"cal_nav_{anio_sig}_{mes_sig:02d}",
    ))
    filas.append(nav)

    return InlineKeyboardMarkup(filas)


# ── Helper: filas de botones de horas ────────────────────────────────────────

def _botones_horas(horas):
    """Convierte una lista de horas en filas de 4 botones para el teclado inline."""
    botones, fila = [], []
    for hora in horas:
        fila.append(InlineKeyboardButton(hora, callback_data=hora))
        if len(fila) == 4:
            botones.append(fila)
            fila = []
    if fila:
        botones.append(fila)
    return botones


# ── /start ────────────────────────────────────────────────────────────────────

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Muestra la bienvenida con los comandos disponibles y el teclado persistente."""
    await update.message.reply_text(
        "*Bienvenido a Barbers Studio*\n\n"
        "Usa los botones de abajo o escribe un comando:\n\n"
        "/agendar — Reservar una nueva cita\n"
        "/cancelar — Cancelar tu cita\n"
        "/reprogramar — Cambiar fecha u hora\n"
        "/micita — Consultar tu cita\n",
        parse_mode="Markdown",
        reply_markup=TECLADO_INICIO,
    )


# ── /agendar — Paso 1: nombre ─────────────────────────────────────────────────

async def agendar_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Inicia el flujo de agendar cita. Limpia datos anteriores y pide el nombre."""
    ctx.user_data.clear()
    await update.message.reply_text(
        "Vamos a agendar tu cita.\n\n¿Cuál es tu nombre completo?"
    )
    return NOMBRE


async def nombre_recibido(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Guarda el nombre y pide la cédula."""
    ctx.user_data["nombre"] = update.message.text.strip()
    await update.message.reply_text(
        "¿Cuál es tu número de cédula?\n"
        "(Solo los dígitos, sin puntos ni espacios)"
    )
    return CEDULA


# ── /agendar — Paso 2: cédula con confirmación ────────────────────────────────

async def cedula_recibida(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Recibe la cédula, la formatea y pide confirmación al cliente."""
    cedula_raw = update.message.text.strip()
    digitos = "".join(c for c in cedula_raw if c.isdigit())

    if len(digitos) < 5:
        await update.message.reply_text(
            "El número de cédula parece muy corto. Ingrésalo de nuevo:"
        )
        return CEDULA

    ctx.user_data["cedula"] = digitos
    cedula_formateada = formatear_cedula(digitos)

    teclado = InlineKeyboardMarkup([[
        InlineKeyboardButton("Sí, es correcta", callback_data="ced_si"),
        InlineKeyboardButton("No, corregir",    callback_data="ced_no"),
    ]])
    await update.message.reply_text(
        f"Tu número de cédula es: *{cedula_formateada}*\n\n"
        "¿Es correcto?",
        reply_markup=teclado,
        parse_mode="Markdown",
    )
    return CONFIRMAR_CEDULA


async def confirmar_cedula(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Procesa la confirmación de la cédula — si dijo 'No', vuelve a pedirla."""
    query = update.callback_query
    await query.answer()

    if query.data == "ced_no":
        await query.edit_message_text(
            "Entendido. Ingresa tu número de cédula de nuevo:"
        )
        return CEDULA

    await query.edit_message_text(
        f"Cédula confirmada: *{formatear_cedula(ctx.user_data['cedula'])}*\n\n"
        "¿Cuál es tu número de teléfono?",
        parse_mode="Markdown",
    )
    return TELEFONO


# ── /agendar — Paso 3: teléfono ───────────────────────────────────────────────

async def telefono_recibido(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Guarda el teléfono y muestra el catálogo de servicios como botones."""
    ctx.user_data["telefono"] = update.message.text.strip()
    servicios = obtener_servicios()

    if not servicios:
        await update.message.reply_text(
            "No hay servicios disponibles en este momento.\n"
            "Contacta directamente a la barberia."
        )
        return ConversationHandler.END

    botones = []
    for srv in servicios:
        etiqueta = f"{srv['nombre']}  —  ${srv['precio']:,.0f}"
        botones.append([InlineKeyboardButton(etiqueta, callback_data=str(srv["id"]))])

    await update.message.reply_text(
        "Elige el servicio:",
        reply_markup=InlineKeyboardMarkup(botones),
    )
    return SERVICIO


# ── /agendar — Paso 4: servicio ───────────────────────────────────────────────

async def servicio_recibido(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Guarda el servicio elegido y muestra los barberos disponibles."""
    query = update.callback_query
    await query.answer()

    servicio_id = int(query.data)
    servicios   = obtener_servicios()
    srv         = next((s for s in servicios if s["id"] == servicio_id), None)

    if not srv:
        await query.edit_message_text(
            "Servicio no encontrado. Escribe /agendar para intentar de nuevo."
        )
        return ConversationHandler.END

    ctx.user_data["servicio_id"] = srv["id"]
    ctx.user_data["servicio"]    = srv["nombre"]
    ctx.user_data["precio"]      = srv["precio"]

    empleados = obtener_empleados()
    if not empleados:
        await query.edit_message_text(
            "No hay barberos disponibles en este momento. Intenta más tarde."
        )
        return ConversationHandler.END

    botones = []
    for emp in empleados:
        etiqueta = f"{emp.get('nombre')}  ({emp.get('especialidad', '')})"
        botones.append([InlineKeyboardButton(etiqueta, callback_data=str(emp["id"]))])
    botones.append([InlineKeyboardButton("Cualquier barbero disponible", callback_data="0")])

    await query.edit_message_text(
        f"Servicio: *{srv['nombre']}* — ${srv['precio']:,.0f}\n\n"
        "¿Con cuál barbero quieres tu cita?",
        reply_markup=InlineKeyboardMarkup(botones),
        parse_mode="Markdown",
    )
    return BARBERO


# ── /agendar — Paso 5: barbero ────────────────────────────────────────────────

async def barbero_recibido(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Guarda el barbero elegido y muestra el calendario para elegir la fecha."""
    query = update.callback_query
    await query.answer()

    empleado_id = int(query.data)

    if empleado_id == 0:
        ctx.user_data["empleado_id"]    = None
        ctx.user_data["barbero_nombre"] = "Primer barbero disponible"
    else:
        empleados = obtener_empleados()
        barbero   = next((e for e in empleados if e["id"] == empleado_id), None)
        ctx.user_data["empleado_id"]    = empleado_id
        ctx.user_data["barbero_nombre"] = barbero["nombre"] if barbero else f"Barbero #{empleado_id}"

    hoy = date.today()
    await query.edit_message_text(
        f"Barbero: *{ctx.user_data['barbero_nombre']}*\n\n"
        "Selecciona la fecha de tu cita:",
        reply_markup=_teclado_calendario(hoy.year, hoy.month),
        parse_mode="Markdown",
    )
    return FECHA


# ── /agendar — Paso 6: fecha (calendario inline) ─────────────────────────────

async def fecha_recibida(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """
    Maneja los clics del calendario inline:
    - 'noop'        → botón decorativo, no hace nada
    - 'cal_nav_...' → navega al mes anterior o siguiente
    - 'cal_...'     → el usuario seleccionó un día, muestro las horas disponibles
    """
    query = update.callback_query
    await query.answer()
    data = query.data

    # Botón decorativo — ignorar
    if data == "noop":
        return FECHA

    # Navegación entre meses: cal_nav_YYYY_MM
    if data.startswith("cal_nav_"):
        resto               = data[len("cal_nav_"):]
        anio_str, mes_str   = resto.split("_")
        await query.edit_message_reply_markup(
            reply_markup=_teclado_calendario(int(anio_str), int(mes_str))
        )
        return FECHA

    # Selección de día: cal_YYYY_MM_DD
    if data.startswith("cal_"):
        resto               = data[len("cal_"):]
        anio_str, mes_str, dia_str = resto.split("_")
        fecha_str = f"{anio_str}-{mes_str}-{dia_str}"
        ctx.user_data["fecha"] = fecha_str

        empleado_id = ctx.user_data.get("empleado_id")
        if empleado_id:
            horas = horarios_disponibles(fecha_str, empleado_id)
            pie   = f"para {ctx.user_data['barbero_nombre']}"
        else:
            horas = horarios_disponibles_cualquiera(fecha_str)
            pie   = "con algún barbero disponible"

        if not horas:
            # Sin horas disponibles — el cliente elige otra fecha en el mismo calendario
            await query.edit_message_text(
                f"No hay horas disponibles el {fecha_str} {pie}.\n\n"
                "Elige otra fecha:",
                reply_markup=_teclado_calendario(int(anio_str), int(mes_str)),
            )
            return FECHA

        await query.edit_message_text(
            f"Fecha: *{fecha_str}*\n\n"
            f"Horas disponibles {pie}:",
            reply_markup=InlineKeyboardMarkup(_botones_horas(horas)),
            parse_mode="Markdown",
        )
        return HORA

    return FECHA


# ── /agendar — Paso 7: hora ───────────────────────────────────────────────────

async def hora_recibida(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Guarda la hora elegida y muestra el resumen de la cita para confirmar."""
    query = update.callback_query
    await query.answer()

    ctx.user_data["hora"] = query.data
    d = ctx.user_data

    resumen = (
        f"*Resumen de tu cita:*\n\n"
        f"Nombre:   {d['nombre']}\n"
        f"Cédula:   {formatear_cedula(d['cedula'])}\n"
        f"Teléfono: {d['telefono']}\n"
        f"Servicio: {d['servicio']}\n"
        f"Barbero:  {d['barbero_nombre']}\n"
        f"Fecha:    {d['fecha']}\n"
        f"Hora:     {d['hora']}\n"
        f"Precio:   ${d['precio']:,.0f}\n\n"
        "¿Confirmas la cita?"
    )

    teclado = InlineKeyboardMarkup([[
        InlineKeyboardButton("Sí, confirmar", callback_data="si"),
        InlineKeyboardButton("No, cancelar",  callback_data="no"),
    ]])
    await query.edit_message_text(resumen, reply_markup=teclado, parse_mode="Markdown")
    return CONFIRMAR


# ── /agendar — Paso 8: guardar en BD ─────────────────────────────────────────

async def confirmar_cita(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Si el cliente confirmó, guarda la cita en la BD y entrega el código para copiar."""
    query = update.callback_query
    await query.answer()

    if query.data == "no":
        await query.edit_message_text(
            "Cita no agendada. Escribe /agendar para intentar de nuevo."
        )
        return ConversationHandler.END

    d = ctx.user_data
    codigo, error = agendar_cita(
        nombre=d["nombre"],
        cedula=d["cedula"],
        telefono=d["telefono"],
        servicio_id=d["servicio_id"],
        fecha=d["fecha"],
        hora=d["hora"],
        empleado_id=d.get("empleado_id"),
        confirmar=True,   # el cliente ya confirmo en el chat, no necesita aprobacion manual
    )

    if error:
        await query.edit_message_text(
            f"No se pudo agendar: {error}\n\nEscribe /agendar para intentar de nuevo."
        )
        return ConversationHandler.END

    # El código va en backticks para que el cliente pueda tocarlo y copiarlo
    await query.edit_message_text(
        f"*Cita confirmada*\n\n"
        f"Tu codigo de cita es:\n\n"
        f"`{codigo}`\n\n"
        f"_(Toca el codigo para copiarlo)_\n\n"
        f"Guarda este codigo, lo vas a necesitar para cancelar o reprogramar tu cita.\n\n"
        f"Usa /micita para consultar el estado de tu cita en cualquier momento.",
        parse_mode="Markdown",
    )
    return ConversationHandler.END


async def salir_flujo(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Cancela el flujo actual cuando el usuario escribe /salir."""
    await update.message.reply_text(
        "Operación cancelada.\n\nUsa los botones de abajo o escribe /start para comenzar.",
        reply_markup=TECLADO_INICIO,
    )
    return ConversationHandler.END


# ── /cancelar ─────────────────────────────────────────────────────────────────

async def cancelar_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Inicia el flujo de cancelación — pide el código de la cita."""
    await update.message.reply_text(
        "Indica el código de tu cita para cancelarla:\n"
        "_(Puedes copiarlo de tu mensaje de confirmación)_",
        parse_mode="Markdown",
    )
    return CODIGO_CANCELAR


async def codigo_cancelar_recibido(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Recibe el código y cancela la cita si existe."""
    codigo = update.message.text.strip().upper()
    if cancelar_cita(codigo):
        await update.message.reply_text(
            f"Cita `{codigo}` cancelada correctamente.",
            parse_mode="Markdown",
        )
    else:
        await update.message.reply_text(
            "No se encontró esa cita, o ya estaba completada o cancelada."
        )
    return ConversationHandler.END


# ── /reprogramar ──────────────────────────────────────────────────────────────

async def reprogramar_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Inicia el flujo de reprogramación — pide el código de la cita."""
    ctx.user_data.clear()
    await update.message.reply_text(
        "Indica el código de la cita a reprogramar:\n"
        "_(Puedes copiarlo de tu mensaje de confirmación)_",
        parse_mode="Markdown",
    )
    return CODIGO_REPROG


async def codigo_reprog_recibido(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Verifica que la cita exista y esté en estado reprogramable, luego muestra el calendario."""
    codigo = update.message.text.strip().upper()
    cita   = obtener_cita(codigo)

    if not cita:
        await update.message.reply_text("No se encontró esa cita. Verifica el código.")
        return ConversationHandler.END

    if cita.get("estado") in ("completada", "cancelada"):
        await update.message.reply_text(
            f"No se puede reprogramar: la cita está '{cita['estado']}'."
        )
        return ConversationHandler.END

    ctx.user_data["codigo"]      = codigo
    ctx.user_data["empleado_id"] = cita.get("empleado_id")

    hoy = date.today()
    await update.message.reply_text(
        f"Cita encontrada:\n"
        f"Servicio:     {cita.get('servicio')}\n"
        f"Fecha actual: {cita.get('fecha')}\n"
        f"Hora actual:  {str(cita.get('hora', ''))[:5]}\n\n"
        "Selecciona la nueva fecha:",
        reply_markup=_teclado_calendario(hoy.year, hoy.month),
    )
    return FECHA_REPROG


async def fecha_reprog_recibida(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """
    Maneja los clics del calendario en el flujo de reprogramacion.
    Misma lógica que fecha_recibida pero para FECHA_REPROG.
    """
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "noop":
        return FECHA_REPROG

    if data.startswith("cal_nav_"):
        resto             = data[len("cal_nav_"):]
        anio_str, mes_str = resto.split("_")
        await query.edit_message_reply_markup(
            reply_markup=_teclado_calendario(int(anio_str), int(mes_str))
        )
        return FECHA_REPROG

    if data.startswith("cal_"):
        resto                      = data[len("cal_"):]
        anio_str, mes_str, dia_str = resto.split("_")
        fecha_str = f"{anio_str}-{mes_str}-{dia_str}"
        ctx.user_data["nueva_fecha"] = fecha_str

        horas = horarios_disponibles(fecha_str, ctx.user_data.get("empleado_id"))

        if not horas:
            await query.edit_message_text(
                f"No hay horas disponibles para el {fecha_str}.\n\n"
                "Elige otra fecha:",
                reply_markup=_teclado_calendario(int(anio_str), int(mes_str)),
            )
            return FECHA_REPROG

        await query.edit_message_text(
            f"Nueva fecha: *{fecha_str}*\n\n"
            "Horas disponibles:",
            reply_markup=InlineKeyboardMarkup(_botones_horas(horas)),
            parse_mode="Markdown",
        )
        return HORA_REPROG

    return FECHA_REPROG


async def hora_reprog_recibida(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Guarda la nueva hora y reprograma la cita en la BD."""
    query = update.callback_query
    await query.answer()

    exito = reprogramar_cita(
        ctx.user_data["codigo"],
        ctx.user_data["nueva_fecha"],
        query.data,
    )

    if exito:
        await query.edit_message_text(
            f"Cita `{ctx.user_data['codigo']}` reprogramada correctamente.\n\n"
            f"Nueva fecha: *{ctx.user_data['nueva_fecha']}*\n"
            f"Nueva hora:  *{query.data}*",
            parse_mode="Markdown",
        )
    else:
        await query.edit_message_text(
            "No se pudo reprogramar. Escribe /reprogramar e intenta de nuevo."
        )
    return ConversationHandler.END


# ── /micita ───────────────────────────────────────────────────────────────────

async def micita_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Inicia el flujo de consulta de cita — pide el código."""
    await update.message.reply_text(
        "Ingresa el código de tu cita:\n"
        "_(Puedes copiarlo de tu mensaje de confirmación)_",
        parse_mode="Markdown",
    )
    return CODIGO_MICITA


async def codigo_micita_recibido(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Busca la cita por código y muestra sus detalles al cliente."""
    codigo = update.message.text.strip().upper()
    cita   = obtener_cita(codigo)

    if not cita:
        await update.message.reply_text("No se encontró ninguna cita con ese código.")
        return ConversationHandler.END

    etiquetas = {
        "pendiente":  "Pendiente de confirmación",
        "confirmada": "Confirmada",
        "en_curso":   "En servicio ahora",
        "completada": "Completada",
        "cancelada":  "Cancelada",
    }
    estado_txt = etiquetas.get(cita.get("estado", ""), cita.get("estado", ""))

    await update.message.reply_text(
        f"*Informacion de tu cita:*\n\n"
        f"Codigo:   `{codigo}`\n"
        f"Servicio: {cita.get('servicio')}\n"
        f"Fecha:    {cita.get('fecha')}\n"
        f"Hora:     {str(cita.get('hora', ''))[:5]}\n"
        f"Estado:   {estado_txt}\n\n"
        f"_(Toca el codigo para copiarlo)_",
        parse_mode="Markdown",
    )
    return ConversationHandler.END


# ── Handler de mensajes fuera de flujo ───────────────────────────────────────
# Se activa cuando el usuario escribe texto sin estar dentro de ninguna
# conversacion activa (/agendar, /cancelar, etc.). Guia al usuario para
# que use los comandos correctos en lugar de quedarse sin respuesta.

async def mensaje_desconocido(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Responde a cualquier texto que no pertenezca a un flujo activo."""
    await update.message.reply_text(
        "Para usar el servicio de Barbers Studio elige una de estas opciones:\n\n"
        "/agendar — Reservar una nueva cita\n"
        "/micita — Consultar el estado de tu cita\n"
        "/cancelar — Cancelar tu cita\n"
        "/reprogramar — Cambiar la fecha u hora de tu cita\n\n"
        "Tambien puedes usar los botones que aparecen en la parte inferior del chat.",
        reply_markup=TECLADO_INICIO,
    )
