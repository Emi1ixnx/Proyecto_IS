"""Sistema de Control de Asistencia de Alumnos (versión 1.0).

Aplicación web con Flask y SQLite: el profesor registra materias y alumnos,
pasa lista por fecha y consulta el resumen de asistencia.
"""

import os

from flask import Flask, render_template

import db

app = Flask(__name__)
app.config["SECRET_KEY"] = "cambia-esta-clave"  # necesaria para flash()
app.config["DATABASE"] = os.environ.get(
    "ASISTENCIA_DB", os.path.join(app.root_path, "asistencia.db")
)
db.init_app(app)


@app.route("/")
def index():
    return render_template("base.html")


if __name__ == "__main__":
    app.run(debug=True)
