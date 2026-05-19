from datetime import datetime, timedelta
from app.models.cita_model import CitaModel
from app.models.cliente_model import ClienteModel
from app.models.empleado_model import EmpleadoModel
from app.models.servicio_model import ServicioModel
from app.config import HORARIO_INICIO, HORARIO_FIN

modelo_cita = CitaModel()
modelo_cliente = ClienteModel()
modelo_emp = EmpleadoModel()
modelo_servicio = ServicioModel()


def obtener_empleados():
    return modelo_emp.listar()


def obtener_servicios():
    return modelo_servicio.listar(solo_activos=True)


def todas_las_horas():
    inicio = datetime.strptime(HORARIO_INICIO, "%H:%M")
    fin = datetime.strptime(HORARIO_FIN, "%H:%M")
    horas = []
    h = inicio
    while h < fin:
        horas.append(h.strftime("%H:%M"))
        h += timedelta(minutes=30)
    return horas


def horarios_disponibles(fecha, empleado_id):
    return modelo_cita.horarios_disponibles(fecha, empleado_id)


def horarios_disponibles_cualquiera(fecha):
    empleados = modelo_emp.listar()
    if not empleados:
        return []

    disponibles = []
    for hora in todas_las_horas():
        for emp in empleados:
            libres = modelo_cita.horarios_disponibles(fecha, emp["id"])
            if hora in libres:
                disponibles.append(hora)
                break

    return disponibles


def primer_barbero_libre(fecha, hora):
    for emp in modelo_emp.listar():
        if hora in modelo_cita.horarios_disponibles(fecha, emp["id"]):
            return emp["id"], emp["nombre"]
    return None, None


def agendar_cita(nombre, cedula, telefono, servicio_id, fecha, hora, empleado_id=None, confirmar=False):
    cliente_id = modelo_cliente.obtener_o_crear(nombre, cedula, telefono)

    if not empleado_id:
        empleado_id, _ = primer_barbero_libre(fecha, hora)
        if not empleado_id:
            return None, "No hay barberos disponibles en ese horario."

    horas_libres = modelo_cita.horarios_disponibles(fecha, empleado_id)
    if hora not in horas_libres:
        if horas_libres:
            sugerencias = ", ".join(horas_libres[:3])
        else:
            sugerencias = "ninguna"
        return None, f"Esa hora ya fue tomada. Opciones: {sugerencias}"

    # Las citas del chatbot se crean directamente como confirmadas porque el
    # cliente ya paso por el flujo completo de confirmacion en Telegram
    estado = "confirmada" if confirmar else "pendiente"
    codigo = modelo_cita.crear(cliente_id, empleado_id, servicio_id, fecha, hora, estado=estado)
    return codigo, None


def cancelar_cita(codigo):
    return modelo_cita.cancelar(codigo)


def reprogramar_cita(codigo, nueva_fecha, nueva_hora):
    return modelo_cita.reprogramar(codigo, nueva_fecha, nueva_hora)


def obtener_cita(codigo):
    return modelo_cita.obtener_por_codigo(codigo)
