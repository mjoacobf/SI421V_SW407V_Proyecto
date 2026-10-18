"""Punto de entrada de NexusOS-Sim.

Uso:  python src/main.py
"""
import sys

from shell import Shell


def main() -> None:
    # En Windows la consola/pipe puede no usar UTF-8 por defecto.
    for flujo in (sys.stdout, sys.stdin):
        if hasattr(flujo, "reconfigure"):
            flujo.reconfigure(encoding="utf-8")
    Shell().ejecutar()


if __name__ == "__main__":
    main()
