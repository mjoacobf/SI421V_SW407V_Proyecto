# IMPLEMENTATIONS_FASE_2 — Gestión del Procesador

Cubre las Semanas 3 y 4 del [PLAN_IMPLEMENTACIÓN_1](PLAN_IMPLEMENTACIÓN_1.md). Corresponde al Módulo 1 de la propuesta.

## Semana 3 — Procesos e hilos (`src/procesos.py`)

* **`Estado`** (enum): Nuevo, Listo, Ejecución, Bloqueado, Terminado.
* **`TRANSICIONES`**: grafo de transiciones legales del modelo de 5 estados; `Proceso.cambiar_estado` lanza `ErrorProceso` ante una transición ilegal.
* **`Proceso` (PCB)**: `pid`, `ppid`, `nombre`, `estado`, `pc`, `registros` (AX–DX), y los datos de planificación `rafaga`, `prioridad` (menor = más prioritaria), `llegada`. Valida ráfaga > 0 y llegada ≥ 0.
* **`GestorProcesos`**: tabla de procesos, colas `listos` y `bloqueados`, proceso `en_ejecucion` (la CPU es única).
  * `crear` (Nuevo→Listo), `despachar`, `expropiar`, `bloquear`, `desbloquear`, `terminar`.
  * **`fork(pid)`**: copia profunda del PCB (PC y registros) con PID nuevo y `ppid` = padre. Los registros quedan aislados entre padre e hijo.
  * **`exec(pid, nombre, rafaga)`**: conserva PID/PPID; reinicia PC y registros y cambia la imagen.
  * `terminar` actúa como `kill`: fuerza Terminado desde Listo/Bloqueado/Ejecución (señal del kernel, por eso no sigue el grafo normal).
* **`src/demo_hilos.py`**: demuestra la diferencia proceso/hilo.
  * `demo_fork`: el hijo modifica `AX` y el padre no lo ve.
  * `demo_hilos`: N hilos (`threading`) incrementan un contador **compartido** protegido por `Lock`; el total final coincide con el esperado.
  * Los hilos no imprimen directamente: acumulan líneas y las imprime el hilo principal (salida limpia, evita mezclar texto).

## Semana 4 — Planificador (`src/planificador.py`)

* **`Planificador(procesos)`** trabaja sobre los atributos de los procesos **sin modificarlos**, así una misma lista se evalúa con todos los algoritmos.
* Algoritmos: `fcfs()`, `sjf()` (no expropiativo), `round_robin(quantum)`, `prioridad()` (no expropiativo, menor número = mayor prioridad).
* Manejo de **CPU ociosa** cuando ningún proceso ha llegado.
* Desempates por llegada y luego PID. En Round Robin, un proceso que llega justo al terminar un quantum entra a la cola antes que el expropiado.
* **`Resultado`**: diagrama de Gantt `(pid, inicio, fin)` (segmentos contiguos del mismo proceso se fusionan), métricas por proceso (`MetricasProceso`: inicio, finalización, retorno, **espera**, **respuesta**) y promedios.
* **Reportes**: `Planificador.reporte(r)` (tabla + Gantt + promedios) y `Planificador.comparativa(resultados)` (tabla comparativa y algoritmo con menor espera).

Validación con el ejemplo clásico de ráfagas 24/3/3 en t=0:

| Algoritmo | Espera prom. | Respuesta prom. |
|---|---|---|
| FCFS | 17.00 | 17.00 |
| SJF | 3.00 | 3.00 |
| Round Robin (q=4) | 5.67 | 3.67 |

Ilustra el efecto convoy descrito en el caso NexusBank: la transacción pesada (24) bloquea las consultas de saldo (3) bajo FCFS.

## Integración con el shell (`src/shell.py`)

Nuevos comandos: `ps`, `crear <nombre> <rafaga> [prioridad] [llegada]`, `fork`, `exec`, `kill`, `despachar`, `expropiar`, `bloquear`, `desbloquear`, `planificar [fcfs|sjf|rr|prioridad|todos] [quantum]`, `hilos`.
`planificar` evalúa los procesos no terminados de la tabla.

## Pruebas (19 nuevas; 23 en total al cierre de la fase)

* `tests/test_procesos.py` (9): ciclo de vida, CPU ocupada, transición ilegal, aislamiento de `fork`, `exec`, PID inexistente/terminado, `kill` desde cada cola, hilos sin pérdida de incrementos.
* `tests/test_planificador.py` (10): valores del ejemplo clásico para FCFS/SJF/RR, regla de llegada en RR, prioridad, CPU ociosa, no mutación, invariantes (ráfagas totales, retorno = espera + ráfaga, sin solapamientos) en los 4 algoritmos, errores y reportes.

## Notas
* En la prueba de la CLI con procesos de igual prioridad, `Prioridad` coincide con FCFS (desempate por llegada); es el comportamiento esperado.
* El planificador es una simulación de tiempos; no cambia aún los estados de los PCB (queda como posible integración futura).
