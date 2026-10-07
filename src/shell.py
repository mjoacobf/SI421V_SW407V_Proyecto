"""Shell (CLI) de NexusOS-Sim: interfaz de usuario del simulador.

Representa el modo usuario: el shell nunca toca las estructuras del "kernel"
directamente, solo despacha comandos registrados en ``self.comandos``.
"""
from __future__ import annotations

import os
import shlex
import sys
from typing import Callable, TextIO

from demo_hilos import demo_fork, demo_hilos
from memoria import ErrorMemoria, GestorMemoriaContigua, GestorPaginacion
from planificador import Planificador
from procesos import Estado, GestorProcesos
from sincronizacion import filosofos, productor_consumidor

PROMPT = "nexus@sim"
TAM_MEMORIA_CONTIGUA = 1000   # unidades de la RAM con particiones variables
NUM_MARCOS = 16               # RAM paginada: 16 marcos x 256 bytes
TAM_PAGINA = 256


class ErrorSistemaArchivos(Exception):
    """Error al operar sobre el sistema de archivos simulado."""


class SistemaArchivosSimulado:
    """Árbol de directorios en memoria (solo directorios, sin contenido)."""

    def __init__(self) -> None:
        self.raiz: dict = {}
        self.ruta: list[str] = []
        for d in ("bin", "home", "var", "tmp"):
            self.raiz[d] = {}

    def _dir_actual(self) -> dict:
        nodo = self.raiz
        for parte in self.ruta:
            nodo = nodo[parte]
        return nodo

    @property
    def pwd(self) -> str:
        return "/" + "/".join(self.ruta)

    def ls(self) -> list[str]:
        return sorted(self._dir_actual())

    def mkdir(self, nombre: str) -> None:
        if not nombre or "/" in nombre:
            raise ErrorSistemaArchivos(f"nombre inválido: '{nombre}'")
        actual = self._dir_actual()
        if nombre in actual:
            raise ErrorSistemaArchivos(f"'{nombre}' ya existe")
        actual[nombre] = {}

    def cd(self, destino: str) -> None:
        if destino == "/":
            self.ruta = []
        elif destino == "..":
            if self.ruta:
                self.ruta.pop()
        elif destino in self._dir_actual():
            self.ruta.append(destino)
        else:
            raise ErrorSistemaArchivos(f"no existe el directorio '{destino}'")


class Shell:
    """Bucle interactivo REPL del simulador."""

    def __init__(self, entrada: TextIO | None = None, salida: TextIO | None = None) -> None:
        self.entrada = entrada or sys.stdin
        self.salida = salida or sys.stdout
        self.fs = SistemaArchivosSimulado()
        self.activo = True
        # nombre -> (función, ayuda). Las fases siguientes agregan comandos aquí.
        self.comandos: dict[str, tuple[Callable[[list[str]], None], str]] = {}
        self.gestor = GestorProcesos()
        self.mem_contigua = GestorMemoriaContigua(TAM_MEMORIA_CONTIGUA)
        self.mem_paginada = GestorPaginacion(NUM_MARCOS, TAM_PAGINA)
        self._registrar_comandos_base()
        self._registrar_comandos_procesos()
        self._registrar_comandos_sincronizacion()
        self._registrar_comandos_memoria()

    # -- utilidades -------------------------------------------------------
    def imprimir(self, texto: str = "") -> None:
        print(texto, file=self.salida)

    def registrar(self, nombre: str, funcion: Callable[[list[str]], None], ayuda: str) -> None:
        self.comandos[nombre] = (funcion, ayuda)

    def _registrar_comandos_base(self) -> None:
        self.registrar("help", self.cmd_help, "help              Muestra esta ayuda")
        self.registrar("clear", self.cmd_clear, "clear             Limpia la pantalla")
        self.registrar("exit", self.cmd_exit, "exit              Apaga el simulador")
        self.registrar("ls", self.cmd_ls, "ls                Lista el directorio actual")
        self.registrar("mkdir", self.cmd_mkdir, "mkdir <nombre>     Crea un directorio simulado")
        self.registrar("cd", self.cmd_cd, "cd <dir>           Cambia de directorio (.. y / soportados)")
        self.registrar("pwd", self.cmd_pwd, "pwd               Muestra el directorio actual")

    def _registrar_comandos_procesos(self) -> None:
        self.registrar("ps", self.cmd_ps, "ps                Lista la tabla de procesos")
        self.registrar("crear", self.cmd_crear,
                       "crear <nombre> <rafaga> [prioridad] [llegada]   Crea un proceso")
        self.registrar("fork", self.cmd_fork, "fork <pid>        Duplica un proceso")
        self.registrar("exec", self.cmd_exec, "exec <pid> <nombre> [rafaga]   Reemplaza la imagen de un proceso")
        self.registrar("kill", self.cmd_kill, "kill <pid>        Termina un proceso")
        self.registrar("despachar", self.cmd_despachar, "despachar         Asigna la CPU al primer proceso Listo")
        self.registrar("expropiar", lambda a: self._con_pid(a, "expropiar", self.gestor.expropiar),
                       "expropiar <pid>   EJECUCION -> LISTO")
        self.registrar("bloquear", lambda a: self._con_pid(a, "bloquear", self.gestor.bloquear),
                       "bloquear <pid>    EJECUCION -> BLOQUEADO")
        self.registrar("desbloquear", lambda a: self._con_pid(a, "desbloquear", self.gestor.desbloquear),
                       "desbloquear <pid> BLOQUEADO -> LISTO")
        self.registrar("planificar", self.cmd_planificar,
                       "planificar [fcfs|sjf|rr|prioridad|todos] [quantum]   Compara algoritmos de CPU")
        self.registrar("hilos", self.cmd_hilos, "hilos             Demo procesos (fork) vs. hilos (threading)")

    # -- comandos de procesos ---------------------------------------------
    @staticmethod
    def _entero(texto: str, campo: str) -> int:
        try:
            return int(texto)
        except ValueError:
            raise ValueError(f"{campo} debe ser un entero, se recibió '{texto}'") from None

    def _con_pid(self, args: list[str], nombre: str, accion: Callable[[int], None]) -> None:
        if len(args) != 1:
            self.imprimir(f"uso: {nombre} <pid>")
            return
        accion(self._entero(args[0], "pid"))

    def cmd_ps(self, args: list[str]) -> None:
        if not self.gestor.tabla:
            self.imprimir("(no hay procesos)")
            return
        self.imprimir(self.gestor.tabla_texto())

    def cmd_crear(self, args: list[str]) -> None:
        if not 2 <= len(args) <= 4:
            self.imprimir("uso: crear <nombre> <rafaga> [prioridad] [llegada]")
            return
        nums = [self._entero(a, "argumento") for a in args[1:]]
        p = self.gestor.crear(args[0], *nums)
        self.imprimir(f"proceso creado: PID {p.pid} ({p.nombre})")

    def cmd_fork(self, args: list[str]) -> None:
        if len(args) != 1:
            self.imprimir("uso: fork <pid>")
            return
        hijo = self.gestor.fork(self._entero(args[0], "pid"))
        self.imprimir(f"fork: hijo PID {hijo.pid} (padre {hijo.ppid})")

    def cmd_exec(self, args: list[str]) -> None:
        if not 2 <= len(args) <= 3:
            self.imprimir("uso: exec <pid> <nombre> [rafaga]")
            return
        rafaga = self._entero(args[2], "rafaga") if len(args) == 3 else None
        p = self.gestor.exec(self._entero(args[0], "pid"), args[1], rafaga)
        self.imprimir(f"exec: PID {p.pid} ahora ejecuta '{p.nombre}'")

    def cmd_kill(self, args: list[str]) -> None:
        self._con_pid(args, "kill", self._terminar)

    def _terminar(self, pid: int) -> None:
        """Termina el proceso y devuelve al SO toda la memoria que tenía."""
        self.gestor.terminar(pid)
        for gestor_mem in (self.mem_contigua, self.mem_paginada):
            try:
                gestor_mem.liberar(pid)
            except ErrorMemoria:
                pass

    def cmd_despachar(self, args: list[str]) -> None:
        p = self.gestor.despachar()
        self.imprimir(f"CPU asignada al PID {p.pid}" if p else "no hay procesos Listos")

    def cmd_planificar(self, args: list[str]) -> None:
        algoritmo = args[0] if args else "todos"
        quantum = self._entero(args[1], "quantum") if len(args) > 1 else 2
        procesos = [p for p in self.gestor.listar() if p.estado is not Estado.TERMINADO]
        if not procesos:
            self.imprimir("no hay procesos para planificar (usa 'crear')")
            return
        plan = Planificador(procesos)
        if algoritmo == "todos":
            resultados = plan.todos(quantum)
            for r in resultados:
                self.imprimir(plan.reporte(r))
                self.imprimir()
            self.imprimir(plan.comparativa(resultados))
        else:
            self.imprimir(plan.reporte(plan.ejecutar(algoritmo, quantum)))

    def cmd_hilos(self, args: list[str]) -> None:
        demo_fork(self.imprimir)
        demo_hilos(imprimir=self.imprimir)

    # -- sincronización ---------------------------------------------------
    def _registrar_comandos_sincronizacion(self) -> None:
        self.registrar("simular_productor", self.cmd_productor,
                       "simular_productor [productores] [consumidores] [items] [capacidad]")
        self.registrar("simular_filosofos", self.cmd_filosofos,
                       "simular_filosofos [asimetrico|ingenuo]   Cena de filósofos")

    def cmd_productor(self, args: list[str]) -> None:
        valores = [self._entero(a, "argumento") for a in args[:4]]
        productor_consumidor(*valores, log=self.imprimir)

    def cmd_filosofos(self, args: list[str]) -> None:
        modo = args[0] if args else "asimetrico"
        if modo not in ("asimetrico", "ingenuo"):
            self.imprimir("uso: simular_filosofos [asimetrico|ingenuo]")
            return
        filosofos(asimetrico=(modo == "asimetrico"), log=self.imprimir)

    # -- memoria ----------------------------------------------------------
    def _registrar_comandos_memoria(self) -> None:
        self.registrar("memoria", self.cmd_memoria, "memoria           Muestra el mapa de memoria (contigua y paginada)")
        self.registrar("asignar", self.cmd_asignar,
                       "asignar <pid> <tamano> [contigua|paginada]   Reserva memoria para un proceso")
        self.registrar("liberar", self.cmd_liberar, "liberar <pid> [contigua|paginada]   Libera la memoria de un proceso")
        self.registrar("traducir", self.cmd_traducir, "traducir <pid> <dir_virtual>   Dirección virtual -> física")

    def cmd_memoria(self, args: list[str]) -> None:
        self.imprimir(self.mem_contigua.mapa_texto())
        self.imprimir()
        self.imprimir(self.mem_paginada.mapa_texto())

    def _gestor_mem(self, tipo: str):
        if tipo == "contigua":
            return self.mem_contigua
        if tipo == "paginada":
            return self.mem_paginada
        raise ValueError("el tipo de memoria debe ser 'contigua' o 'paginada'")

    def cmd_asignar(self, args: list[str]) -> None:
        if not 2 <= len(args) <= 3:
            self.imprimir("uso: asignar <pid> <tamano> [contigua|paginada]")
            return
        pid, tamano = self._entero(args[0], "pid"), self._entero(args[1], "tamano")
        tipo = args[2] if len(args) == 3 else "paginada"
        gestor_mem = self._gestor_mem(tipo)
        if self.gestor.obtener(pid).estado is Estado.TERMINADO:
            self.imprimir(f"el PID {pid} ya terminó")
            return
        resultado = gestor_mem.asignar(pid, tamano)
        if tipo == "contigua":
            self.imprimir(f"PID {pid}: {tamano} u. en la dirección base {resultado}")
        else:
            self.imprimir(f"PID {pid}: {len(resultado)} páginas en los marcos {resultado.marcos}")

    def cmd_liberar(self, args: list[str]) -> None:
        if not 1 <= len(args) <= 2:
            self.imprimir("uso: liberar <pid> [contigua|paginada]")
            return
        self._gestor_mem(args[1] if len(args) == 2 else "paginada").liberar(self._entero(args[0], "pid"))

    def cmd_traducir(self, args: list[str]) -> None:
        if len(args) != 2:
            self.imprimir("uso: traducir <pid> <dir_virtual>")
            return
        pid, virtual = self._entero(args[0], "pid"), self._entero(args[1], "dir_virtual")
        fisica = self.mem_paginada.traducir_direccion(pid, virtual)
        self.imprimir(f"PID {pid}: virtual {virtual} -> física {fisica}")

    # -- comandos base ----------------------------------------------------
    def cmd_help(self, args: list[str]) -> None:
        self.imprimir("Comandos disponibles:")
        for _, (_, ayuda) in sorted(self.comandos.items()):
            self.imprimir("  " + ayuda)

    def cmd_clear(self, args: list[str]) -> None:
        if self.salida is sys.stdout and sys.stdout.isatty():
            os.system("cls" if os.name == "nt" else "clear")
        else:
            self.imprimir("\n")

    def cmd_exit(self, args: list[str]) -> None:
        self.imprimir("Apagando NexusOS-Sim...")
        self.activo = False

    def cmd_ls(self, args: list[str]) -> None:
        for nombre in self.fs.ls():
            self.imprimir(nombre + "/")

    def cmd_mkdir(self, args: list[str]) -> None:
        if len(args) != 1:
            self.imprimir("uso: mkdir <nombre>")
            return
        self.fs.mkdir(args[0])

    def cmd_cd(self, args: list[str]) -> None:
        if len(args) != 1:
            self.imprimir("uso: cd <directorio>")
            return
        self.fs.cd(args[0])

    def cmd_pwd(self, args: list[str]) -> None:
        self.imprimir(self.fs.pwd)

    # -- bucle principal --------------------------------------------------
    def ejecutar_linea(self, linea: str) -> None:
        try:
            partes = shlex.split(linea)
        except ValueError as e:
            self.imprimir(f"error de sintaxis: {e}")
            return
        if not partes:
            return
        nombre, args = partes[0], partes[1:]
        if nombre not in self.comandos:
            self.imprimir(f"{nombre}: comando no encontrado (escribe 'help')")
            return
        try:
            self.comandos[nombre][0](args)
        except Exception as e:  # el shell (modo usuario) nunca debe caerse por un error del kernel
            self.imprimir(f"error: {e}")

    def ejecutar(self) -> None:
        self.imprimir("NexusOS-Sim v0.1 — escribe 'help' para ver los comandos.")
        while self.activo:
            self.salida.write(f"{PROMPT}:{self.fs.pwd}$ ")
            self.salida.flush()
            linea = self.entrada.readline()
            if linea == "":  # EOF
                break
            self.ejecutar_linea(linea.strip())
