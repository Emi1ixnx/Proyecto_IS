"""Utilidades comunes para las pruebas: base de datos temporal y datos de ejemplo."""
import os
import tempfile
import unittest

# La app lee ASISTENCIA_DB al importarse, así que se define antes de importarla.
os.environ["ASISTENCIA_DB"] = os.path.join(tempfile.mkdtemp(), "pruebas.db")

import db  # noqa: E402
from app import app  # noqa: E402


class BaseTest(unittest.TestCase):
    """Cada prueba empieza con la base de datos vacía."""

    def setUp(self):
        app.config.update(TESTING=True)
        with app.app_context():
            conexion = db.get_db()
            conexion.executescript(
                "DELETE FROM asistencia; DELETE FROM alumno; DELETE FROM materia;"
            )
            conexion.commit()
        self.client = app.test_client()

    def texto(self, respuesta):
        return respuesta.get_data(as_text=True)

    def contar(self, tabla):
        with app.app_context():
            return db.get_db().execute(f"SELECT COUNT(*) FROM {tabla}").fetchone()[0]

    def crear_materia(self, nombre="Algoritmos", dias="0,2,4", inicio=None, fin=None):
        """Crea una materia (por defecto lunes, miércoles y viernes) y devuelve su id."""
        with app.app_context():
            return db.guardar_materia(nombre, dias, inicio, fin)

    def crear_alumno(self, id_materia, cuenta="1001", nombre="Ana", correo="ana@aragon.unam.mx"):
        with app.app_context():
            return db.guardar_alumno(id_materia, cuenta, nombre, correo)
