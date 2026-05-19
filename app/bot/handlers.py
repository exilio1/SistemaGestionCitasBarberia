"""
Handlers del bot de Telegram — Barbers Studio.

Flujo completo de /agendar:
  nombre → cédula → [confirmar cédula] → teléfono
  → servicio → barbero → fecha → hora → confirmar cita
"""

from datetime import date, datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
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
# Cada constante representa un paso del flujo de conversación
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


# ── Helper: construir filas de botones de horas ───────────────────────────────

def _botones_horas(horas):
    """Convierte una lista de horas en filas de 4 botones para el teclado inline."""
    botones, fila = [], []
    for hora in horas:
        fila.append(InlineKeyboardButton(hora, callback_data=hora))
        # Cuando llego a 4 botones, cierro la fila y empiezo una nueva
        if len(fila) == 4:
            botones.append(fila)
            fila = []
    # Si quedó algún botón suelto, lo agrego como fila incompleta
    if fila:
        botones.append(fila)
    return botones


# ── /start ────────────────────────────────────────────────────────────────────

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Muestra el mensaje de bienvenida con los comandos disponibles."""
    await update.message.reply_text(
        "Bienvenido a *Barbers Studio*\n\n"
        "Comandos disponibles:\n\n"
        "/agendar — Reservar una nueva cita\n"
        "/cancelar — Cancelar tu cita\n"
        "/reprogramar — Cambiar fecha u hora\n"
        "/micita — Consultar tu cita\n",
        parse_mode="Markdown",
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

    # Valido que tenga al menos 5 dígitos para evitar errores de digitación
    digitos = "".join(c for c in cedula_raw if c.isdigit())
    if len(digitos) < 5:
        await update.message.reply_text(
            "El número de cédula parece muy corto. Ingrésalo de nuevo:"
        )
        return CEDULA

    ctx.user_data["cedula"] = digitos

    # Muestro la cédula con formato colombiano y pido confirmación
    cedula_formateada = formatear_cedula(digitos)
    teclado = InlineKeyboardMarkup([[
        InlineKeyboardButton("Sí, es correcta",  callback_data="ced_si"),
        InlineKeyboardButton("No, corregir",      callback_data="ced_no"),
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
        # El cliente quiere corregirla — vuelvo al paso de pedir cédula
        await query.edit_message_text(
            "Entendido. Ingresa tu número de cédula de nuevo:"
        )
        return CEDULA

    # Si confirmó que es correcta, paso a pedir el teléfono
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

    # Cargo los servicios desde la BD y los muestro como botones con precio
    servicios = obtener_servicios()
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

    # El callback_data contiene el ID del servicio en la BD
    servicio_id = int(query.data)
    servicios   = obtener_servicios()
    srv         = next((s for s in servicios if s["id"] == servicio_id), None)

    if not srv:
        await query.edit_message_text("Servicio no encontrado. Escribe /agendar para intentar de nuevo.")
        return ConversationHandler.END

    # Guardo los datos del servicio para usarlos al confirmar
    ctx.user_data["servicio_id"] = srv["id"]
    ctx.user_data["servicio"]    = srv["nombre"]
    ctx.user_data["precio"]      = srv["precio"]

    # Cargo los barberos activos
    empleados = obtener_empleados()
    if not empleados:
        await query.edit_message_text(
            "No hay barberos disponibles en este momento. Intenta más tarde."
        )
        return ConversationHandler.END

    # Muestro cada barbero como botón y agrego la opción de "cualquiera disponible"
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
    """Guarda el barbero elegido y pide la fecha de la cita."""
    query = update.callback_query
    await query.answer()

    empleado_id = int(query.data)

    # Si eligió "cualquier barbero" (id=0), se asignará automáticamente después
    if empleado_id == 0:
        ctx.user_data["empleado_id"]    = None
        ctx.user_data["barbero_nombre"] = "Primer barbero disponible"
    else:
        # Busco el nombre del barbero elegido en la lista
        empleados = obtener_empleados()
        barbero   = next((e for e in empleados if e["id"] == empleado_id), None)
        ctx.user_data["empleado_id"]    = empleado_id
        ctx.user_data["barbero_nombre"] = barbero["nombre"] if barbero else f"Barbero #{empleado_id}"

    hoy = date.today().isoformat()
    await query.edit_message_text(
        f"Barbero: *{ctx.user_data['barbero_nombre']}*\n\n"
        f"¿Para qué fecha quieres la cita?\n"
        f"Formato: AAAA-MM-DD  —  Ejemplo: {hoy}",
        parse_mode="Markdown",
    )
    return FECHA


# ── /agendar — Paso 6: fecha ──────────────────────────────────────────────────

async def fecha_recibida(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Valida la fecha ingresada y muestra las horas disponibles como botones."""
    texto_fecha = update.message.text.strip()

    # Valido que la fecha tenga el formato correcto
    try:
        fecha_obj = datetime.strptime(texto_fecha, "%Y-%m-%d").date()
    except ValueError:
        await update.message.reply_text(
            f"Formato incorrecto. Usa AAAA-MM-DD  (Ejemplo: {date.today().isoformat()})"
        )
        return FECHA

    # No permito fechas en el pasado
    if fecha_obj < date.today():
        await update.message.reply_text(
            "Esa fecha ya pasó. Escribe una fecha de hoy en adelante:"
        )
        return FECHA

    ctx.user_data["fecha"] = texto_fecha
    empleado_id = ctx.user_data.get("empleado_id")

    # Cargo las horas disponibles según si eligió un barbero específico o cualquiera
    if empleado_id:
        horas = horarios_disponibles(texto_fecha, empleado_id)
        pie   = f"para {ctx.user_data['barbero_nombre']}"
    else:
        horas = horarios_disponibles_cualquiera(texto_fecha)
        pie   = "con algún barbero disponible"

    if not horas:
        await update.message.reply_text(
            f"No hay horas disponibles el {texto_fecha} {pie}.\n"
            "Intenta con otra fecha:"
        )
        return FECHA

    # Muestro las horas disponibles como botones de 4 en 4
    await update.message.reply_text(
        f"Horas disponibles el {texto_fecha} {pie}:",
        reply_markup=InlineKeyboardMarkup(_botones_horas(horas)),
    )
    return HORA


# ── /agendar — Paso 7: hora ───────────────────────────────────────────────────

async def hora_recibida(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Guarda la hora elegida y muestra el resumen de la cita para confirmar."""
    query = update.callback_query
    await query.answer()

    ctx.user_data["hora"] = query.data
    d = ctx.user_data  # alias para no repetir ctx.user_data muchas veces

    # Armo el resumen completo de la cita para que el cliente lo revise
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
    """Si el cliente confirmó, guarda la cita en la BD y le da el código."""
    query = update.callback_query
    await query.answer()

    # Si el cliente cancela el proceso, termino el flujo
    if query.data == "no":
        await query.edit_message_text(
            "Cita no agendada. Escribe /agendar para intentar de nuevo."
        )
        return ConversationHandler.END

    # Llamo al servicio para crear la cita con todos los datos recolectados
    d = ctx.user_data
    codigo, error = agendar_cita(
        nombre=d["nombre"],
        cedula=d["cedula"],
        telefono=d["telefono"],
        servicio_id=d["servicio_id"],
        fecha=d["fecha"],
        hora=d["hora"],
        empleado_id=d.get("empleado_id"),
    )

    # Si hubo algún error al agendar, se lo informo al cliente
    if error:
        await query.edit_message_text(
            f"No se pudo agendar: {error}\n\nEscribe /agendar para intentar de nuevo."
        )
        return ConversationHandler.END

    # Todo bien — le doy el código al cliente para que pueda gestionar su cita
    await query.edit_message_text(
        f"*¡Cita confirmada!*\n\n"
        f"Tu código es: `{codigo}`\n\n"
        f"Guarda este código — lo necesitas para cancelar o reprogramar.\n"
        f"Usa /micita para consultar tus detalles en cualquier momento.",
        parse_mode="Markdown",
    )
    return ConversationHandler.END


async def salir_flujo(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Cancela el flujo actual cuando el usuario escribe /salir."""
    await update.message.reply_text(
        "Operación cancelada. Escribe /start para ver los comandos."
    )
    return ConversationHandler.END


# ── /cancelar ─────────────────────────────────────────────────────────────────

async def cancelar_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Inicia el flujo de cancelación — pide el código de la cita."""
    await update.message.reply_text("Indica el código de tu cita para cancelarla:")
    return CODIGO_CANCELAR


async def codigo_cancelar_recibido(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Recibe el código y cancela la cita si existe."""
    codigo = update.message.text.strip().upper()
    if cancelar_cita(codigo):
        await update.message.reply_text(f"Cita {codigo} cancelada correctamente.")
    else:
        await update.message.reply_text(
            "No se encontró esa cita, o ya estaba completada o cancelada."
        )
    return ConversationHandler.END


# ── /reprogramar ──────────────────────────────────────────────────────────────

async def reprogramar_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Inicia el flujo de reprogramación — pide el código de la cita."""
    ctx.user_data.clear()
    await update.message.reply_text("Indica el código de la cita a reprogramar:")
    return CODIGO_REPROG


async def codigo_reprog_recibido(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Verifica que la cita exista y esté en estado reprogramable, luego pide la nueva fecha."""
    codigo = update.message.text.strip().upper()
    cita   = obtener_cita(codigo)

    if not cita:
        await update.message.reply_text("No se encontró esa cita. Verifica el código.")
        return ConversationHandler.END

    # No permito reprogramar citas ya completadas o canceladas
    if cita.get("estado") in ("completada", "cancelada"):
        await update.message.reply_text(
            f"No se puede reprogramar: la cita está '{cita['estado']}'."
        )
        return ConversationHandler.END

    # Guardo los datos que necesito para los siguientes pasos
    ctx.user_data["codigo"]      = codigo
    ctx.user_data["empleado_id"] = cita.get("empleado_id")

    await update.message.reply_text(
        f"Cita encontrada:\n"
        f"Servicio:     {cita.get('servicio')}\n"
        f"Fecha actual: {cita.get('fecha')}\n"
        f"Hora actual:  {str(cita.get('hora', ''))[:5]}\n\n"
        "¿Para qué nueva fecha la reprogramamos? (AAAA-MM-DD)"
    )
    return FECHA_REPROG


async def fecha_reprog_recibida(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Valida la nueva fecha y muestra las horas disponibles para reprogramar."""
    texto_fecha = update.message.text.strip()

    # Valido el formato de la fecha
    try:
        fecha_obj = datetime.strptime(texto_fecha, "%Y-%m-%d").date()
    except ValueError:
        await update.message.reply_text("Formato incorrecto. Usa AAAA-MM-DD:")
        return FECHA_REPROG

    if fecha_obj < date.today():
        await update.message.reply_text("La fecha no puede ser en el pasado:")
        return FECHA_REPROG

    ctx.user_data["nueva_fecha"] = texto_fecha
    horas = horarios_disponibles(texto_fecha, ctx.user_data.get("empleado_id"))

    if not horas:
        await update.message.reply_text(
            f"No hay horas disponibles para el {texto_fecha}. Intenta con otra fecha:"
        )
        return FECHA_REPROG

    await update.message.reply_text(
        f"Horas disponibles para el {texto_fecha}:",
        reply_markup=InlineKeyboardMarkup(_botones_horas(horas)),
    )
    return HORA_REPROG


async def hora_reprog_recibida(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Guarda la nueva hora y reprograma la cita en la BD."""
    query = update.callback_query
    await query.answer()

    # Llamo al servicio para reprogramar con la nueva fecha y hora
    exito = reprogramar_cita(
        ctx.user_data["codigo"],
        ctx.user_data["nueva_fecha"],
        query.data,
    )

    if exito:
        await query.edit_message_text(
            f"Cita {ctx.user_data['codigo']} reprogramada.\n"
            f"Nueva fecha: {ctx.user_data['nueva_fecha']}\n"
            f"Nueva hora:  {query.data}"
        )
    else:
        await query.edit_message_text(
            "No se pudo reprogramar. Escribe /reprogramar e intenta de nuevo."
        )
    return ConversationHandler.END


# ── /micita ───────────────────────────────────────────────────────────────────

async def micita_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Inicia el flujo de consulta de cita — pide el código."""
    await update.message.reply_text("Ingresa el código de tu cita:")
    return CODIGO_MICITA


async def codigo_micita_recibido(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Busca la cita por código y muestra sus detalles al cliente."""
    codigo = update.message.text.strip().upper()
    cita   = obtener_cita(codigo)

    if not cita:
        await update.message.reply_text("No se encontró ninguna cita con ese código.")
        return ConversationHandler.END

    # Convierto los estados técnicos a textos más amigables para el cliente
    etiquetas = {
        "pendiente":  "Pendiente de confirmación",
        "confirmada": "Confirmada",
        "en_curso":   "En servicio ahora",
        "completada": "Completada",
        "cancelada":  "Cancelada",
    }
    estado_txt = etiquetas.get(cita.get("estado", ""), cita.get("estado", ""))

    await update.message.reply_text(
        f"*Código:*   `{codigo}`\n"
        f"*Servicio:* {cita.get('servicio')}\n"
        f"*Fecha:*    {cita.get('fecha')}\n"
        f"*Hora:*     {str(cita.get('hora', ''))[:5]}\n"
        f"*Estado:*   {estado_txt}",
        parse_mode="Markdown",
    )
    return ConversationHandler.END
