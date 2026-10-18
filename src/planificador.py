"""Algoritmos de asignación de CPU (FCFS, SJF, Round Robin, Prioridad).

El planificador trabaja sobre una *vista* (llegada, ráfaga, prioridad) de los
procesos y nunca modifica los PCB originales, de modo que la misma lista puede
evaluarse con todos los algoritmos y compararse.

Convenciones:
  * SJF y Prioridad son no expropiativos.
  * Prioridad: un número menor significa mayor prioridad.
  * Los empates se resuelven por tiempo de llegada y luego por PID.
  * Round Robin: un proceso que llega justo cuando termina un quantum entra a
    la cola *antes* que el proceso que se expropia.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Callable

from procesos import Proceso

# Unidad de las métricas: 1 unidad de tiempo simulada = 1 milisegundo (ms).
UNIDAD_TIEMPO = "ms"


@dataclass
class MetricasProceso:
    pid: int
    nombre: str
    llegada: int
    rafaga: int
    inicio: int          # primer instante en CPU
    finalizacion: int
    retorno: int         # finalización - llegada
    espera: int          # retorno - ráfaga
    respuesta: int       # inicio - llegada


@dataclass
class Resultado:
    algoritmo: str
    gantt: list[tuple[int, int, int]]  # (pid, inicio, fin) en orden cronológico
    metricas: list[MetricasProceso]
    espera_promedio: float
    respuesta_promedio: float
    retorno_promedio: float


class Planificador:
    """Evalúa una lista de procesos con distintos algoritmos de CPU."""

    def __init__(self, procesos: list[Proceso]) -> None:
        if not procesos:
            raise ValueError("se necesita al menos un proceso para planificar")
        pids = [p.pid for p in procesos]
        if len(set(pids)) != len(pids):
            raise ValueError("hay PIDs repetidos en la lista de procesos")
        self.procesos = list(procesos)

    # -- algoritmos -------------------------------------------------------
    def fcfs(self) -> Resultado:
        return self._no_expropiativo("FCFS", lambda p: (p.llegada, p.pid))

    def sjf(self) -> Resultado:
        return self._no_expropiativo("SJF", lambda p: (p.rafaga, p.llegada, p.pid))

    def prioridad(self) -> Resultado:
        return self._no_expropiativo("Prioridad", lambda p: (p.prioridad, p.llegada, p.pid))

    def round_robin(self, quantum: int) -> Resultado:
        if quantum <= 0:
            raise ValueError("el quantum debe ser positivo")
        pendientes = sorted(self.procesos, key=lambda p: (p.llegada, p.pid))
        restante = {p.pid: p.rafaga for p in pendientes}
        cola: deque[Proceso] = deque()
        gantt: list[tuple[int, int, int]] = []
        inicio: dict[int, int] = {}
        fin: dict[int, int] = {}
        t = 0
        i = 0  # siguiente proceso por llegar

        def admitir() -> None:
            nonlocal i
            while i < len(pendientes) and pendientes[i].llegada <= t:
                cola.append(pendientes[i])
                i += 1

        admitir()
        while cola or i < len(pendientes):
            if not cola:                      # CPU ociosa hasta la próxima llegada
                t = pendientes[i].llegada
                admitir()
            p = cola.popleft()
            inicio.setdefault(p.pid, t)
            uso = min(quantum, restante[p.pid])
            gantt.append((p.pid, t, t + uso))
            t += uso
            restante[p.pid] -= uso
            admitir()
            if restante[p.pid] > 0:
                cola.append(p)
            else:
                fin[p.pid] = t
        return self._resultado(f"Round Robin (q={quantum})", gantt, inicio, fin)

    # -- núcleo común -----------------------------------------------------
    def _no_expropiativo(self, nombre: str, clave: Callable[[Proceso], tuple]) -> Resultado:
        por_llegar = sorted(self.procesos, key=lambda p: (p.llegada, p.pid))
        listos: list[Proceso] = []
        gantt: list[tuple[int, int, int]] = []
        inicio: dict[int, int] = {}
        fin: dict[int, int] = {}
        t = 0
        i = 0
        while i < len(por_llegar) or listos:
            while i < len(por_llegar) and por_llegar[i].llegada <= t:
                listos.append(por_llegar[i])
                i += 1
            if not listos:                    # CPU ociosa
                t = por_llegar[i].llegada
                continue
            p = min(listos, key=clave)
            listos.remove(p)
            inicio[p.pid] = t
            gantt.append((p.pid, t, t + p.rafaga))
            t += p.rafaga
            fin[p.pid] = t
        return self._resultado(nombre, gantt, inicio, fin)

    def _resultado(
        self, algoritmo: str, gantt: list[tuple[int, int, int]],
        inicio: dict[int, int], fin: dict[int, int],
    ) -> Resultado:
        # Une segmentos contiguos del mismo proceso (útil en Round Robin).
        fusionado: list[tuple[int, int, int]] = []
        for pid, a, b in gantt:
            if fusionado and fusionado[-1][0] == pid and fusionado[-1][2] == a:
                fusionado[-1] = (pid, fusionado[-1][1], b)
            else:
                fusionado.append((pid, a, b))
        metricas = []
        for p in sorted(self.procesos, key=lambda p: p.pid):
            retorno = fin[p.pid] - p.llegada
            metricas.append(MetricasProceso(
                pid=p.pid, nombre=p.nombre, llegada=p.llegada, rafaga=p.rafaga,
                inicio=inicio[p.pid], finalizacion=fin[p.pid], retorno=retorno,
                espera=retorno - p.rafaga, respuesta=inicio[p.pid] - p.llegada,
            ))
        n = len(metricas)
        return Resultado(
            algoritmo=algoritmo, gantt=fusionado, metricas=metricas,
            espera_promedio=sum(m.espera for m in metricas) / n,
            respuesta_promedio=sum(m.respuesta for m in metricas) / n,
            retorno_promedio=sum(m.retorno for m in metricas) / n,
        )

    # -- ejecución por nombre y reportes ---------------------------------
    def ejecutar(self, algoritmo: str, quantum: int = 2) -> Resultado:
        algoritmo = algoritmo.lower()
        if algoritmo == "fcfs":
            return self.fcfs()
        if algoritmo == "sjf":
            return self.sjf()
        if algoritmo in ("prioridad", "prio"):
            return self.prioridad()
        if algoritmo in ("rr", "round_robin"):
            return self.round_robin(quantum)
        raise ValueError(f"algoritmo desconocido: '{algoritmo}' (fcfs, sjf, rr, prioridad)")

    def todos(self, quantum: int = 2) -> list[Resultado]:
        return [self.fcfs(), self.sjf(), self.round_robin(quantum), self.prioridad()]

    @staticmethod
    def reporte(r: Resultado) -> str:
        lineas = [f"=== {r.algoritmo} ===", "Gantt: " + _gantt_texto(r.gantt)]
        lineas.append(f"{'PID':>4} {'NOMBRE':<12} {'LLEG':>4} {'RAF':>4} {'INI':>4} {'FIN':>4} "
                      f"{'RET':>4} {'ESP':>4} {'RESP':>4}")
        for m in r.metricas:
            lineas.append(f"{m.pid:>4} {m.nombre:<12} {m.llegada:>4} {m.rafaga:>4} {m.inicio:>4} "
                          f"{m.finalizacion:>4} {m.retorno:>4} {m.espera:>4} {m.respuesta:>4}")
        u = UNIDAD_TIEMPO
        lineas.append(f"Espera promedio:    {r.espera_promedio:.2f} {u}")
        lineas.append(f"Respuesta promedio: {r.respuesta_promedio:.2f} {u}")
        lineas.append(f"Retorno promedio:   {r.retorno_promedio:.2f} {u}")
        lineas.append(f"Leyenda: LLEG=llegada, RAF=ráfaga, INI=inicio, FIN=finalización, "
                      f"RET=retorno, ESP=espera, RESP=respuesta (todo en {u})")
        return "\n".join(lineas)

    @staticmethod
    def comparativa(resultados: list[Resultado]) -> str:
        u = UNIDAD_TIEMPO
        lineas = [f"=== Comparativa (tiempos promedio en {u}) ===",
                  f"{'ALGORITMO':<20} {'ESPERA ('+u+')':>11} {'RESPUESTA ('+u+')':>14} {'RETORNO ('+u+')':>12}"]
        for r in resultados:
            lineas.append(f"{r.algoritmo:<20} {r.espera_promedio:>11.2f} "
                          f"{r.respuesta_promedio:>14.2f} {r.retorno_promedio:>12.2f}")
        mejor = min(resultados, key=lambda r: r.espera_promedio)
        lineas.append(f"Menor espera promedio: {mejor.algoritmo} ({mejor.espera_promedio:.2f} {u})")
        return "\n".join(lineas)


def _gantt_texto(gantt: list[tuple[int, int, int]]) -> str:
    if not gantt:
        return ""
    partes = [f"{gantt[0][1]}"]
    for pid, _, b in gantt:
        partes.append(f"| P{pid} | {b}")
    return " ".join(partes) + f"  ({UNIDAD_TIEMPO})"
