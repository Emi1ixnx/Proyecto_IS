"""Sistema de Control de Asistencia de Alumnos (versión 1.0).

Aplicación web con Flask y SQLite: el profesor registra materias y alumnos,
pasa lista por fecha y consulta el resumen de asistencia.
"""

import os
from datetime import date

from flask import Flask, flash, redirect, render_template, request, url_for

import db

app = Flask(__name__)
app.config["SECRET_KEY"] = "cambia-esta-clave"  # necesaria para flash()
app.config["DATABASE"] = os.environ.get(
    "ASISTENCIA_DB", os.path.join(app.root_path, "asistencia.db")
)
db.init_app(app)
app.add_template_filter(db.dias_legibles, "dias_legibles")


@app.route("/")
def index():
    return render_template("base.html")


# ---------------------------------------------------------------- Materias (HU01)
def validar_materia(datos):
    """RN01 y RN02. Devuelve la lista de errores (vacía si todo está bien)."""
    errores = []
    if not datos["nombre"]:
        errores.append("El nombre de la materia es obligatorio.")
    if not datos["dias"]:
        errores.append("Selecciona al menos un día de clase.")

    fechas = {}
    for campo, etiqueta in (("fecha_inicio", "inicio"), ("fecha_fin", "término")):
        if datos[campo]:
            try:
                fechas[campo] = date.fromisoformat(datos[campo])
            except ValueError:
                errores.append(f"La fecha de {etiqueta} no es válida.")
    if len(fechas) == 2 and fechas["fecha_inicio"] > fechas["fecha_fin"]:
        errores.append("La fecha de inicio no puede ser posterior a la de término.")
    return errores


@app.route("/materias", methods=["GET", "POST"])
def materias():
    datos = {"nombre": "", "dias": [], "fecha_inicio": "", "fecha_fin": ""}
    if request.method == "POST":
        datos = {
            "nombre": request.form.get("nombre", "").strip(),
            "dias": [d for d in request.form.getlist("dias") if d in db.VALORES_DIAS],
            "fecha_inicio": request.form.get("fecha_inicio", "").strip(),
            "fecha_fin": request.form.get("fecha_fin", "").strip(),
        }
        errores = validar_materia(datos)
        if not errores:
            db.guardar_materia(
                datos["nombre"],
                db.dias_a_texto(datos["dias"]),
                datos["fecha_inicio"] or None,
                datos["fecha_fin"] or None,
            )
            flash("Materia registrada correctamente.", "success")
            return redirect(url_for("materias"))
        for error in errores:
            flash(error, "danger")
    return render_template(
        "materias.html",
        materias=db.listar_materias(),
        datos=datos,
        dias_semana=db.DIAS_SEMANA,
    )


# ---------------------------------------------------------------- Alumnos (HU02)
@app.route("/alumnos", methods=["GET", "POST"])
def alumnos():
    if request.method == "POST":
        db.guardar_alumno(
            request.form.get("id_materia", ""),
            request.form.get("numero_cuenta", "").strip(),
            request.form.get("nombre", "").strip(),
            request.form.get("correo", "").strip(),
        )
        flash("Alumno guardado correctamente.", "success")
        return redirect(url_for("alumnos"))
    return render_template("alumnos.html", materias=db.listar_materias(), datos={})


# ------------------------------------------------- Asistencia (HU03, HU04, HU05)
def formatear_fecha(texto):
    """'2026-11-16' -> '16/11/2026'."""
    return date.fromisoformat(texto).strftime("%d/%m/%Y")


def validar_dia_de_clase(materia, fecha_texto):
    """RN05. Devuelve un mensaje de error, o None si se puede pasar lista."""
    if materia is None:
        return "Selecciona una materia registrada."
    try:
        fecha = date.fromisoformat(fecha_texto)
        if fecha.isoformat() != fecha_texto:
            raise ValueError
    except ValueError:
        return "Selecciona una fecha válida."

    if fecha.weekday() not in db.texto_a_dias(materia["dias_clase"]):
        return (
            f"El {formatear_fecha(fecha_texto)} no es día de clase de {materia['nombre']}. "
            f"Se imparte: {db.dias_legibles(materia['dias_clase'])}."
        )
    if materia["fecha_inicio"] and fecha_texto < materia["fecha_inicio"]:
        return (
            f"{materia['nombre']} inicia el {formatear_fecha(materia['fecha_inicio'])}; "
            "esa fecha es anterior."
        )
    if materia["fecha_fin"] and fecha_texto > materia["fecha_fin"]:
        return (
            f"{materia['nombre']} termina el {formatear_fecha(materia['fecha_fin'])}; "
            "esa fecha es posterior."
        )
    return None


@app.route("/pasar-lista", methods=["GET", "POST"])
def pasar_lista():
    """Elegir la materia y la fecha de la lista y validar que sea día de clase."""
    id_materia = fecha = ""
    error = None
    if request.method == "POST":
        id_materia = request.form.get("id_materia", "").strip()
        fecha = request.form.get("fecha", "").strip()
        materia = db.obtener_materia(id_materia)
        error = validar_dia_de_clase(materia, fecha)
    return render_template(
        "pasar_lista.html",
        materias=db.listar_materias(),
        id_materia=id_materia,
        fecha=fecha,
        error=error,
    )


if __name__ == "__main__":
    app.run(debug=True)
