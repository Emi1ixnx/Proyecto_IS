"""HU04-T04: pruebas con fechas válidas e inválidas.

Referencia de fechas (2026): 16/nov lunes, 17 martes, 18 miércoles, 20 viernes, 21 sábado.
"""
import unittest

from app import validar_dia_de_clase
from tests.base import BaseTest


def materia(dias="0,2,4", inicio=None, fin=None, nombre="Algoritmos"):
    return {"nombre": nombre, "dias_clase": dias, "fecha_inicio": inicio, "fecha_fin": fin}


class TestValidarDiaDeClase(unittest.TestCase):
    def test_un_dia_de_clase_es_valido(self):
        self.assertIsNone(validar_dia_de_clase(materia(), "2026-11-16"))  # lunes
        self.assertIsNone(validar_dia_de_clase(materia(), "2026-11-18"))  # miércoles
        self.assertIsNone(validar_dia_de_clase(materia(), "2026-11-20"))  # viernes

    def test_un_dia_sin_clase_es_invalido(self):
        error = validar_dia_de_clase(materia(), "2026-11-17")  # martes
        self.assertIn("no es día de clase", error)
        self.assertIn("Lunes, Miércoles, Viernes", error)

    def test_martes_y_miercoles_no_se_confunden(self):
        solo_martes = materia(dias="1")
        self.assertIsNone(validar_dia_de_clase(solo_martes, "2026-11-17"))
        self.assertIn("no es día de clase", validar_dia_de_clase(solo_martes, "2026-11-18"))

    def test_el_sabado_es_dia_de_clase_si_se_selecciono(self):
        self.assertIsNone(validar_dia_de_clase(materia(dias="5"), "2026-11-21"))

    def test_el_domingo_nunca_es_dia_de_clase(self):
        self.assertIn("no es día de clase", validar_dia_de_clase(materia(dias="0,1,2,3,4,5"), "2026-11-22"))

    def test_fecha_anterior_al_inicio_de_la_materia(self):
        error = validar_dia_de_clase(materia(inicio="2026-11-18"), "2026-11-16")
        self.assertIn("inicia el 18/11/2026", error)

    def test_fecha_posterior_al_termino_de_la_materia(self):
        error = validar_dia_de_clase(materia(fin="2026-11-18"), "2026-11-20")
        self.assertIn("termina el 18/11/2026", error)

    def test_los_extremos_del_rango_si_son_validos(self):
        rango = materia(inicio="2026-11-16", fin="2026-11-20")
        self.assertIsNone(validar_dia_de_clase(rango, "2026-11-16"))
        self.assertIsNone(validar_dia_de_clase(rango, "2026-11-20"))

    def test_fechas_vacias_o_con_formato_incorrecto(self):
        for texto in ("", "hoy", "16/11/2026", "2026-13-01", "2026-11-31", "20261116"):
            self.assertEqual(validar_dia_de_clase(materia(), texto), "Selecciona una fecha válida.", texto)

    def test_materia_inexistente(self):
        self.assertEqual(validar_dia_de_clase(None, "2026-11-16"), "Selecciona una materia registrada.")


class TestMensajeDeErrorEnPantalla(BaseTest):
    def elegir(self, id_materia, fecha):
        return self.client.post("/pasar-lista", data={"id_materia": id_materia, "fecha": fecha})

    def test_se_muestra_el_error_cuando_no_es_dia_de_clase(self):
        id_materia = self.crear_materia(dias="0,2,4")
        html = self.texto(self.elegir(id_materia, "2026-11-17"))
        self.assertIn("No se puede pasar lista", html)
        self.assertIn("no es día de clase", html)

    def test_no_se_muestra_error_en_un_dia_de_clase(self):
        id_materia = self.crear_materia(dias="0,2,4")
        self.crear_alumno(id_materia)
        html = self.texto(self.elegir(id_materia, "2026-11-16"))
        self.assertNotIn("No se puede pasar lista", html)
