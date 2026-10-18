import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from memoria import comparar_reemplazo, reemplazo_paginas  # noqa: E402

# Cadena clásica (Silberschatz): 20 referencias, 3 marcos -> FIFO 15, LRU 12, Óptimo 9.
CLASICA = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]
# Cadena de Belady: FIFO con 4 marcos falla más que con 3.
BELADY = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]


class TestReemplazo(unittest.TestCase):
    def test_cadena_clasica(self):
        r = {x.algoritmo: x.fallos for x in comparar_reemplazo(CLASICA, 3)}
        self.assertEqual(r, {"fifo": 15, "lru": 12, "optimo": 9})

    def test_optimo_es_cota_inferior(self):
        for marcos in range(1, 8):
            f = {x.algoritmo: x.fallos for x in comparar_reemplazo(CLASICA, marcos)}
            self.assertLessEqual(f["optimo"], f["lru"])
            self.assertLessEqual(f["optimo"], f["fifo"])

    def test_anomalia_de_belady_en_fifo(self):
        self.assertEqual(reemplazo_paginas("fifo", BELADY, 3).fallos, 9)
        self.assertEqual(reemplazo_paginas("fifo", BELADY, 4).fallos, 10)

    def test_lru_no_sufre_belady(self):
        self.assertLessEqual(reemplazo_paginas("lru", BELADY, 4).fallos, reemplazo_paginas("lru", BELADY, 3).fallos)

    def test_pasos_y_expulsion(self):
        r = reemplazo_paginas("fifo", [1, 2, 3, 1], 2)
        self.assertEqual([p[2] for p in r.pasos], [None, None, 1, 2])
        self.assertEqual(r.fallos, 4)

    def test_lru_protege_pagina_reciente(self):
        # al reutilizar 1, LRU expulsa 2 (no 1) cuando llega 3
        r = reemplazo_paginas("lru", [1, 2, 1, 3], 2)
        self.assertEqual(r.pasos[-1][2], 2)

    def test_marcos_suficientes_solo_fallos_obligatorios(self):
        for a in ("fifo", "lru", "optimo"):
            self.assertEqual(reemplazo_paginas(a, CLASICA, 8).fallos, 6)

    def test_errores(self):
        with self.assertRaises(ValueError):
            reemplazo_paginas("mru", [1], 2)
        with self.assertRaises(ValueError):
            reemplazo_paginas("fifo", [1], 0)
        with self.assertRaises(ValueError):
            reemplazo_paginas("fifo", [-1], 2)


if __name__ == "__main__":
    unittest.main()
