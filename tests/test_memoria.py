import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from memoria import (  # noqa: E402
    ErrorMemoria, GestorMemoriaContigua, GestorPaginacion, SegmentationFault,
)
from procesos import Proceso  # noqa: E402


class TestContigua(unittest.TestCase):
    def test_fragmentacion_externa(self):
        m = GestorMemoriaContigua(100)
        for pid in (1, 2, 3, 4):
            m.asignar(pid, 25)
        m.liberar(1)
        m.liberar(3)  # dos huecos de 25 no adyacentes
        self.assertEqual(m.libre_total(), 50)
        self.assertEqual(m.hueco_mayor(), 25)
        self.assertEqual(m.fragmentacion_externa(), 25)
        with self.assertRaisesRegex(ErrorMemoria, "fragmentación externa"):
            m.asignar(5, 40)

    def test_fusion_de_huecos_adyacentes(self):
        m = GestorMemoriaContigua(100)
        m.asignar(1, 30)
        m.asignar(2, 30)
        m.liberar(1)
        m.liberar(2)
        self.assertEqual(len(m.bloques), 1)
        self.assertEqual(m.hueco_mayor(), 100)

    def test_estrategias(self):
        def preparar(estrategia):
            m = GestorMemoriaContigua(100, estrategia)
            m.asignar(1, 10); m.asignar(2, 20); m.asignar(3, 10)  # noqa: E702
            m.asignar(4, 40); m.asignar(5, 10)  # noqa: E702
            m.liberar(2)  # hueco de 20 en [10,30)
            m.liberar(4)  # hueco de 40 en [40,80); resto libre 10 al final
            return m
        self.assertEqual(preparar("first").asignar(9, 8), 10)
        self.assertEqual(preparar("best").asignar(9, 8), 90)   # hueco más ajustado (10)
        self.assertEqual(preparar("worst").asignar(9, 8), 40)  # hueco mayor

    def test_errores(self):
        m = GestorMemoriaContigua(50)
        m.asignar(1, 10)
        with self.assertRaises(ErrorMemoria):
            m.asignar(1, 5)
        with self.assertRaises(ErrorMemoria):
            m.asignar(2, 100)
        with self.assertRaises(ErrorMemoria):
            m.liberar(99)
        with self.assertRaises(ValueError):
            GestorMemoriaContigua(10, "next")


class TestPaginacion(unittest.TestCase):
    def setUp(self):
        self.g = GestorPaginacion(num_marcos=8, tam_pagina=100)

    def test_traduccion(self):
        self.g.asignar(1, 250)           # 3 páginas -> marcos 0,1,2
        self.g.asignar(2, 100)           # marco 3
        self.g.liberar(1)
        t = self.g.asignar(3, 250)       # reutiliza marcos 0,1,2 (no hace falta contigüidad)
        self.assertEqual(t.marcos, [0, 1, 2])
        self.assertEqual(self.g.traducir_direccion(3, 0), 0)
        self.assertEqual(self.g.traducir_direccion(3, 149), 149)
        self.assertEqual(self.g.traducir_direccion(2, 42), 342)

    def test_traduccion_no_contigua(self):
        self.g.asignar(1, 100)
        self.g.asignar(2, 100)
        self.g.asignar(3, 100)
        self.g.liberar(2)
        t = self.g.asignar(4, 250)       # marcos libres: 1, 3, 4
        self.assertEqual(t.marcos, [1, 3, 4])
        self.assertEqual(self.g.traducir_direccion(4, 120), 3 * 100 + 20)

    def test_acepta_objeto_proceso(self):
        self.g.asignar(7, 50)
        self.assertEqual(self.g.traducir_direccion(Proceso(7, "x"), 10), 10)

    def test_segmentation_fault(self):
        self.g.asignar(1, 250)
        for virtual in (250, -1, 10_000):
            with self.assertRaises(SegmentationFault):
                self.g.traducir_direccion(1, virtual)
        with self.assertRaises(SegmentationFault):
            self.g.traducir_direccion(42, 0)

    def test_fragmentacion_interna_y_capacidad(self):
        self.g.asignar(1, 250)
        self.assertEqual(self.g.fragmentacion_interna(1), 50)
        with self.assertRaises(ErrorMemoria):
            self.g.asignar(2, 600)       # necesita 6 marcos, quedan 5
        self.assertEqual(self.g.marcos_libres(), 5)  # el intento fallido no reservó nada

    def test_liberar_y_errores(self):
        self.g.asignar(1, 300)
        self.g.liberar(1)
        self.assertEqual(self.g.marcos_libres(), 8)
        with self.assertRaises(ErrorMemoria):
            self.g.liberar(1)
        with self.assertRaises(ValueError):
            GestorPaginacion(0, 10)


class TestUnidades(unittest.TestCase):
    def test_mapas_indican_bytes(self):
        self.assertIn("1000 B", GestorMemoriaContigua(1000).mapa_texto())
        self.assertIn("B = bytes", GestorMemoriaContigua(1000).mapa_texto())
        self.assertIn("256 B", GestorPaginacion(4, 256).mapa_texto())


if __name__ == "__main__":
    unittest.main()
