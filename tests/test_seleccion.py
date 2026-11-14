"""HU03-T03: pruebas de la selección de materia y fecha."""
from app import app
import db
from tests.base import BaseTest


class TestSeleccionMateriaYFecha(BaseTest):
    def test_las_materias_aparecen_en_la_lista_desplegable(self):
        self.crear_materia("Algoritmos")
        self.crear_materia("Bases de datos")
        html = self.texto(self.client.get("/pasar-lista"))
        self.assertIn("Algoritmos", html)
        self.assertIn("Bases de datos", html)
        self.assertIn('type="date"', html)

    def test_sin_materias_se_avisa_que_hay_que_registrar_una(self):
        html = self.texto(self.client.get("/pasar-lista"))
        self.assertIn("Primero registra una materia", html)

    def test_materia_y_fecha_elegidas_se_conservan_en_pantalla(self):
        id_materia = self.crear_materia("Algoritmos")
        respuesta = self.client.post(
            "/pasar-lista", data={"id_materia": id_materia, "fecha": "2026-11-16"}
        )
        self.assertEqual(respuesta.status_code, 200)
        html = self.texto(respuesta)
        self.assertIn('value="2026-11-16"', html)
        self.assertIn(f'value="{id_materia}" selected', html)

    def test_una_materia_inexistente_no_rompe_la_pantalla(self):
        respuesta = self.client.post(
            "/pasar-lista", data={"id_materia": "999", "fecha": "2026-11-16"}
        )
        self.assertEqual(respuesta.status_code, 200)

    def test_obtener_materia_regresa_none_con_ids_invalidos(self):
        with app.app_context():
            self.assertIsNone(db.obtener_materia("abc"))
            self.assertIsNone(db.obtener_materia(""))
            self.assertIsNone(db.obtener_materia(None))
            self.assertIsNone(db.obtener_materia(12345))
