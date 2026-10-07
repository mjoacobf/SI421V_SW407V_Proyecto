import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from sincronizacion import filosofos, productor_consumidor  # noqa: E402


class TestSincronizacion(unittest.TestCase):
    def test_productor_consumidor_correcto(self):
        for prod, cons, items, cap in [(2, 2, 5, 3), (3, 1, 4, 1), (1, 3, 7, 2), (4, 4, 10, 2)]:
            r = productor_consumidor(prod, cons, items, cap, retardo=0)
            self.assertEqual(len(r.producidos), prod * items)
            self.assertTrue(r.correcto, (prod, cons, items, cap))
            self.assertLessEqual(r.max_ocupacion, cap)

    def test_productor_consumidor_parametros_invalidos(self):
        with self.assertRaises(ValueError):
            productor_consumidor(0, 1, 1, 1)

    def test_filosofos_asimetrico_sin_interbloqueo(self):
        for _ in range(5):
            r = filosofos(asimetrico=True, comidas=3)
            self.assertFalse(r.interbloqueo)
            self.assertEqual(r.comidas, [3] * 5)

    def test_filosofos_ingenuo_se_interbloquea(self):
        r = filosofos(asimetrico=False, espera_max=0.2)
        self.assertTrue(r.interbloqueo)

    def test_filosofos_parametros_invalidos(self):
        with self.assertRaises(ValueError):
            filosofos(n=1)


if __name__ == "__main__":
    unittest.main()
