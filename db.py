"""Conexión a SQLite, creación de tablas y consultas de la aplicación."""

import sqlite3

from flask import current_app, g


# ------------------------------------------------------------------ Conexión
def get_db():
    """Una conexión por petición; las filas se pueden leer por nombre de columna."""
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(error=None):
    conexion = g.pop("db", None)
    if conexion is not None:
        conexion.close()


def init_db():
    """Crea las tablas de schema.sql si todavía no existen."""
    with current_app.open_resource("schema.sql") as archivo:
        get_db().executescript(archivo.read().decode("utf-8"))


def init_app(app):
    app.teardown_appcontext(close_db)
    with app.app_context():
        init_db()


# ------------------------------------------------------------ Días de clase
# Se guardan como números de date.weekday() (0 = lunes ... 5 = sábado) en un
# TEXT separado por comas, por ejemplo "0,2,4". Así la validación compara
# directo con el día de la fecha y no se confunden las dos «M» (martes/miércoles).
DIAS_SEMANA = [
    (0, "L", "Lunes"),
    (1, "M", "Martes"),
    (2, "M", "Miércoles"),
    (3, "J", "Jueves"),
    (4, "V", "Viernes"),
    (5, "S", "Sábado"),
]
VALORES_DIAS = [str(numero) for numero, _, _ in DIAS_SEMANA]


def dias_a_texto(dias):
    """['2', '0', '4'] -> '0,2,4' (listo para guardar en SQLite)."""
    return ",".join(str(d) for d in sorted({int(d) for d in dias}))


def texto_a_dias(texto):
    """'0,2,4' -> [0, 2, 4] (para comparar con date.weekday())."""
    return [int(d) for d in (texto or "").split(",") if d.strip() != ""]


def dias_legibles(texto):
    """'0,2,4' -> 'Lunes, Miércoles, Viernes' (para mostrar en pantalla)."""
    nombres = {numero: nombre for numero, _, nombre in DIAS_SEMANA}
    return ", ".join(nombres[d] for d in texto_a_dias(texto))


# ---------------------------------------------------------------- Materias
def guardar_materia(nombre, dias_clase, fecha_inicio=None, fecha_fin=None):
    conexion = get_db()
    cursor = conexion.execute(
        "INSERT INTO materia (nombre, dias_clase, fecha_inicio, fecha_fin) "
        "VALUES (?, ?, ?, ?)",
        (nombre, dias_clase, fecha_inicio, fecha_fin),
    )
    conexion.commit()
    return cursor.lastrowid


def listar_materias():
    return get_db().execute("SELECT * FROM materia ORDER BY nombre").fetchall()


def obtener_materia(id_materia):
    """Devuelve la materia, o None si no existe o el id no es válido."""
    try:
        id_materia = int(id_materia)
    except (TypeError, ValueError):
        return None
    return get_db().execute(
        "SELECT * FROM materia WHERE id_materia = ?", (id_materia,)
    ).fetchone()


# ----------------------------------------------------------------- Alumnos
def guardar_alumno(id_materia, numero_cuenta, nombre, correo):
    conexion = get_db()
    cursor = conexion.execute(
        "INSERT INTO alumno (numero_cuenta, nombre, correo, id_materia) "
        "VALUES (?, ?, ?, ?)",
        (numero_cuenta, nombre, correo, id_materia),
    )
    conexion.commit()
    return cursor.lastrowid
