"""Traducción de direcciones y asignación de espacio (contigua y paginación)."""
from __future__ import annotations

from dataclasses import dataclass

from procesos import Proceso


class ErrorMemoria(Exception):
    """No hay memoria suficiente o la operación es inválida."""


class SegmentationFault(Exception):
    """Acceso a una dirección virtual fuera del espacio del proceso."""


# ---------------------------------------------------------------------------
# Asignación contigua con particiones variables
# ---------------------------------------------------------------------------
@dataclass
class Bloque:
    inicio: int
    tamano: int
    pid: int | None = None  # None = hueco libre

    @property
    def fin(self) -> int:
        return self.inicio + self.tamano


class GestorMemoriaContigua:
    """Lista de bloques ocupados/libres con estrategias first/best/worst fit."""

    ESTRATEGIAS = ("first", "best", "worst")

    def __init__(self, tamano_total: int, estrategia: str = "first") -> None:
        if tamano_total <= 0:
            raise ValueError("el tamaño de la memoria debe ser positivo")
        if estrategia not in self.ESTRATEGIAS:
            raise ValueError(f"estrategia desconocida: {estrategia} {self.ESTRATEGIAS}")
        self.tamano_total = tamano_total
        self.estrategia = estrategia
        self.bloques: list[Bloque] = [Bloque(0, tamano_total)]

    def asignar(self, pid: int, tamano: int) -> int:
        """Reserva ``tamano`` bytes contiguos; devuelve la dirección base."""
        if tamano <= 0:
            raise ValueError("el tamaño solicitado debe ser positivo")
        if any(b.pid == pid for b in self.bloques):
            raise ErrorMemoria(f"el PID {pid} ya tiene memoria asignada")
        huecos = [b for b in self.bloques if b.pid is None and b.tamano >= tamano]
        if not huecos:
            if self.libre_total() >= tamano:
                raise ErrorMemoria(
                    f"fragmentación externa: hay {self.libre_total()} libres en total "
                    f"pero el hueco mayor es de {self.hueco_mayor()} (se piden {tamano})"
                )
            raise ErrorMemoria(f"memoria insuficiente: se piden {tamano}, libres {self.libre_total()}")
        if self.estrategia == "first":
            hueco = huecos[0]
        elif self.estrategia == "best":
            hueco = min(huecos, key=lambda b: b.tamano)
        else:
            hueco = max(huecos, key=lambda b: b.tamano)
        idx = self.bloques.index(hueco)
        if hueco.tamano > tamano:
            self.bloques.insert(idx + 1, Bloque(hueco.inicio + tamano, hueco.tamano - tamano))
        hueco.tamano = tamano
        hueco.pid = pid
        return hueco.inicio

    def liberar(self, pid: int) -> None:
        for b in self.bloques:
            if b.pid == pid:
                b.pid = None
                break
        else:
            raise ErrorMemoria(f"el PID {pid} no tiene memoria contigua asignada")
        self._fusionar_huecos()

    def _fusionar_huecos(self) -> None:
        fusionados: list[Bloque] = []
        for b in self.bloques:
            if fusionados and fusionados[-1].pid is None and b.pid is None:
                fusionados[-1].tamano += b.tamano
            else:
                fusionados.append(b)
        self.bloques = fusionados

    def libre_total(self) -> int:
        return sum(b.tamano for b in self.bloques if b.pid is None)

    def hueco_mayor(self) -> int:
        return max((b.tamano for b in self.bloques if b.pid is None), default=0)

    def fragmentacion_externa(self) -> int:
        """Memoria libre que no puede usarse en una sola asignación: libre total - hueco mayor."""
        return self.libre_total() - self.hueco_mayor()

    def mapa_texto(self) -> str:
        lineas = [f"Memoria contigua ({self.tamano_total} B, {self.estrategia}-fit)"]
        for b in self.bloques:
            dueno = "LIBRE" if b.pid is None else f"PID {b.pid}"
            lineas.append(f"  [{b.inicio:>5} - {b.fin - 1:>5}] {b.tamano:>5} B  {dueno}")
        lineas.append(f"  Libre total: {self.libre_total()} B  |  Hueco mayor: {self.hueco_mayor()} B  "
                      f"|  Fragmentación externa: {self.fragmentacion_externa()} B")
        lineas.append("  Leyenda: B = bytes")
        return "\n".join(lineas)


# ---------------------------------------------------------------------------
# Paginación
# ---------------------------------------------------------------------------
class TablaPaginas:
    """Tabla de páginas de un proceso: índice = nº de página, valor = nº de marco."""

    def __init__(self, tamano_logico: int, marcos: list[int]) -> None:
        self.tamano_logico = tamano_logico
        self.marcos = marcos

    def __len__(self) -> int:
        return len(self.marcos)


class GestorPaginacion:
    """RAM dividida en marcos de tamaño fijo; cada proceso tiene su TablaPaginas."""

    def __init__(self, num_marcos: int, tam_pagina: int) -> None:
        if num_marcos <= 0 or tam_pagina <= 0:
            raise ValueError("num_marcos y tam_pagina deben ser positivos")
        self.num_marcos = num_marcos
        self.tam_pagina = tam_pagina
        self.marcos: list[int | None] = [None] * num_marcos  # marco -> PID dueño
        self.tablas: dict[int, TablaPaginas] = {}

    def marcos_libres(self) -> int:
        return self.marcos.count(None)

    def asignar(self, pid: int, tamano: int) -> TablaPaginas:
        """Divide ``tamano`` bytes en páginas y las ubica en marcos libres (no necesariamente contiguos)."""
        if tamano <= 0:
            raise ValueError("el tamaño solicitado debe ser positivo")
        if pid in self.tablas:
            raise ErrorMemoria(f"el PID {pid} ya tiene memoria asignada")
        paginas = -(-tamano // self.tam_pagina)  # división techo
        if paginas > self.marcos_libres():
            raise ErrorMemoria(f"memoria insuficiente: se necesitan {paginas} marcos, libres {self.marcos_libres()}")
        asignados = [i for i, dueno in enumerate(self.marcos) if dueno is None][:paginas]
        for m in asignados:
            self.marcos[m] = pid
        self.tablas[pid] = TablaPaginas(tamano, asignados)
        return self.tablas[pid]

    def liberar(self, pid: int) -> None:
        tabla = self.tablas.pop(pid, None)
        if tabla is None:
            raise ErrorMemoria(f"el PID {pid} no tiene páginas asignadas")
        for m in tabla.marcos:
            self.marcos[m] = None

    def fragmentacion_interna(self, pid: int) -> int:
        tabla = self.tablas[pid]
        return len(tabla) * self.tam_pagina - tabla.tamano_logico

    def traducir_direccion(self, proceso: Proceso | int, dir_virtual: int) -> int:
        """Traduce una dirección virtual a física o lanza ``SegmentationFault``."""
        pid = proceso.pid if isinstance(proceso, Proceso) else proceso
        tabla = self.tablas.get(pid)
        if tabla is None:
            raise SegmentationFault(f"el PID {pid} no tiene espacio de direcciones asignado")
        if not 0 <= dir_virtual < tabla.tamano_logico:
            raise SegmentationFault(
                f"SEGMENTATION FAULT: dirección virtual {dir_virtual} fuera del rango "
                f"[0, {tabla.tamano_logico - 1}] del PID {pid}"
            )
        pagina, desplazamiento = divmod(dir_virtual, self.tam_pagina)
        return tabla.marcos[pagina] * self.tam_pagina + desplazamiento

    def mapa_texto(self) -> str:
        lineas = [f"Paginación ({self.num_marcos} marcos x {self.tam_pagina} B, libres: {self.marcos_libres()} marcos)"]
        for i, dueno in enumerate(self.marcos):
            if dueno is None:
                lineas.append(f"  marco {i:>3}: libre")
            else:
                pagina = self.tablas[dueno].marcos.index(i)
                lineas.append(f"  marco {i:>3}: PID {dueno} página {pagina}")
        for pid, tabla in sorted(self.tablas.items()):
            lineas.append(f"  Tabla de páginas PID {pid} ({tabla.tamano_logico} B, "
                          f"frag. interna {self.fragmentacion_interna(pid)} B): "
                          + ", ".join(f"p{p}->m{m}" for p, m in enumerate(tabla.marcos)))
        return "\n".join(lineas)


# ---------------------------------------------------------------------------
# Reemplazo de páginas (memoria virtual): FIFO, LRU y Óptimo
# ---------------------------------------------------------------------------
ALGORITMOS_REEMPLAZO = ("fifo", "lru", "optimo")


@dataclass
class ResultadoReemplazo:
    algoritmo: str
    num_marcos: int
    referencias: list[int]
    fallos: int
    # (página referenciada, ¿fallo?, página expulsada o None, marcos tras el acceso)
    pasos: list[tuple[int, bool, int | None, list[int]]]

    @property
    def tasa_fallos(self) -> float:
        return self.fallos / len(self.referencias) if self.referencias else 0.0


def reemplazo_paginas(algoritmo: str, referencias: list[int], num_marcos: int) -> ResultadoReemplazo:
    """Simula el reemplazo de páginas sobre una cadena de referencias.

    FIFO expulsa la página más antigua en memoria; LRU la menos recientemente
    usada; Óptimo la que se volverá a usar más tarde (o nunca).
    """
    algoritmo = algoritmo.lower()
    if algoritmo not in ALGORITMOS_REEMPLAZO:
        raise ValueError(f"algoritmo desconocido: {algoritmo} (use fifo, lru u optimo)")
    if num_marcos <= 0:
        raise ValueError("el número de marcos debe ser positivo")
    if any(p < 0 for p in referencias):
        raise ValueError("las páginas deben ser enteros no negativos")

    marcos: list[int] = []  # orden de llegada (FIFO) o de uso, de menos a más reciente (LRU)
    pasos: list[tuple[int, bool, int | None, list[int]]] = []
    fallos = 0
    for i, pag in enumerate(referencias):
        expulsada = None
        fallo = pag not in marcos
        if fallo:
            fallos += 1
            if len(marcos) >= num_marcos:
                if algoritmo == "optimo":
                    futuro = referencias[i + 1:]
                    victima = max(marcos, key=lambda q: futuro.index(q) if q in futuro else len(futuro) + 1)
                else:  # fifo y lru: la víctima es la primera de la lista
                    victima = marcos[0]
                marcos.remove(victima)
                expulsada = victima
            marcos.append(pag)
        elif algoritmo == "lru":
            marcos.remove(pag)
            marcos.append(pag)
        pasos.append((pag, fallo, expulsada, list(marcos)))
    return ResultadoReemplazo(algoritmo, num_marcos, list(referencias), fallos, pasos)


def comparar_reemplazo(referencias: list[int], num_marcos: int) -> list[ResultadoReemplazo]:
    return [reemplazo_paginas(a, referencias, num_marcos) for a in ALGORITMOS_REEMPLAZO]


def reporte_reemplazo(resultados: list[ResultadoReemplazo]) -> str:
    r0 = resultados[0]
    lineas = [f"Reemplazo de páginas: {r0.num_marcos} marcos, {len(r0.referencias)} referencias",
              f"Cadena: {' '.join(map(str, r0.referencias))}",
              f"{'ALGORITMO':<10}{'FALLOS':>8}{'TASA':>9}"]
    for r in resultados:
        lineas.append(f"{r.algoritmo.upper():<10}{r.fallos:>8}{r.tasa_fallos:>8.1%}")
    mejor = min(resultados, key=lambda r: r.fallos)
    lineas.append(f"Menos fallos: {mejor.algoritmo.upper()}")
    return "\n".join(lineas)
