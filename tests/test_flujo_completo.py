"""HU07-T03: prueba final de la versión 1 (flujo completo por la interfaz web).

Calendario usado (2026): lunes 16, miércoles 18 y viernes 20 de noviembre.
"""
import unittest

from app import app
import db
from tests.base import BaseTest


class TestPorcentaje(unittest.TestCase):
    def test_formula_de_la_regla_rn08(self):
        self.assertEqual(db.calcular_porcentaje(3, 3), 100.0)
        self.assertEqual(db.calcular_porcentaje(2, 3), 66.7)
        self.assertEqual(db.calcular_porcentaje(1, 3), 33.3)
        self.assertEqual(db.calcular_porcentaje(0, 3), 0.0)

    def test_sin_listas_el_porcentaje_es_cero_y_no_hay_division_entre_cero(self):
        self.assertEqual(db.calcular_porcentaje(0, 0), 0.0)


class TestFlujoCompleto(BaseTest):
    def test_registrar_materia_capturar_alumnos_pasar_lista_y_ver_resultados(self):
        c = self.client

        # HU01: registrar la materia (lunes, miércoles y viernes)
        r = c.post("/materias", data={"nombre": "Algoritmos", "dias": ["0", "2", "4"]}, follow_redirects=True)
        self.assertIn("Materia registrada correctamente.", self.texto(r))
        with app.app_context():
            id_materia = db.listar_materias()[0]["id_materia"]

        # HU02: capturar tres alumnos
        for cuenta, nombre in (("1001", "Ana Perez"), ("1002", "Beto Lopez"), ("1003", "Carla Ruiz")):
            r = c.post(
                "/alumnos",
                data={"id_materia": id_materia, "numero_cuenta": cuenta, "nombre": nombre, "correo": f"{cuenta}@aragon.unam.mx"},
                follow_redirects=True,
            )
            self.assertIn("Alumno guardado correctamente.", self.texto(r))
        with app.app_context():
            ids = {a["nombre"]: a["id_alumno"] for a in db.listar_alumnos(id_materia)}

        # HU03 + HU04: un martes no se puede pasar lista
        r = c.post("/pasar-lista", data={"id_materia": id_materia, "fecha": "2026-11-17"})
        self.assertIn("no es día de clase", self.texto(r))

        # HU05: tres listas (Ana asiste siempre, Beto dos veces, Carla una vez)
        asistencias = {
            "2026-11-16": {"Ana Perez": "Presente", "Beto Lopez": "Presente", "Carla Ruiz": "Presente"},
            "2026-11-18": {"Ana Perez": "Presente", "Beto Lopez": "Presente", "Carla Ruiz": "Ausente"},
            "2026-11-20": {"Ana Perez": "Presente", "Beto Lopez": "Ausente", "Carla Ruiz": "Ausente"},
        }
        for fecha, estados in asistencias.items():
            r = c.post("/pasar-lista", data={"id_materia": id_materia, "fecha": fecha})
            self.assertIn("Guardar asistencia", self.texto(r))
            datos = {"id_materia": id_materia, "fecha": fecha}
            datos.update({f"estado_{ids[nombre]}": estado for nombre, estado in estados.items()})
            r = c.post("/pasar-lista/guardar", data=datos, follow_redirects=True)
            self.assertIn("guardada (3 alumnos)", self.texto(r))

        # HU05: no se repite la lista de una fecha
        r = c.post("/pasar-lista", data={"id_materia": id_materia, "fecha": "2026-11-16"})
        self.assertIn("Ya se pasó lista", self.texto(r))
        self.assertEqual(self.contar("asistencia"), 9)

        # HU06 + HU07: resumen con porcentajes
        html = self.texto(c.get(f"/resumen?materia={id_materia}"))
        self.assertIn("Listas registradas:", html)
        for esperado in ("Ana Perez", "100.0%", "Beto Lopez", "66.7%", "Carla Ruiz", "33.3%"):
            self.assertIn(esperado, html)

        with app.app_context():
            filas, total = db.resumen_materia(id_materia)
        por_nombre = {f["nombre"]: f for f in filas}
        self.assertEqual(total, 3)
        self.assertEqual(
            (por_nombre["Beto Lopez"]["asistencias"], por_nombre["Beto Lopez"]["faltas"], por_nombre["Beto Lopez"]["porcentaje"]),
            (2, 1, 66.7),
        )

    def test_las_paginas_principales_responden(self):
        for ruta in ("/", "/materias", "/alumnos", "/pasar-lista", "/resumen"):
            self.assertEqual(self.client.get(ruta).status_code, 200, ruta)


if __name__ == "__main__":
    unittest.main()
