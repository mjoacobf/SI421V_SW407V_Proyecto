import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from demo_hilos import demo_hilos  # noqa: E402
from procesos import ErrorProceso, Estado, GestorProcesos  # noqa: E402


class TestProcesos(unittest.TestCase):
    def setUp(self):
        self.g = GestorProcesos()

    def test_crear_admite_en_listos(self):
        p = self.g.crear("a", 3)
        self.assertEqual(p.estado, Estado.LISTO)
        self.assertEqual(self.g.listos, [p])

    def test_ciclo_de_vida_completo(self):
        p = self.g.crear("a", 3)
        self.assertIs(self.g.despachar(), p)
        self.assertEqual(p.estado, Estado.EJECUCION)
        self.g.bloquear(p.pid)
        self.assertEqual(self.g.bloqueados, [p])
        self.g.desbloquear(p.pid)
        self.g.despachar()
        self.g.expropiar(p.pid)
        self.assertEqual(p.estado, Estado.LISTO)
        self.g.despachar()
        self.g.terminar(p.pid)
        self.assertEqual(p.estado, Estado.TERMINADO)
        self.assertIsNone(self.g.en_ejecucion)

    def test_cpu_ocupada(self):
        self.g.crear("a")
        self.g.crear("b")
        self.g.despachar()
        with self.assertRaises(ErrorProceso):
            self.g.despachar()

    def test_transicion_ilegal(self):
        p = self.g.crear("a")
        with self.assertRaises(ErrorProceso):
            p.cambiar_estado(Estado.BLOQUEADO)

    def test_fork_copia_aislada(self):
        p = self.g.crear("a", 4, prioridad=2)
        p.registros["AX"] = 7
        p.pc = 3
        h = self.g.fork(p.pid)
        self.assertNotEqual(h.pid, p.pid)
        self.assertEqual(h.ppid, p.pid)
        self.assertEqual((h.pc, h.registros["AX"], h.prioridad), (3, 7, 2))
        h.registros["AX"] = 1
        self.assertEqual(p.registros["AX"], 7)
        self.assertEqual(h.estado, Estado.LISTO)

    def test_exec_reinicia_conservando_pid(self):
        p = self.g.crear("a", 4)
        p.pc = 9
        p.registros["BX"] = 5
        self.g.exec(p.pid, "b", 2)
        self.assertEqual((p.nombre, p.pc, p.registros["BX"], p.rafaga), ("b", 0, 0, 2))

    def test_pid_inexistente_y_terminado(self):
        with self.assertRaises(ErrorProceso):
            self.g.fork(99)
        p = self.g.crear("a")
        self.g.terminar(p.pid)
        with self.assertRaises(ErrorProceso):
            self.g.fork(p.pid)

    def test_terminar_desde_listos_y_bloqueados(self):
        a, b = self.g.crear("a"), self.g.crear("b")
        self.g.despachar()
        self.g.bloquear(a.pid)
        self.g.terminar(a.pid)
        self.g.terminar(b.pid)
        self.assertEqual((self.g.listos, self.g.bloqueados), ([], []))

    def test_hilos_comparten_memoria_sin_perder_incrementos(self):
        self.assertEqual(demo_hilos(6, 20, imprimir=lambda _: None), 120)


if __name__ == "__main__":
    unittest.main()
