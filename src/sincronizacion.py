"""Concurrencia, semáforos y prevención de interbloqueos.

Contiene dos simulaciones clásicas:

* Productor-Consumidor con búfer acotado (mutex + semáforos ``vacios``/``llenos``).
* Filósofos comensales, con modo ingenuo (provoca interbloqueo de forma
  determinista y lo detecta) y modo asimétrico (lo previene).
"""
from __future__ import annotations

import threading
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Callable

Log = Callable[[str], None]


def _logger_seguro(log: Log | None) -> Log:
    """Serializa las llamadas a ``log`` para que las líneas no se mezclen."""
    candado = threading.Lock()
    destino = log or (lambda _: None)

    def emitir(mensaje: str) -> None:
        with candado:
            destino(mensaje)

    return emitir


# ---------------------------------------------------------------------------
# Productor-Consumidor
# ---------------------------------------------------------------------------
@dataclass
class ResultadoProductorConsumidor:
    producidos: list[int] = field(default_factory=list)
    consumidos: list[int] = field(default_factory=list)
    max_ocupacion: int = 0
    capacidad: int = 0

    @property
    def correcto(self) -> bool:
        """Se consumió exactamente lo producido y el búfer nunca se desbordó."""
        return (sorted(self.producidos) == sorted(self.consumidos)
                and self.max_ocupacion <= self.capacidad)


def productor_consumidor(
    n_productores: int = 2,
    n_consumidores: int = 2,
    items_por_productor: int = 5,
    capacidad: int = 3,
    log: Log | None = None,
    retardo: float = 0.001,
) -> ResultadoProductorConsumidor:
    """Simula productores y consumidores sobre un búfer de ``capacidad`` posiciones."""
    if min(n_productores, n_consumidores, items_por_productor, capacidad) <= 0:
        raise ValueError("todos los parámetros deben ser positivos")
    emitir = _logger_seguro(log)
    buffer: deque[int] = deque()
    mutex = threading.Semaphore(1)            # exclusión mutua sobre el búfer
    vacios = threading.Semaphore(capacidad)   # posiciones libres
    llenos = threading.Semaphore(0)           # posiciones ocupadas
    res = ResultadoProductorConsumidor(capacidad=capacidad)

    total = n_productores * items_por_productor
    base, extra = divmod(total, n_consumidores)
    cuotas = [base + (1 if i < extra else 0) for i in range(n_consumidores)]

    def productor(num: int) -> None:
        for k in range(items_por_productor):
            item = num * 1000 + k
            time.sleep(retardo)
            vacios.acquire()                  # espera una posición libre
            mutex.acquire()
            buffer.append(item)
            res.producidos.append(item)
            res.max_ocupacion = max(res.max_ocupacion, len(buffer))
            emitir(f"[productor-{num}] produce {item}  (búfer: {len(buffer)}/{capacidad})")
            mutex.release()
            llenos.release()

    def consumidor(num: int, cuota: int) -> None:
        for _ in range(cuota):
            llenos.acquire()                  # espera un elemento disponible
            mutex.acquire()
            item = buffer.popleft()
            res.consumidos.append(item)
            emitir(f"[consumidor-{num}] consume {item}  (búfer: {len(buffer)}/{capacidad})")
            mutex.release()
            vacios.release()
            time.sleep(retardo)

    hilos = [threading.Thread(target=productor, args=(i,)) for i in range(n_productores)]
    hilos += [threading.Thread(target=consumidor, args=(i, cuotas[i])) for i in range(n_consumidores)]
    for h in hilos:
        h.start()
    for h in hilos:
        h.join()
    emitir(f"Resumen: producidos={len(res.producidos)} consumidos={len(res.consumidos)} "
           f"máx. ocupación={res.max_ocupacion}/{capacidad} -> "
           f"{'CORRECTO' if res.correcto else 'INCORRECTO'}")
    return res


# ---------------------------------------------------------------------------
# Filósofos comensales
# ---------------------------------------------------------------------------
@dataclass
class ResultadoFilosofos:
    interbloqueo: bool
    comidas: list[int]


def filosofos(
    n: int = 5,
    comidas: int = 3,
    asimetrico: bool = True,
    log: Log | None = None,
    espera_max: float = 0.5,
) -> ResultadoFilosofos:
    """Simula ``n`` filósofos con ``n`` tenedores (Locks).

    * ``asimetrico=False``: todos toman primero el tenedor izquierdo y luego el
      derecho. Una barrera garantiza que todos tengan el izquierdo antes de
      pedir el derecho, lo que produce un interbloqueo cíclico. Se detecta con
      un ``acquire`` con tiempo límite (``espera_max``) y los filósofos abandonan.
    * ``asimetrico=True``: el último filósofo toma los tenedores en orden
      inverso. Se rompe la espera circular, por lo que el interbloqueo es imposible.
    """
    if n < 2 or comidas <= 0:
        raise ValueError("se requieren al menos 2 filósofos y 1 comida")
    emitir = _logger_seguro(log)
    tenedores = [threading.Lock() for _ in range(n)]
    barrera = threading.Barrier(n, timeout=espera_max * 4)
    hubo_interbloqueo = threading.Event()
    contador = [0] * n

    def filosofo(i: int) -> None:
        izq, der = i, (i + 1) % n
        primero, segundo = (der, izq) if asimetrico and i == n - 1 else (izq, der)
        for _ in range(comidas):
            if hubo_interbloqueo.is_set():
                return
            emitir(f"[filósofo-{i}] piensa")
            tenedores[primero].acquire()
            emitir(f"[filósofo-{i}] toma tenedor {primero}")
            if not asimetrico and contador[i] == 0:
                try:
                    barrera.wait()            # fuerza que todos sostengan su primer tenedor
                except threading.BrokenBarrierError:
                    pass
            if not tenedores[segundo].acquire(timeout=espera_max if not asimetrico else -1):
                hubo_interbloqueo.set()
                emitir(f"[filósofo-{i}] INTERBLOQUEO: espera el tenedor {segundo} que nunca se liberará")
                tenedores[primero].release()
                return
            emitir(f"[filósofo-{i}] toma tenedor {segundo} y COME")
            contador[i] += 1
            time.sleep(0.001)
            tenedores[segundo].release()
            tenedores[primero].release()
            emitir(f"[filósofo-{i}] suelta los tenedores")

    hilos = [threading.Thread(target=filosofo, args=(i,)) for i in range(n)]
    for h in hilos:
        h.start()
    for h in hilos:
        h.join()
    res = ResultadoFilosofos(interbloqueo=hubo_interbloqueo.is_set(), comidas=contador)
    if res.interbloqueo:
        emitir("Resumen: se detectó INTERBLOQUEO (espera circular)")
    else:
        emitir(f"Resumen: sin interbloqueo; comidas por filósofo = {contador}")
    return res
