"""HU02-T05: pruebas de la carga de alumnos."""
from app import app
import db
from tests.base import BaseTest


class TestCargaDeAlumnos(BaseTest):
    def capturar(self, id_materia, cuenta="1001", nombre="Ana", correo="ana@aragon.unam.mx"):
        return self.client.post(
            "/alumnos",
            data={"id_materia": id_materia, "numero_cuenta": cuenta, "nombre": nombre, "correo": correo},
            follow_redirects=True,
        )

    def test_guarda_el_alumno_asociado_a_su_materia(self):
        id_materia = self.crear_materia()
        respuesta = self.capturar(id_materia)
        self.assertIn("Alumno guardado correctamente.", self.texto(respuesta))
        with app.app_context():
            alumno = db.get_db().execute("SELECT * FROM alumno").fetchone()
        self.assertEqual(alumno["numero_cuenta"], "1001")
        self.assertEqual(alumno["id_materia"], id_materia)

    def test_numero_de_cuenta_nombre_y_correo_son_obligatorios(self):
        id_materia = self.crear_materia()
        self.assertIn("El número de cuenta es obligatorio.", self.texto(self.capturar(id_materia, cuenta="")))
        self.assertIn("El nombre del alumno es obligatorio.", self.texto(self.capturar(id_materia, nombre=" ")))
        self.assertIn("El correo del alumno es obligatorio.", self.texto(self.capturar(id_materia, correo="")))
        self.assertEqual(self.contar("alumno"), 0)

    def test_correo_sin_arroba_se_rechaza(self):
        id_materia = self.crear_materia()
        respuesta = self.capturar(id_materia, correo="ana.aragon.unam.mx")
        self.assertIn("El correo no es válido.", self.texto(respuesta))
        self.assertEqual(self.contar("alumno"), 0)

    def test_hay_que_elegir_una_materia_registrada(self):
        respuesta = self.capturar("999")
        self.assertIn("Selecciona una materia registrada.", self.texto(respuesta))
        self.assertEqual(self.contar("alumno"), 0)

    def test_el_numero_de_cuenta_no_se_repite_en_la_misma_materia(self):
        id_materia = self.crear_materia()
        self.capturar(id_materia, cuenta="1001", nombre="Ana")
        respuesta = self.capturar(id_materia, cuenta="1001", nombre="Beto")
        self.assertIn("ya está registrado en esta materia", self.texto(respuesta))
        self.assertEqual(self.contar("alumno"), 1)

    def test_el_mismo_numero_de_cuenta_se_permite_en_otra_materia(self):
        algoritmos = self.crear_materia("Algoritmos")
        bases = self.crear_materia("Bases de datos")
        self.capturar(algoritmos, cuenta="1001")
        self.capturar(bases, cuenta="1001")
        self.assertEqual(self.contar("alumno"), 2)

    def test_la_tabla_muestra_solo_los_alumnos_de_la_materia(self):
        algoritmos = self.crear_materia("Algoritmos")
        bases = self.crear_materia("Bases de datos")
        self.crear_alumno(algoritmos, "1001", "Ana Perez")
        self.crear_alumno(bases, "2002", "Beto Lopez")
        html = self.texto(self.client.get(f"/alumnos?materia={algoritmos}"))
        self.assertIn("Ana Perez", html)
        self.assertNotIn("Beto Lopez", html)
