# Guía de demostración de NexusOS-Sim

Guion paso a paso para mostrar **todo** el funcionamiento del simulador, siguiendo la historia del caso NexusBank.
Cada paso indica qué escribir, qué debe verse y qué decir. Duración sugerida: 12–15 minutos (los bloques 5 a 8 son los más
largos; si falta tiempo, vean la sección [Versión corta](#versión-corta-5-minutos)).

## 0. Preparación

| Requisito | Detalle |
|---|---|
| Python | 3.10 o superior (solo biblioteca estándar, no hay dependencias) |
| Carpeta | Raíz del repositorio (`SI421V_SW407V_Proyecto`) |
| Terminal | Ancha (≥ 100 columnas) y con letra grande para proyectar |

```bash
# 1) Verificar que todo está sano antes de exponer
cd tests && python -m unittest discover      # esperado: Ran 40 tests ... OK
cd ..

# 2) Iniciar el simulador
python src/main.py
```

Debe aparecer el banner y el prompt:

```
NexusOS-Sim v0.1 — escribe 'help' para ver los comandos.
nexus@sim:/$
```

**Convenciones de unidades** (mencionarlas al inicio): 1 unidad de tiempo simulada = **1 ms**; la memoria se mide en **B** (bytes).
Para salir en cualquier momento: `exit`.

> Si un comando falla, el shell imprime `error: ...` y **no se cae**; eso también es parte de la demostración.

---

## 1. Shell y sistema de archivos simulado (modo usuario)

**Mensaje:** *“Todo empieza en el shell: el usuario solo escribe comandos y el núcleo hace el trabajo.”*

| # | Comando | Resultado esperado |
|---|---|---|
| 1.1 | `help` | Lista de los 24 comandos con su sintaxis |
| 1.2 | `ls` | `bin/ home/ tmp/ var/` |
| 1.3 | `mkdir reportes` | Sin salida (crea el directorio) |
| 1.4 | `cd reportes` | El prompt cambia a `nexus@sim:/reportes$` |
| 1.5 | `pwd` | `/reportes` |
| 1.6 | `cd ..` | Vuelve a `nexus@sim:/$` |
| 1.7 | `comando_inexistente` | `comando_inexistente: comando no encontrado (escribe 'help')` |

---

## 2. Procesos: crear, fork, exec, estados y kill

**Mensaje:** *“Cada petición del banco es un proceso con su PCB y cinco estados posibles.”*

Creamos el caso clásico: una transferencia pesada y dos consultas de saldo, todas llegando en t = 0.

```
crear transferencia 24 0 0
crear saldo1 3 0 0
crear saldo2 3 0 0
ps
```

Sintaxis: `crear <nombre> <rafaga_ms> [prioridad] [llegada_ms]` (menor número de prioridad = mayor prioridad).

Salida esperada de `ps`:

```
 PID PPID NOMBRE       ESTADO       PC  RAF PRIO LLEG
   1    0 transferencia Listo         0   24    0    0
   2    0 saldo1       Listo         0    3    0    0
   3    0 saldo2       Listo         0    3    0    0
```

### 2.1 Ciclo de vida (los cinco estados)

| Paso | Comando | Estado resultante |
|---|---|---|
| a | `despachar` | PID 1: **Ejecución** (`CPU asignada al PID 1`) |
| b | `bloquear 1` | PID 1: **Bloqueado** (espera de E/S) |
| c | `desbloquear 1` | PID 1: **Listo** (al final de la cola) |
| d | `despachar` | Ahora el PID 2 pasa a **Ejecución** (cola FIFO de listos) |
| e | `expropiar 2` | PID 2 vuelve a **Listo** |
| f | `ps` | Verificar los estados después de cada paso |

> Mostrar una transición ilegal: con la CPU libre, `expropiar 1` → `error: el PID 1 no está en ejecución`.
> Las transiciones se validan: el simulador no permite saltarse el ciclo de vida.

### 2.2 `fork`, `exec` y `kill`

```
fork 1                  # fork: hijo PID 4 (padre 1)
exec 4 consulta 5       # exec: PID 4 ahora ejecuta 'consulta'
ps                      # PID 4 tiene PPID 1, nombre 'consulta' y ráfaga 5
kill 4                  # termina el proceso
ps                      # PID 4 aparece como Terminado
```

**Qué decir:** *`fork` copia el PCB (PC y registros aislados); `exec` reemplaza la imagen conservando PID y PPID; `kill` libera
CPU, colas y la memoria que tuviera el proceso.*

---

## 3. Planificación de CPU (efecto convoy)

**Mensaje:** *“El sistema legacy de NexusBank atiende por orden de llegada. Veamos qué le pasa a una consulta de saldo.”*

Con los tres procesos del paso 2 (sin terminar):

```
planificar fcfs
```

Salida esperada (extracto):

```
=== FCFS ===
Gantt: 0 | P1 | 24 | P2 | 27 | P3 | 30  (ms)
...
Espera promedio:    17.00 ms
Respuesta promedio: 17.00 ms
Retorno promedio:   27.00 ms
```

**Qué decir:** *las consultas de saldo (P2 y P3) esperan 24 ms y 27 ms detrás de la transferencia: es el efecto convoy.*

Luego comparar con los demás algoritmos:

```
planificar sjf
planificar rr 4
planificar prioridad
planificar todos 4
```

La tabla final de `planificar todos 4`:

```
=== Comparativa (tiempos promedio en ms) ===
ALGORITMO            ESPERA (ms) RESPUESTA (ms) RETORNO (ms)
FCFS                       17.00          17.00        27.00
SJF                         3.00           3.00        13.00
Round Robin (q=4)           5.67           3.67        15.67
Prioridad                  17.00          17.00        27.00
Menor espera promedio: SJF (3.00 ms)
```

| Lectura | Valor |
|---|---|
| Menor espera promedio | SJF: 3.00 ms frente a 17.00 ms de FCFS |
| Respuesta más pareja | Round Robin: 3.67 ms |
| Prioridad = FCFS aquí | La transferencia tiene prioridad 0 (la más alta) y entra primero |

### 3.1 (Opcional) Prioridad con diferencias reales

Reiniciar el simulador (`exit` y volver a ejecutar) y crear:

```
crear internacional 10 1 0
crear local 4 3 0
crear consulta 2 5 0
planificar todos 3
```

Aquí prioridad y FCFS atienden primero la transferencia internacional (prioridad 1), mientras SJF atiende primero la consulta
de 2 ms. Sirve para mostrar el riesgo de **inanición** de las prioridades bajas.

---

## 4. Procesos frente a hilos

**Mensaje:** *“Los procesos aíslan su memoria; los hilos la comparten, y por eso necesitan exclusión mutua.”*

```
hilos
```

Salida esperada (resumen):

```
[fork] padre PID 1 AX=10  |  hijo PID 2 (ppid 1) AX=99
[fork] los registros están aislados: el cambio del hijo no afecta al padre
[hilo-0] paso 1/3 -> contador=1
...
[hilos] contador final=12 (esperado 12): los hilos comparten memoria
```

**Qué decir:** *el hijo cambió su registro AX y el padre no lo vio. Los cuatro hilos incrementaron el mismo contador con un
`Lock`: el total es exactamente 12, sin condiciones de carrera (el problema de los saldos inconsistentes).*

---

## 5. Sincronización: productor-consumidor

**Mensaje:** *“Así se garantiza que dos operaciones no corrompan el mismo búfer o cuenta.”*

```
simular_productor 2 2 5 3
```

Parámetros: `[productores] [consumidores] [items por productor] [capacidad]`. También funciona sin argumentos.

Salida esperada (final):

```
[productor-0] produce 0  (búfer: 1/3)
[consumidor-0] consume 0  (búfer: 0/3)
...
Resumen: producidos=10 consumidos=10 máx. ocupación=1/3 -> CORRECTO
```

**Qué verificar:** `producidos = consumidos` y la ocupación máxima nunca supera la capacidad.

Prueba de capacidad mínima (búfer de 1 posición):

```
simular_productor 3 2 4 1
```

**Qué decir:** *el orden `vacios/llenos` antes que `mutex` evita el interbloqueo; el orden inverso lo causaría.*

---

## 6. Sincronización: filósofos comensales (interbloqueo)

**Mensaje:** *“Ahora provocamos un interbloqueo a propósito y mostramos cómo se evita.”*

### 6.1 Modo ingenuo (interbloqueo)

```
simular_filosofos ingenuo
```

Salida esperada (final):

```
[filósofo-4] INTERBLOQUEO: espera el tenedor 0 que nunca se liberará
...
Resumen: se detectó INTERBLOQUEO (espera circular)
```

**Qué decir:** *cada filósofo tomó su tenedor izquierdo y espera el derecho: se cumplen las 4 condiciones de Coffman.*

### 6.2 Modo asimétrico (solución)

```
simular_filosofos asimetrico
```

Salida esperada (final):

```
Resumen: sin interbloqueo; comidas por filósofo = [3, 3, 3, 3, 3]
```

**Qué decir:** *el último filósofo toma los tenedores en orden inverso: se rompe la espera circular y todos completan sus
3 comidas.* (El orden del log puede variar entre ejecuciones; el resumen no.)

---

## 7. Memoria contigua

**Mensaje:** *“Los servidores se quedan sin RAM. Veamos cómo se reparte y por qué se fragmenta.”*

Necesitamos procesos existentes (crear 4 si el simulador es nuevo):

```
crear a 5 0 0
crear b 5 0 0
crear c 5 0 0
crear d 5 0 0
```

```
asignar 1 250 contigua      # PID 1: 250 B en la dirección base 0
asignar 2 250 contigua      # ... base 250
asignar 3 250 contigua      # ... base 500
asignar 4 250 contigua      # ... base 750
memoria                     # mapa: 1000 B completos
```

### 7.1 Provocar fragmentación externa

```
liberar 1 contigua
liberar 3 contigua
memoria                     # dos huecos de 250 B no adyacentes
asignar 1 400 contigua
```

Resultado esperado:

```
error: fragmentación externa: hay 500 libres en total pero el hueco mayor es de 250 (se piden 400)
```

**Qué decir:** *hay 500 B libres pero no contiguos: el sistema distingue “memoria insuficiente” de “fragmentación externa”.
En `memoria` se ve `Fragmentación externa: 250 B`.*

### 7.2 Fusión de huecos

```
liberar 2 contigua
memoria                     # los huecos adyacentes se fusionan (0-749 libre)
```

---

## 8. Paginación y traducción de direcciones virtuales

**Mensaje:** *“Con paginación no hace falta espacio contiguo, y además cada proceso queda protegido.”*

La RAM paginada tiene 16 marcos de 256 B.

```
asignar 2 700 paginada     # PID 2: 3 páginas en los marcos [0, 1, 2]
asignar 3 300 paginada     # PID 3: 2 páginas en los marcos [3, 4]
memoria                    # marcos y tablas de páginas
```

En el mapa se observa la **fragmentación interna**: 300 B en 2 marcos (512 B) desperdician 212 B.

### 8.1 Traducción válida

```
traducir 3 299
```

```
PID 3: virtual 299 B -> física 1067 B
```

Cálculo para explicar: página = 299 // 256 = 1, desplazamiento = 299 % 256 = 43; la página 1 está en el marco 4;
física = 4 × 256 + 43 = **1067 B**.

### 8.2 Protección de memoria (Segmentation Fault)

```
traducir 3 300
traducir 3 99999
traducir 9 1
```

```
error: SEGMENTATION FAULT: dirección virtual 300 fuera del rango [0, 299] del PID 3
error: el PID 9 no tiene espacio de direcciones asignado
```

### 8.3 Asignación atómica y liberación

```
asignar 2 5000 paginada    # error: memoria insuficiente: se necesitan 20 marcos, libres ...
liberar 3 paginada         # devuelve los marcos
kill 2                     # kill también libera la memoria del proceso
memoria                    # todo libre otra vez
```

**Qué decir:** *si no alcanzan los marcos no se reserva ninguno (atómico), y `kill` devuelve toda la memoria al sistema.*

---

## 9. Manejo de errores (robustez)

Mostrar que el simulador nunca se cae:

| Comando | Resultado |
|---|---|
| `crear x` | `uso: crear <nombre> <rafaga> [prioridad] [llegada]` |
| `crear x abc` | `error: argumento debe ser un entero, se recibió 'abc'` |
| `planificar xyz` | `error: algoritmo desconocido: 'xyz' (fcfs, sjf, rr, prioridad)` |
| `kill 99` | `error: ...` (PID inexistente) |
| `traducir 9 1` | `error: el PID 9 no tiene espacio de direcciones asignado` |
| `exit` | `Apagando NexusOS-Sim...` |

---

## 10. Cierre

Terminar con `exit` y resumir con los tres hallazgos:

1. **FCFS** produce el efecto convoy: las consultas esperan 24 ms y 27 ms.
2. **SJF** minimiza la espera (3.00 ms) y **Round Robin** equilibra la respuesta (3.67 ms).
3. **Semáforos y orden asimétrico** eliminan el interbloqueo; la **paginación** asigna marcos no contiguos y protege la memoria.

Pendiente (hoja de ruta): reemplazo de páginas (FIFO/LRU/Óptimo), E/S y archivos con permisos, seguridad y sistemas distribuidos.

---

## Versión corta (5 minutos)

Para tiempos reducidos, ejecutar solo este bloque (equivale a la diapositiva de demostración):

```
crear transferencia 24 0 0
crear saldo1 3 0 0
crear saldo2 3 0 0
planificar todos 4
simular_filosofos ingenuo
simular_filosofos asimetrico
asignar 3 200 paginada
traducir 3 100
traducir 3 99999
exit
```

## Ejecución sin teclado (preparar la demo o respaldo)

El shell lee de la entrada estándar, de modo que se puede reproducir un guion completo:

```bash
printf 'crear transferencia 24 0 0\ncrear saldo1 3 0 0\ncrear saldo2 3 0 0\nplanificar todos 4\nexit\n' | python src/main.py
```

## Solución de problemas

| Síntoma | Causa y solución |
|---|---|
| `python` no se reconoce | Usar `py src/main.py` (Windows) o `python3 src/main.py` |
| Caracteres extraños (tildes) | El simulador fuerza UTF-8; usar una terminal moderna (Windows Terminal) |
| `error: el PID n ya terminó` al asignar | El proceso fue terminado con `kill`; crear uno nuevo |
| Los PID no coinciden con la guía | El simulador se reinicia en cada ejecución; los PID empiezan en 1 en orden de creación |
| El log de hilos o filósofos cambia | Es normal: el orden depende del planificador del sistema real; los resúmenes son deterministas |
