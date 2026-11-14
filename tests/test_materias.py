"""HU01-T05: pruebas del registro de materias."""
from app import app
import db
from tests.base import BaseTest


class TestRegistroMaterias(BaseTest):
    def registrar(self, **datos):
        return self.client.post("/materias", data=datos, follow_redirects=True)

    def test_guarda_materia_con_sus_dias(self):
        respuesta = self.registrar(nombre="Algoritmos", dias=["0", "2"])
        self.assertIn("Materia registrada correctamente.", self.texto(respuesta))
        with app.app_context():
            fila = db.get_db().execute("SELECT * FROM materia").fetchone()
        self.assertEqual(fila["nombre"], "Algoritmos")
        self.assertEqual(fila["dias_clase"], "0,2")
        self.assertIsNone(fila["fecha_inicio"])
        self.assertIsNone(fila["fecha_fin"])

    def test_los_dias_se_guardan_ordenados(self):
        self.registrar(nombre="Bases de datos", dias=["4", "0", "2"])
        with app.app_context():
            fila = db.get_db().execute("SELECT dias_clase FROM materia").fetchone()
        self.assertEqual(fila["dias_clase"], "0,2,4")

    def test_el_nombre_es_obligatorio(self):
        respuesta = self.registrar(nombre="   ", dias=["0"])
        self.assertIn("El nombre de la materia es obligatorio.", self.texto(respuesta))
        self.assertEqual(self.contar("materia"), 0)

    def test_se_necesita_al_menos_un_dia(self):
        respuesta = self.registrar(nombre="Algoritmos")
        self.assertIn("Selecciona al menos un día de clase.", self.texto(respuesta))
        self.assertEqual(self.contar("materia"), 0)

    def test_ignora_dias_que_no_existen(self):
        respuesta = self.registrar(nombre="Algoritmos", dias=["9", "x"])
        self.assertIn("Selecciona al menos un día de clase.", self.texto(respuesta))
        self.assertEqual(self.contar("materia"), 0)

    def test_inicio_posterior_al_termino_se_rechaza(self):
        respuesta = self.registrar(
            nombre="Algoritmos", dias=["0"], fecha_inicio="2026-12-01", fecha_fin="2026-08-01"
        )
        self.assertIn("no puede ser posterior", self.texto(respuesta))
        self.assertEqual(self.contar("materia"), 0)

    def test_acepta_fechas_opcionales_validas(self):
        self.registrar(
            nombre="Algoritmos", dias=["0"], fecha_inicio="2026-08-10", fecha_fin="2026-12-04"
        )
        with app.app_context():
            fila = db.get_db().execute("SELECT * FROM materia").fetchone()
        self.assertEqual(fila["fecha_inicio"], "2026-08-10")
        self.assertEqual(fila["fecha_fin"], "2026-12-04")

    def test_fecha_con_formato_invalido_se_rechaza(self):
        respuesta = self.registrar(nombre="Algoritmos", dias=["0"], fecha_inicio="ayer")
        self.assertIn("La fecha de inicio no es válida.", self.texto(respuesta))
        self.assertEqual(self.contar("materia"), 0)

    def test_la_materia_aparece_en_la_lista_con_dias_legibles(self):
        self.registrar(nombre="Algoritmos", dias=["0", "2", "4"])
        html = self.texto(self.client.get("/materias"))
        self.assertIn("Algoritmos", html)
        self.assertIn("Lunes, Miércoles, Viernes", html)
