"""Gestión del Bloque de Control de Proceso (PCB) y su ciclo de vida.

Modelo de 5 estados:

    NUEVO -> LISTO -> EJECUCION -> TERMINADO
               ^          |
               |          v
               +------ BLOQUEADO   (EJECUCION -> LISTO = expropiación)
"""
from __future__ import annotations

import copy
from enum import Enum


class Estado(Enum):
    NUEVO = "Nuevo"
    LISTO = "Listo"
    EJECUCION = "Ejecución"
    BLOQUEADO = "Bloqueado"
    TERMINADO = "Terminado"


# Transiciones permitidas del diagrama de 5 estados.
TRANSICIONES: dict[Estado, set[Estado]] = {
    Estado.NUEVO: {Estado.LISTO},
    Estado.LISTO: {Estado.EJECUCION},
    Estado.EJECUCION: {Estado.LISTO, Estado.BLOQUEADO, Estado.TERMINADO},
    Estado.BLOQUEADO: {Estado.LISTO},
    Estado.TERMINADO: set(),
}

REGISTROS_INICIALES = ("AX", "BX", "CX", "DX")


class ErrorProceso(Exception):
    """Operación inválida sobre un proceso (PID inexistente, transición ilegal...)."""


class Proceso:
    """Bloque de Control de Proceso (PCB).

    Los atributos ``llegada``, ``rafaga`` y ``prioridad`` son los datos que
    consume el planificador (menor número de prioridad = mayor prioridad).
    """

    def __init__(
        self,
        pid: int,
        nombre: str,
        rafaga: int = 1,
        prioridad: int = 0,
        llegada: int = 0,
        ppid: int = 0,
    ) -> None:
        if rafaga <= 0:
            raise ValueError("la ráfaga de CPU debe ser positiva")
        if llegada < 0:
            raise ValueError("el tiempo de llegada no puede ser negativo")
        self.pid = pid
        self.ppid = ppid
        self.nombre = nombre
        self.estado = Estado.NUEVO
        self.pc = 0
        self.registros: dict[str, int] = dict.fromkeys(REGISTROS_INICIALES, 0)
        self.rafaga = rafaga
        self.prioridad = prioridad
        self.llegada = llegada

    def cambiar_estado(self, nuevo: Estado) -> None:
        if nuevo not in TRANSICIONES[self.estado]:
            raise ErrorProceso(
                f"transición ilegal para PID {self.pid}: "
                f"{self.estado.value} -> {nuevo.value}"
            )
        self.estado = nuevo

    def __repr__(self) -> str:
        return (
            f"Proceso(pid={self.pid}, nombre={self.nombre!r}, "
            f"estado={self.estado.value}, rafaga={self.rafaga}, prioridad={self.prioridad})"
        )


class GestorProcesos:
    """Tabla de procesos más las colas de Listos y Bloqueados."""

    def __init__(self) -> None:
        self.tabla: dict[int, Proceso] = {}
        self.listos: list[Proceso] = []
        self.bloqueados: list[Proceso] = []
        self.en_ejecucion: Proceso | None = None
        self._siguiente_pid = 1

    # -- creación ---------------------------------------------------------
    def _nuevo_pid(self) -> int:
        pid = self._siguiente_pid
        self._siguiente_pid += 1
        return pid

    def crear(
        self, nombre: str, rafaga: int = 1, prioridad: int = 0, llegada: int = 0, ppid: int = 0
    ) -> Proceso:
        """Crea un proceso y lo admite en la cola de Listos."""
        p = Proceso(self._nuevo_pid(), nombre, rafaga, prioridad, llegada, ppid)
        self.tabla[p.pid] = p
        self._admitir(p)
        return p

    def _admitir(self, p: Proceso) -> None:
        p.cambiar_estado(Estado.LISTO)
        self.listos.append(p)

    def obtener(self, pid: int) -> Proceso:
        try:
            return self.tabla[pid]
        except KeyError:
            raise ErrorProceso(f"no existe el proceso con PID {pid}") from None

    # -- fork / exec ------------------------------------------------------
    def fork(self, pid: int) -> Proceso:
        """Duplica un proceso: el hijo recibe copia de PC y registros y un PID nuevo."""
        padre = self.obtener(pid)
        if padre.estado is Estado.TERMINADO:
            raise ErrorProceso(f"el proceso {pid} ya terminó; no se puede hacer fork")
        hijo = copy.deepcopy(padre)
        hijo.pid = self._nuevo_pid()
        hijo.ppid = padre.pid
        hijo.estado = Estado.NUEVO
        self.tabla[hijo.pid] = hijo
        self._admitir(hijo)
        return hijo

    def exec(self, pid: int, nombre: str, rafaga: int | None = None) -> Proceso:
        """Reemplaza la imagen del proceso: conserva PID/PPID, reinicia PC y registros."""
        p = self.obtener(pid)
        if p.estado is Estado.TERMINADO:
            raise ErrorProceso(f"el proceso {pid} ya terminó; no se puede hacer exec")
        if rafaga is not None and rafaga <= 0:
            raise ValueError("la ráfaga de CPU debe ser positiva")
        p.nombre = nombre
        p.pc = 0
        p.registros = dict.fromkeys(REGISTROS_INICIALES, 0)
        if rafaga is not None:
            p.rafaga = rafaga
        return p

    # -- movimiento entre estados ----------------------------------------
    def despachar(self) -> Proceso | None:
        """Asigna la CPU al primer proceso de la cola de Listos."""
        if self.en_ejecucion is not None:
            raise ErrorProceso(f"la CPU está ocupada por el PID {self.en_ejecucion.pid}")
        if not self.listos:
            return None
        p = self.listos.pop(0)
        p.cambiar_estado(Estado.EJECUCION)
        self.en_ejecucion = p
        return p

    def _liberar_cpu(self, pid: int) -> Proceso:
        p = self.obtener(pid)
        if self.en_ejecucion is not p:
            raise ErrorProceso(f"el PID {pid} no está en ejecución")
        self.en_ejecucion = None
        return p

    def expropiar(self, pid: int) -> None:
        """EJECUCION -> LISTO (fin de quantum o llegada de otro proceso)."""
        p = self._liberar_cpu(pid)
        p.cambiar_estado(Estado.LISTO)
        self.listos.append(p)

    def bloquear(self, pid: int) -> None:
        """EJECUCION -> BLOQUEADO (espera de E/S o de un evento)."""
        p = self._liberar_cpu(pid)
        p.cambiar_estado(Estado.BLOQUEADO)
        self.bloqueados.append(p)

    def desbloquear(self, pid: int) -> None:
        """BLOQUEADO -> LISTO (el evento esperado ocurrió)."""
        p = self.obtener(pid)
        if p not in self.bloqueados:
            raise ErrorProceso(f"el PID {pid} no está bloqueado")
        self.bloqueados.remove(p)
        p.cambiar_estado(Estado.LISTO)
        self.listos.append(p)

    def terminar(self, pid: int) -> None:
        """Termina un proceso desde cualquier estado activo (equivale a kill)."""
        p = self.obtener(pid)
        if p.estado is Estado.TERMINADO:
            raise ErrorProceso(f"el PID {pid} ya terminó")
        if p is self.en_ejecucion:
            self.en_ejecucion = None
        elif p in self.listos:
            self.listos.remove(p)
        elif p in self.bloqueados:
            self.bloqueados.remove(p)
        # Los estados no permiten LISTO/BLOQUEADO -> TERMINADO por el camino
        # normal; kill es una señal del kernel y fuerza la transición.
        p.estado = Estado.TERMINADO

    # -- consulta ---------------------------------------------------------
    def listar(self) -> list[Proceso]:
        return sorted(self.tabla.values(), key=lambda p: p.pid)

    def tabla_texto(self) -> str:
        filas = [f"{'PID':>4} {'PPID':>4} {'NOMBRE':<12} {'ESTADO':<10} {'PC':>4} {'RAF':>4} {'PRIO':>4} {'LLEG':>4}"]
        for p in self.listar():
            filas.append(
                f"{p.pid:>4} {p.ppid:>4} {p.nombre:<12} {p.estado.value:<10} "
                f"{p.pc:>4} {p.rafaga:>4} {p.prioridad:>4} {p.llegada:>4}"
            )
        return "\n".join(filas)
