"""HU06-T03: pruebas del resumen de asistencia (asistencias y faltas por alumno)."""
from app import app
import db
from tests.base import BaseTest


class TestResumenDeAsistencia(BaseTest):
    def setUp(self):
        super().setUp()
        self.materia = self.crear_materia("Algoritmos", dias="0,2,4")
        self.ana = self.crear_alumno(self.materia, "1001", "Ana Perez")
        self.beto = self.crear_alumno(self.materia, "1002", "Beto Lopez")
        self.registrar_lista(self.materia, "2026-11-16", {self.ana: "Presente", self.beto: "Presente"})
        self.registrar_lista(self.materia, "2026-11-18", {self.ana: "Presente", self.beto: "Ausente"})
        self.registrar_lista(self.materia, "2026-11-20", {self.ana: "Ausente", self.beto: "Ausente"})

    def resumen(self):
        with app.app_context():
            filas, total = db.resumen_materia(self.materia)
        return {f["nombre"]: f for f in filas}, total

    def test_cuenta_asistencias_y_faltas_de_cada_alumno(self):
        filas, _ = self.resumen()
        self.assertEqual((filas["Ana Perez"]["asistencias"], filas["Ana Perez"]["faltas"]), (2, 1))
        self.assertEqual((filas["Beto Lopez"]["asistencias"], filas["Beto Lopez"]["faltas"]), (1, 2))

    def test_cuenta_las_listas_registradas_de_la_materia(self):
        _, total = self.resumen()
        self.assertEqual(total, 3)

    def test_un_alumno_sin_registros_aparece_con_ceros(self):
        self.crear_alumno(self.materia, "1003", "Carla Ruiz")
        filas, _ = self.resumen()
        self.assertEqual((filas["Carla Ruiz"]["asistencias"], filas["Carla Ruiz"]["faltas"]), (0, 0))

    def test_no_mezcla_alumnos_ni_listas_de_otra_materia(self):
        otra = self.crear_materia("Bases de datos", dias="0")
        luis = self.crear_alumno(otra, "3003", "Luis Ruiz")
        self.registrar_lista(otra, "2026-11-16", {luis: "Presente"})
        filas, total = self.resumen()
        self.assertNotIn("Luis Ruiz", filas)
        self.assertEqual(total, 3)

    def test_la_ruta_resumen_muestra_los_alumnos_de_la_materia(self):
        html = self.texto(self.client.get(f"/resumen?materia={self.materia}"))
        self.assertIn("Ana Perez", html)
        self.assertIn("Beto Lopez", html)
        self.assertIn("Asistencias", html)
        self.assertIn("Faltas", html)

    def test_la_ruta_resumen_sin_materia_solo_muestra_el_selector(self):
        respuesta = self.client.get("/resumen")
        self.assertEqual(respuesta.status_code, 200)
        self.assertNotIn("Ana Perez", self.texto(respuesta))

    def test_la_ruta_resumen_con_materia_inexistente_no_falla(self):
        self.assertEqual(self.client.get("/resumen?materia=999").status_code, 200)
