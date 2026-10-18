# IMPLEMENTATIONS_OBSERVACIONES — Mejoras tras la revisión del profesor (13-10-2026)

Recoge los cambios hechos en el **sistema**, los **flujogramas** y las **diapositivas** a partir de
[`Observaciones_y_sugerencias_13-10-2026.md`](../Observaciones_y_sugerencias_13-10-2026.md).
Ninguna de las observaciones cambia los algoritmos ni los resultados: son mejoras de formato,
unidades y narrativa.

## 1. Resumen de observaciones y cómo se atendió

| # | Observación | Atención en el sistema | Atención en diapositivas / flujogramas |
|---|---|---|---|
| 1 | Todo flujograma debe tener círculo de inicio (verde) y de fin (rojo); las salidas deben converger en un único fin | Flujogramas Mermaid `.mmd` con nodos `Inicio`/`Fin` y clases de color | Diapositivas 6 y 8 con círculos *Inicio* (verde) y *Fin* (rojo) |
| 2 | Los diagramas de relaciones, de estructura o acompañados de tabla/descripción **no** llevan inicio/fin | No se tocaron: `00`, `01`, `04`, `10`, `14`, `19`, `20` | Diapositivas 7, 9, 13, 14, 16 y 17 sin marcadores |
| 3 | Poner unidades en las métricas (tiempo y memoria) | `planificador.py` en **ms**; `memoria.py` y `shell.py` en **B** (bytes) | Diapositivas 10, 11, 12, 13, 14, 15, 16, 17, 20 y 21 |
| 4 | Nombrar ejes X e Y en las gráficas y añadir leyendas | Los reportes imprimen una leyenda de abreviaturas | Diapositivas 11 y 12: ejes con título y leyenda |
| 5 | Narrativa (*storytelling*) enlazando una diapositiva con otra | — | Frase de enlace visible al pie de las diapositivas 2–16 y 18–21, y en las notas del orador |
| 6 | Que el cliente (NexusBank) entienda el flujo | — | Frases de enlace en lenguaje de negocio; la demostración usa el caso del banco |

## 2. Cambios en el sistema (`src/`)

Convención adoptada: **1 unidad de tiempo simulada = 1 milisegundo (ms)** y **1 unidad de memoria = 1 byte (B)**.
La constante `UNIDAD_TIEMPO = "ms"` está en `src/planificador.py`.

| Archivo | Cambio |
|---|---|
| `src/planificador.py` | Nueva constante `UNIDAD_TIEMPO`. `reporte()` imprime los promedios con unidad (`17.00 ms`), la línea del Gantt termina en `(ms)` y se agrega la leyenda `LLEG, RAF, INI, FIN, RET, ESP, RESP`. `comparativa()` rotula las columnas `ESPERA (ms)`, `RESPUESTA (ms)`, `RETORNO (ms)` y reporta `Menor espera promedio: SJF (3.00 ms)`. |
| `src/memoria.py` | `mapa_texto()` de la memoria contigua usa `B` en lugar de `u.` (`1000 B`, `600 B`, libre total, hueco mayor y fragmentación externa en B) y añade `Leyenda: B = bytes`. El mapa paginado muestra `256 B`, marcos libres y fragmentación interna en B. |
| `src/shell.py` | `asignar` informa `N B en la dirección base X (B = bytes)`; `traducir` informa `virtual V B -> física F B`; la ayuda de `crear` y `asignar` indica `rafaga_ms`, `llegada_ms` y `tamano_B`. |
| `tests/test_planificador.py`, `tests/test_memoria.py` | 2 pruebas nuevas verifican que los reportes llevan unidades: **40 pruebas** en total (antes 38). |

### Salida de ejemplo (`planificar todos 4`)

```
=== Comparativa (tiempos promedio en ms) ===
ALGORITMO            ESPERA (ms) RESPUESTA (ms) RETORNO (ms)
FCFS                       17.00          17.00        27.00
SJF                         3.00           3.00        13.00
Round Robin (q=4)           5.67           3.67        15.67
Prioridad                  17.00          17.00        27.00
Menor espera promedio: SJF (3.00 ms)
```

## 3. Cambios en los flujogramas (`docs/flujogramas/`)

* Nuevos nodos circulares **`Inicio`** (clase `inicio`, verde `#2e7d32`) y **`Fin`** (clase `fin`, rojo `#c62828`).
* Todas las ramas terminales (errores incluidos) convergen en un único `Fin` por flujo.
* Flujogramas con marcadores: `02, 03, 05, 06, 07, 08, 09, 11, 12, 13, 15, 16, 17, 18`
  (los que tienen varios subprocesos independientes, como `05`, `06`, `15`, `16` y `18`, tienen un par inicio/fin por subproceso).
* Sin marcadores (estructura, relaciones, estados o descripción): `00, 01, 04, 10, 14, 19, 20`.
* `02`: los errores regresan al bucle y el único `Fin` está en la salida (EOF o `exit`), lo que refleja el código real.
* `10` y `18`: unidades en milisegundos / bytes.

## 4. Cambios en las diapositivas (`SI421V_SW407V_Presentacion_Proyecto.pptx`)

| Diapositiva | Cambio |
|---|---|
| 6 — Flujograma principal | Círculo verde *Inicio* con un tronco que alimenta los cinco problemas; círculo rojo *Fin* después de *Reporte*. Las filas se reacomodaron para dar espacio. |
| 7 — Arquitectura | "40 pruebas automatizadas". Sin marcadores (es un diagrama de relaciones). |
| 8 — Flujo del shell | Círculo *Inicio* antes de `python src/main.py`; las tres salidas (apagado, comando no encontrado y error) convergen en un círculo *Fin*. |
| 10 — Algoritmos | "cada q ms (q = quantum)". |
| 11 — Efecto convoy | Esperas en ms (`17.00 ms`), duraciones en ms (`24 ms`, `3 ms`), rótulos **Eje X: tiempo (ms)** y **Eje Y: algoritmo**. |
| 12 — Resultados | Encabezados `Espera (ms)`, `Respuesta (ms)`, `Retorno (ms)`; gráfica con título "(ms)", **eje X = Algoritmo de planificación**, **eje Y = Tiempo promedio (ms)**, leyenda `Espera (ms)` / `Respuesta (ms)` y leyenda de abreviaturas (FCFS, SJF, RR, ms). |
| 13 — Productor-consumidor | Cantidades en ítems (capacidad N ítems; "10 de 10 ítems"). |
| 14 — Filósofos | "3 comidas" y leyenda `Fi` = filósofo, `Ti` = tenedor. |
| 15 — Memoria | `1000 B`, `600 B`, `300 B`, `100 B`, `256 B` y leyendas de bloques y marcos. |
| 16 — Traducción | Resultados en B (`física 100 B`, rango `[0, 199] B`). Sin marcadores (el flujo va con tabla). |
| 17 — Demostración | Salida actualizada con la comparativa en ms y direcciones en B. |
| 18 | "40 pruebas automatizadas aprobadas". |
| 20, 21 | Valores con unidad (`3.00 ms`, `3.67 ms`, `24 ms y 27 ms`, "40 pruebas"). |
| 2–16, 18–21 | **Frase de enlace** (storytelling) al pie, repetida en las notas del orador como "Enlace con la siguiente diapositiva". |

### Guion de enlaces (storytelling)

1. Objetivos → "Para saber hacia dónde vamos, primero conozcamos al banco que nos pidió ayuda: NexusBank."
2. Contexto → "Con estos cinco problemas: ¿cómo probar una solución sin arriesgar dinero real?"
3. Alternativa → "La respuesta fue construir un simulador. Veamos qué puede hacer."
4. Características → "Cada capacidad responde a un problema del banco; así se conecta todo."
5. Flujograma principal → "Ahora abramos el simulador y veamos cómo está organizado por dentro."
6. Arquitectura → "Todo empieza en el shell: así recibe y procesa cada orden del usuario."
7. Shell → "Cada orden crea procesos; veamos cómo los representa el sistema."
8. PCB → "Con los procesos listos, ¿quién decide cuál usa primero el procesador? El planificador."
9. Algoritmos → "Veamos qué pasa cuando una transferencia pesada llega antes que dos consultas de saldo."
10. Convoy → "¿Cuánto mejora cada algoritmo? Comparemos los números."
11. Resultados → "Pero atender rápido no basta: dos procesos no deben tocar la misma cuenta a la vez."
12. Productor-consumidor → "Y cuando varios procesos compiten por los mismos recursos, puede aparecer el interbloqueo."
13. Filósofos → "Con la CPU y la concurrencia bajo control, falta resolver dónde viven los datos: la memoria."
14. Memoria → "Y cada proceso debe ver solo su propia memoria: así se protege el saldo de cada cliente."
15. Traducción → "Veamos todo esto funcionando en vivo."
16. Calidad → "Entonces, ¿qué falta por construir? Esta es nuestra hoja de ruta."
17. Hoja de ruta → "Con lo aprendido, esto es lo que le recomendamos a NexusBank."
18. Recomendaciones → "En resumen, esto es lo que logramos."
19. Conclusiones → "Gracias por acompañarnos en esta historia."

## 5. Decisiones y pendientes

* El profesor pidió que las salidas de la diapositiva 8 converjan en un único *Fin*; se siguió esa indicación.
  El diagrama `02_shell_bucle_principal.mmd` es más fiel al código: los errores regresan al prompt y solo EOF o `exit` terminan el shell.
* La unidad de tiempo (ms) es una convención del simulador; si el docente prefiere segundos, basta cambiar `UNIDAD_TIEMPO`
  y los textos de las diapositivas 10–12, 17, 20 y 21.
* Ajustar el tiempo de exposición cuando el profesor lo indique (aún no confirmado en la revisión).
