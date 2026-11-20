"""HU05-T05: pruebas del pase de lista.

Materia de prueba: lunes, miércoles y viernes. 16/nov/2026 es lunes y 17/nov es martes.
"""
from app import app
import db
from tests.base import BaseTest


class TestPasarLista(BaseTest):
    def setUp(self):
        super().setUp()
        self.materia = self.crear_materia("Algoritmos", dias="0,2,4")
        self.ana = self.crear_alumno(self.materia, "1001", "Ana Perez")
        self.beto = self.crear_alumno(self.materia, "1002", "Beto Lopez")

    def elegir(self, fecha="2026-11-16", id_materia=None):
        return self.client.post(
            "/pasar-lista",
            data={"id_materia": id_materia or self.materia, "fecha": fecha},
        )

    def guardar(self, fecha="2026-11-16", estados=None):
        estados = estados if estados is not None else {self.ana: "Presente", self.beto: "Ausente"}
        datos = {"id_materia": self.materia, "fecha": fecha}
        datos.update({f"estado_{id_alumno}": estado for id_alumno, estado in estados.items()})
        return self.client.post("/pasar-lista/guardar", data=datos, follow_redirects=True)

    def registros(self):
        with app.app_context():
            return [dict(f) for f in db.get_db().execute(
                "SELECT id_alumno, fecha, estado FROM asistencia ORDER BY id_alumno"
            )]

    def test_en_un_dia_de_clase_se_muestra_la_lista_de_alumnos(self):
        html = self.texto(self.elegir())
        self.assertIn("Ana Perez", html)
        self.assertIn("Beto Lopez", html)
        self.assertIn(f'name="estado_{self.ana}"', html)
        self.assertIn("Guardar asistencia", html)

    def test_en_un_dia_sin_clase_no_se_muestra_la_lista(self):
        html = self.texto(self.elegir("2026-11-17"))
        self.assertIn("no es día de clase", html)
        self.assertNotIn("Guardar asistencia", html)

    def test_materia_sin_alumnos_avisa_y_no_muestra_lista(self):
        vacia = self.crear_materia("Redes", dias="0")
        html = self.texto(self.elegir(id_materia=vacia))
        self.assertIn("aún no tiene alumnos registrados", html)
        self.assertNotIn("Guardar asistencia", html)

    def test_guarda_presente_y_ausente_de_cada_alumno(self):
        respuesta = self.guardar()
        self.assertIn("guardada (2 alumnos)", self.texto(respuesta))
        self.assertEqual(
            self.registros(),
            [
                {"id_alumno": self.ana, "fecha": "2026-11-16", "estado": "Presente"},
                {"id_alumno": self.beto, "fecha": "2026-11-16", "estado": "Ausente"},
            ],
        )

    def test_no_se_guarda_en_un_dia_sin_clase(self):
        respuesta = self.guardar(fecha="2026-11-17")
        self.assertIn("no es día de clase", self.texto(respuesta))
        self.assertEqual(self.registros(), [])

    def test_estado_invalido_no_guarda_nada(self):
        respuesta = self.guardar(estados={self.ana: "Presente", self.beto: "Retardo"})
        self.assertIn("Marca presente o ausente a cada alumno.", self.texto(respuesta))
        self.assertEqual(self.registros(), [])

    def test_falta_marcar_a_un_alumno_no_guarda_nada(self):
        self.guardar(estados={self.ana: "Presente"})
        self.assertEqual(self.registros(), [])

    def test_no_se_puede_pasar_lista_dos_veces_el_mismo_dia(self):
        self.guardar()
        segunda = self.guardar(estados={self.ana: "Ausente", self.beto: "Ausente"})
        self.assertIn("Ya se pasó lista de Algoritmos el 16/11/2026.", self.texto(segunda))
        self.assertEqual(len(self.registros()), 2)
        self.assertEqual(self.registros()[0]["estado"], "Presente")  # la primera se conserva

    def test_al_elegir_una_fecha_ya_registrada_se_avisa(self):
        self.guardar()
        html = self.texto(self.elegir())
        self.assertIn("Ya se pasó lista", html)
        self.assertNotIn("Guardar asistencia", html)

    def test_otra_fecha_de_la_misma_materia_si_se_puede(self):
        self.guardar("2026-11-16")
        self.guardar("2026-11-18")
        self.assertEqual(len(self.registros()), 4)

    def test_la_misma_fecha_en_otra_materia_si_se_puede(self):
        otra = self.crear_materia("Bases de datos", dias="0")
        luis = self.crear_alumno(otra, "3003", "Luis Ruiz")
        self.guardar()
        self.client.post(
            "/pasar-lista/guardar",
            data={"id_materia": otra, "fecha": "2026-11-16", f"estado_{luis}": "Presente"},
        )
        self.assertEqual(len(self.registros()), 3)

    def test_la_base_de_datos_tambien_impide_repetir_la_lista(self):
        with app.app_context():
            self.assertTrue(db.guardar_asistencia(self.materia, "2026-11-16", {self.ana: "Presente"}))
            self.assertFalse(db.guardar_asistencia(self.materia, "2026-11-16", {self.ana: "Ausente"}))
