import io
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from shell import Shell  # noqa: E402


def correr(*lineas: str) -> str:
    salida = io.StringIO()
    Shell(io.StringIO("\n".join(lineas) + "\n"), salida).ejecutar()
    return salida.getvalue()


class TestShell(unittest.TestCase):
    def test_help_y_exit(self):
        out = correr("help", "exit")
        self.assertIn("Comandos disponibles", out)
        self.assertIn("Apagando", out)

    def test_mkdir_ls_cd(self):
        self.assertIn("/banco", correr("mkdir banco", "cd banco", "pwd", "exit"))
        self.assertIn("banco/", correr("mkdir banco", "ls", "exit"))

    def test_mkdir_duplicado_no_rompe_el_shell(self):
        out = correr("mkdir home", "exit")
        self.assertIn("ya existe", out)
        self.assertIn("Apagando", out)

    def test_comando_desconocido(self):
        self.assertIn("comando no encontrado", correr("foo", "exit"))


if __name__ == "__main__":
    unittest.main()
