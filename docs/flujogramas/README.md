# Flujogramas de NexusOS-Sim (Mermaid)

Un archivo `.mmd` por proceso, derivados del caso (`README.md`), la propuesta, el plan y el código de `src/` (Fases 1 a 3).

| # | Archivo | Tipo | Qué muestra |
|---|---|---|---|
| 00 | `00_caso_nexusbank` | flowchart | Problemas de NexusBank → módulos que los resuelven → reporte final |
| 01 | `01_arquitectura_modular` | flowchart | Módulos, modo usuario vs. kernel y dependencias |
| 02 | `02_shell_bucle_principal` | flowchart | Arranque y bucle REPL del shell, manejo de errores |
| 03 | `03_sistema_archivos_simulado` | flowchart | `ls`, `pwd`, `mkdir`, `cd` |
| 04 | `04_ciclo_vida_proceso_5_estados` | state | Estados y transiciones legales del PCB |
| 05 | `05_gestor_procesos_crear_fork_exec_kill` | flowchart | `crear`, `fork`, `exec`, `kill` |
| 06 | `06_despacho_expropiar_bloquear` | flowchart | `despachar`, `expropiar`, `bloquear`, `desbloquear` |
| 07 | `07_planificador_no_expropiativo` | flowchart | FCFS, SJF y Prioridad (núcleo común) |
| 08 | `08_planificador_round_robin` | flowchart | Round Robin con quantum |
| 09 | `09_comando_planificar_comparativa` | flowchart | Comando `planificar` y tabla comparativa |
| 10 | `10_efecto_convoy_fcfs_vs_sjf_rr` | flowchart | Ejemplo 24/3/3: FCFS 17.00, SJF 3.00, RR 5.67 de espera |
| 11 | `11_demo_proceso_vs_hilo` | flowchart | `fork` (aislado) vs. hilos (compartido + Lock) |
| 12 | `12_productor_consumidor` | flowchart | Búfer acotado con mutex, `vacios` y `llenos` |
| 13 | `13_filosofos_comensales` | flowchart | Modo ingenuo (interbloqueo) vs. asimétrico |
| 14 | `14_interbloqueo_ingenuo_vs_asimetrico` | flowchart | Espera circular vs. ciclo roto (ideal para diapositiva) |
| 15 | `15_memoria_contigua_asignar_liberar` | flowchart | First/best/worst fit, fragmentación externa, fusión de huecos |
| 16 | `16_paginacion_asignar_liberar` | flowchart | Marcos, tabla de páginas, asignación atómica |
| 17 | `17_traduccion_direccion_virtual` | flowchart | Virtual → física y `SegmentationFault` |
| 18 | `18_comando_asignar_y_kill_memoria` | flowchart | Comando `asignar`, `kill` libera memoria, `memoria` |
| 19 | `19_hoja_de_ruta_fases_y_semanas` | flowchart | Fases 1–3 hechas y módulos pendientes (verde = hecho, amarillo = pendiente) |
| 20 | `20_secuencia_sesion_tipica` | sequence | Sesión de ejemplo Usuario ↔ Shell ↔ módulos |

## Cómo usarlos

* **Miro**: Apps → *Mermaid* (o `Diagramming → Mermaid`), pegar el contenido del `.mmd` y *Insert*; se convierte en figuras editables. Los diagramas tipo `flowchart` y `sequenceDiagram` son los mejor soportados; si un `stateDiagram` (04) no se importa, usar la imagen exportada.
* **Diapositivas**: abrir el contenido en <https://mermaid.live>, ajustar y exportar PNG o SVG. Por CLI:
  ```
  npx @mermaid-js/mermaid-cli -i 12_productor_consumidor.mmd -o 12_productor_consumidor.svg
  ```
  Para PNG de mayor resolución: `-e png -s 3 -b white`.
* **GitHub / Markdown**: pegar entre ```` ```mermaid ```` y ```` ``` ````.

Los diagramas grandes (02, 12, 13, 15) quedan mejor en una diapositiva dedicada; 14, 10 y 19 son los más compactos para presentar.
