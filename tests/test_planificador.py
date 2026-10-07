import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from planificador import Planificador  # noqa: E402
from procesos import Proceso  # noqa: E402


def lote(*datos):
    """datos: (rafaga, llegada, prioridad) -> procesos con PID 1..n."""
    return [Proceso(i + 1, f"p{i + 1}", rafaga=r, llegada=l, prioridad=pr)
            for i, (r, l, pr) in enumerate(datos)]


class TestPlanificador(unittest.TestCase):
    def test_fcfs_clasico(self):
        # Ejemplo de libro: ráfagas 24, 3, 3 llegando en t=0 -> espera prom. 17
        r = Planificador(lote((24, 0, 0), (3, 0, 0), (3, 0, 0))).fcfs()
        self.assertEqual([m.espera for m in r.metricas], [0, 24, 27])
        self.assertAlmostEqual(r.espera_promedio, 17.0)
        self.assertEqual(r.gantt, [(1, 0, 24), (2, 24, 27), (3, 27, 30)])

    def test_sjf_reduce_espera_frente_a_fcfs(self):
        plan = Planificador(lote((24, 0, 0), (3, 0, 0), (3, 0, 0)))
        self.assertAlmostEqual(plan.sjf().espera_promedio, 3.0)
        self.assertLess(plan.sjf().espera_promedio, plan.fcfs().espera_promedio)

    def test_round_robin_q4(self):
        # 24,3,3 con q=4 -> esperas 6, 4, 7 (promedio 5.67)
        r = Planificador(lote((24, 0, 0), (3, 0, 0), (3, 0, 0))).round_robin(4)
        self.assertEqual([m.espera for m in r.metricas], [6, 4, 7])
        self.assertEqual([m.respuesta for m in r.metricas], [0, 4, 7])
        self.assertAlmostEqual(r.espera_promedio, 17 / 3)

    def test_round_robin_llegada_antes_de_reencolar(self):
        # p2 llega en t=2, justo cuando p1 agota su quantum: p2 va antes que p1.
        r = Planificador(lote((4, 0, 0), (2, 2, 0))).round_robin(2)
        self.assertEqual([pid for pid, _, _ in r.gantt], [1, 2, 1])

    def test_prioridad(self):
        r = Planificador(lote((5, 0, 3), (5, 0, 1), (5, 0, 2))).prioridad()
        self.assertEqual([pid for pid, _, _ in r.gantt], [2, 3, 1])

    def test_cpu_ociosa_entre_llegadas(self):
        for r in Planificador(lote((2, 0, 0), (2, 10, 0))).todos(2):
            self.assertEqual(r.gantt[-1][2], 12, r.algoritmo)
            self.assertEqual([m.espera for m in r.metricas], [0, 0], r.algoritmo)

    def test_no_muta_los_procesos(self):
        procs = lote((3, 0, 1), (2, 1, 2))
        antes = [(p.rafaga, p.estado, p.pc) for p in procs]
        Planificador(procs).todos(1)
        self.assertEqual(antes, [(p.rafaga, p.estado, p.pc) for p in procs])

    def test_invariantes_en_todos_los_algoritmos(self):
        procs = lote((5, 0, 2), (3, 1, 1), (8, 2, 3), (2, 3, 1), (4, 9, 2))
        for r in Planificador(procs).todos(3):
            ocupado = sum(b - a for _, a, b in r.gantt)
            self.assertEqual(ocupado, sum(p.rafaga for p in procs), r.algoritmo)
            for m in r.metricas:
                self.assertEqual(m.retorno, m.espera + m.rafaga, r.algoritmo)
                self.assertGreaterEqual(m.espera, 0, r.algoritmo)
                self.assertGreaterEqual(m.inicio, m.llegada, r.algoritmo)
            for (_, _, fin), (_, ini, _) in zip(r.gantt, r.gantt[1:]):
                self.assertLessEqual(fin, ini, r.algoritmo)  # sin solapamientos

    def test_errores(self):
        with self.assertRaises(ValueError):
            Planificador([])
        with self.assertRaises(ValueError):
            Planificador(lote((1, 0, 0))).round_robin(0)
        with self.assertRaises(ValueError):
            Planificador(lote((1, 0, 0))).ejecutar("lifo")
        with self.assertRaises(ValueError):
            Proceso(1, "x", rafaga=0)

    def test_reporte_incluye_promedios(self):
        plan = Planificador(lote((3, 0, 0), (2, 0, 0)))
        txt = plan.reporte(plan.fcfs())
        self.assertIn("Espera promedio", txt)
        self.assertIn("Respuesta promedio", txt)
        self.assertIn("Menor espera promedio", plan.comparativa(plan.todos()))


if __name__ == "__main__":
    unittest.main()
