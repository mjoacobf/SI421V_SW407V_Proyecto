"""Demostración: procesos (fork) vs. hilos (threading).

* Un proceso hijo creado con ``fork`` recibe una COPIA de los registros del
  padre: modificarlos no afecta al padre (espacios de direcciones separados).
* Los hilos de un mismo proceso COMPARTEN datos: todos modifican el mismo
  contador, por lo que el acceso debe protegerse con un Lock.

Uso independiente:  python src/demo_hilos.py
"""
from __future__ import annotations

import threading
import time
from typing import Callable

from procesos import GestorProcesos


def demo_fork(imprimir: Callable[[str], None] = print) -> None:
    gestor = GestorProcesos()
    padre = gestor.crear("padre", rafaga=5)
    padre.registros["AX"] = 10
    hijo = gestor.fork(padre.pid)
    hijo.registros["AX"] = 99
    imprimir(f"[fork] padre PID {padre.pid} AX={padre.registros['AX']}  |  "
             f"hijo PID {hijo.pid} (ppid {hijo.ppid}) AX={hijo.registros['AX']}")
    imprimir("[fork] los registros están aislados: el cambio del hijo no afecta al padre")


def demo_hilos(n_hilos: int = 4, incrementos: int = 3, imprimir: Callable[[str], None] = print) -> int:
    """Lanza ``n_hilos`` hilos que incrementan un contador compartido."""
    compartido = {"contador": 0}
    candado = threading.Lock()
    lineas: list[str] = []  # los hilos solo agregan aquí; se imprime desde el hilo principal

    def trabajo(numero: int) -> None:
        for paso in range(incrementos):
            with candado:
                compartido["contador"] += 1
                lineas.append(f"[hilo-{numero}] paso {paso + 1}/{incrementos} -> contador={compartido['contador']}")
            time.sleep(0.001)  # cede la CPU para intercalar la ejecución

    hilos = [threading.Thread(target=trabajo, args=(i,), name=f"hilo-{i}") for i in range(n_hilos)]
    for h in hilos:
        h.start()
    for h in hilos:
        h.join()
    for linea in lineas:
        imprimir(linea)
    esperado = n_hilos * incrementos
    imprimir(f"[hilos] contador final={compartido['contador']} (esperado {esperado}): "
             "los hilos comparten memoria")
    return compartido["contador"]


if __name__ == "__main__":
    demo_fork()
    demo_hilos()
