# IMPLEMENTATIONS_FASE_3 — Concurrencia y Memoria

Cubre las Semanas 5 y 6 del [PLAN_IMPLEMENTACIÓN_1](PLAN_IMPLEMENTACIÓN_1.md). Corresponde a los Módulos 2 y 3 (parcial) de la propuesta.

## Semana 5 — Sincronización (`src/sincronizacion.py`)

### Productor-Consumidor
`productor_consumidor(n_productores, n_consumidores, items_por_productor, capacidad, log, retardo)`
* Búfer acotado (`deque`) protegido por `mutex = Semaphore(1)`, con `vacios = Semaphore(capacidad)` y `llenos = Semaphore(0)`.
* Orden de adquisición `vacios/llenos` → `mutex` (el inverso causaría interbloqueo).
* Cada consumidor recibe una cuota de consumos (el total se reparte con `divmod`), así todos los hilos terminan sin “pastillas de veneno”.
* Devuelve `ResultadoProductorConsumidor`; `correcto` verifica que lo consumido es exactamente lo producido y que la ocupación máxima nunca superó la capacidad.

### Filósofos comensales
`filosofos(n=5, comidas=3, asimetrico=True, log, espera_max)`
* **Modo ingenuo (`asimetrico=False`)**: todos toman primero el tenedor izquierdo; una `Barrier` garantiza que todos lo tengan antes de pedir el derecho, produciendo el interbloqueo de forma **determinista**. Se detecta con `acquire(timeout)` y los filósofos liberan y abandonan (la simulación nunca se cuelga).
* **Modo asimétrico (`asimetrico=True`)**: el último filósofo toma los tenedores en orden inverso, rompiendo la espera circular → interbloqueo imposible. Todos completan sus comidas.
* `_logger_seguro` serializa la salida de los hilos con un Lock.

### Shell
`simular_productor [productores] [consumidores] [items] [capacidad]` y `simular_filosofos [asimetrico|ingenuo]`; el log se imprime conforme los hilos avanzan.

## Semana 6 — Memoria (`src/memoria.py`)

### Asignación contigua — `GestorMemoriaContigua(tamano_total, estrategia)`
* Lista de `Bloque` (ocupado por PID o libre) con estrategias `first`, `best` y `worst` fit.
* `asignar` distingue **memoria insuficiente** de **fragmentación externa** (hay espacio total pero no contiguo) en el mensaje de error.
* `liberar` fusiona huecos adyacentes. `fragmentacion_externa() = libre total − hueco mayor`. `mapa_texto()` para visualizar.

### Paginación — `GestorPaginacion(num_marcos, tam_pagina)`
* RAM dividida en marcos; cada proceso tiene una `TablaPaginas` (página → marco). Los marcos asignados **no necesitan ser contiguos**.
* La asignación es atómica: si no alcanzan los marcos, no se reserva ninguno.
* `fragmentacion_interna(pid)` y `mapa_texto()` (marcos + tablas de páginas).
* **`traducir_direccion(proceso, dir_virtual)`**: acepta un `Proceso` o un PID; calcula `marco·tam_página + desplazamiento`. Lanza `SegmentationFault` si la dirección es negativa, ≥ tamaño lógico, o el proceso no tiene espacio asignado.

### Shell
`memoria` (mapa de ambos gestores), `asignar <pid> <tamano> [contigua|paginada]`, `liberar <pid> [tipo]`, `traducir <pid> <dir_virtual>`. `kill` ahora también libera la memoria del proceso. Configuración: 1000 unidades contiguas; 16 marcos × 256 bytes.

## Pruebas (15 nuevas; 38 en total)
* `tests/test_sincronizacion.py` (5): varias configuraciones de productor-consumidor (incluida capacidad 1), filósofos asimétricos repetidos 5 veces sin interbloqueo, filósofos ingenuos interbloqueados, validación de parámetros.
* `tests/test_memoria.py` (10): fragmentación externa, fusión de huecos, first/best/worst fit con casos distinguibles, errores; traducción, marcos no contiguos, segmentation fault, fragmentación interna, atomicidad y liberación.
* La suite se ejecutó 6 veces seguidas sin fallos para descartar inestabilidad en las pruebas con hilos.

## Notas
* El plan no incluye aún reemplazo de páginas (FIFO/LRU/Óptimo, Módulo 3 de la propuesta, semana 7) ni memoria virtual con fallos de página; son el siguiente paso natural.
* Una corrección durante la fase: una prueba de paginación tenía mal calculados los marcos esperados (error del test, no del código).
