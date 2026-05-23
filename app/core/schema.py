# SQL para crear las tablas de la base de datos

CREATE_TABLES = """

CREATE TABLE IF NOT EXISTS empleados (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre              TEXT    NOT NULL,
    telefono            TEXT,
    especialidad        TEXT    DEFAULT 'Corte de cabello',
    porcentaje_ganancia REAL    DEFAULT 60.0,
    activo              INTEGER DEFAULT 1,
    fecha_creacion      TEXT    DEFAULT (date('now'))
);

CREATE TABLE IF NOT EXISTS usuarios (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre          TEXT    NOT NULL,
    correo          TEXT    UNIQUE NOT NULL,
    contrasena_hash TEXT    NOT NULL,
    rol             TEXT    NOT NULL CHECK(rol IN ('administrador','recepcionista')),
    telefono        TEXT,
    activo          INTEGER DEFAULT 1,
    totp_secret     TEXT    DEFAULT NULL,
    fecha_creacion  TEXT    DEFAULT (date('now'))
);

CREATE TABLE IF NOT EXISTS clientes (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre         TEXT    NOT NULL,
    cedula         TEXT    UNIQUE,
    telefono       TEXT,
    correo         TEXT,
    fecha_creacion TEXT    DEFAULT (date('now'))
);

CREATE TABLE IF NOT EXISTS servicios (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre           TEXT    NOT NULL,
    descripcion      TEXT,
    precio           REAL    NOT NULL,
    duracion_minutos INTEGER DEFAULT 30,
    activo           INTEGER DEFAULT 1
);

-- Estado: pendiente, confirmada, en_curso, completada, cancelada
CREATE TABLE IF NOT EXISTS citas (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id     INTEGER NOT NULL REFERENCES clientes(id),
    empleado_id    INTEGER NOT NULL REFERENCES empleados(id),
    servicio_id    INTEGER NOT NULL REFERENCES servicios(id),
    fecha          TEXT    NOT NULL,
    hora           TEXT    NOT NULL,
    estado         TEXT    DEFAULT 'pendiente',
    observaciones  TEXT,
    codigo         TEXT    UNIQUE NOT NULL,
    fecha_creacion TEXT    DEFAULT (date('now'))
);

CREATE TABLE IF NOT EXISTS pagos (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    cita_id           INTEGER UNIQUE NOT NULL REFERENCES citas(id),
    monto             REAL    NOT NULL,
    metodo            TEXT    NOT NULL,
    fecha             TEXT    NOT NULL,
    estado            TEXT    DEFAULT 'pagado',
    observaciones     TEXT,
    ganancia_empleado REAL    DEFAULT 0.0,
    ganancia_negocio  REAL    DEFAULT 0.0
);

CREATE TABLE IF NOT EXISTS facturas (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    pago_id        INTEGER UNIQUE NOT NULL REFERENCES pagos(id),
    numero_factura TEXT    UNIQUE NOT NULL,
    fecha_emision  TEXT    DEFAULT (date('now')),
    detalle        TEXT
);

CREATE TABLE IF NOT EXISTS gastos (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id     INTEGER REFERENCES usuarios(id),
    descripcion    TEXT    NOT NULL,
    categoria      TEXT    NOT NULL,
    monto          REAL    NOT NULL,
    fecha_gasto    TEXT    NOT NULL,
    fecha_creacion TEXT    DEFAULT (date('now'))
);

CREATE TABLE IF NOT EXISTS configuracion (
    clave TEXT PRIMARY KEY,
    valor TEXT NOT NULL
);

"""
