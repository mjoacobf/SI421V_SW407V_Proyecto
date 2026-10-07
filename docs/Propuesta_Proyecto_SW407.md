### UNIVERSIDAD NACIONAL DE INGENIERÍA

Facultad de Ingeniería Industrial y de Sistemas — Escuela Profesional de Ingeniería de Software *Curso: SW407 — Sistemas Operativos*

# PROPUESTA DE PROYECTO INTEGRADOR

### "SO-Sim: Simulador Educativo de un Sistema Operativo"

## I. Presentación y justificación

El curso SW407 (4.º ciclo, 3 créditos, 4 horas semanales) desarrolla los fundamentos de los sistemas operativos y exige, en su componente práctico, simular mediante programas los algoritmos estudiados en cada unidad. El presente proyecto integrador articula esas actividades de laboratorio, ya previstas en el sílabo, en un único producto acumulativo: un simulador de sistema operativo construido por módulos a lo largo de las 16 semanas lectivas, en lugar de ejercicios aislados por sesión.

De este modo, cada avance reutiliza y amplía el trabajo anterior, refuerza la comprensión de cómo interactúan los subsistemas de un SO real y da a los dos exámenes (parcial y final) y a las cuatro evaluaciones prácticas exigidas por el sílabo (2 prácticas escritas/laboratorio + 2 trabajos domiciliarios) un hilo conductor común.

## II. Objetivos

### Objetivo general

Diseñar, implementar y sustentar en equipo un simulador funcional que reproduzca, mediante programas en C y/o Python, los principales algoritmos y mecanismos de gestión de procesos, memoria, entrada/salida, archivos, seguridad y comunicación distribuida cubiertos en el sílabo de SW407.

### Objetivos específicos

- Implementar y comparar algoritmos de planificación de procesos (FCFS, SJF, Round Robin, Prioridad).
- Resolver un problema clásico de sincronización usando semáforos o mutex, evitando condiciones de carrera.
- Simular la gestión de memoria (asignación contigua, paginación) y comparar algoritmos de reemplazo de páginas (FIFO, LRU, Óptimo).
- Simular operaciones básicas de entrada/salida y un sistema de archivos simplificado con permisos.
- Incorporar un mecanismo simple de autenticación/control de acceso y cifrado, y una demostración de comunicación entre procesos distribuidos.
- Documentar y sustentar oralmente el diseño, la implementación y los resultados obtenidos.
## III. Organización del trabajo

Equipos de 3 a 4 integrantes, constituidos en la semana 1. Lenguajes sugeridos: C (para los módulos de procesos, hilos y sincronización, en línea con las actividades del sílabo) y Python (para los módulos de planificación, memoria y análisis de resultados); un equipo puede usar un solo lenguaje si lo justifica en su ficha técnica. Se recomienda el uso de un repositorio Git para evidenciar la participación individual, criterio considerado en la rúbrica.

## IV. Módulos del simulador

El proyecto se construye incrementalmente en seis módulos, cada uno anclado a la unidad del sílabo correspondiente:

|Módulo|Contenido técnico (según sílabo)|Resultado esperado|
|---|---|---|
|1|Procesos, hilos y planificación (fork/exec, threading, FCFS, SJF, Round Robin, Prioridad).|Planificador que recibe una lista de procesos y calcula tiempos de espera/respuesta por algoritmo.|
|2|Sincronización: semáforos, mutex, un problema clásico (productor-consumidor, filósofos o lectores-escritores).|Programa concurrente sin condiciones de carrera ni interbloqueo, con evidencia de ejecución correcta.|
|3|Gestión de memoria: asignación contigua, fragmentación, paginación y algoritmos de reemplazo (FIFO, LRU, Óptimo).|Simulador que calcula fallos de página y compara los tres algoritmos con un mismo patrón de acceso.|
|4|Entrada/Salida y sistemas de archivos: sondeo, interrupciones, DMA, métodos de asignación de archivos (contigua, enlazada, indexada).|Simulación de operaciones de E/S y un sistema de archivos simplificado con permisos básicos.|
|5|Seguridad: autenticación, control de acceso, cifrado simétrico/asimétrico básico; nociones de virtualización.|Módulo de control de acceso funcional y una demostración de cifrado/descifrado de un archivo.|
|6|Sistemas distribuidos: comunicación entre procesos/nodos (RPC o paso de mensajes simulado).|Demostración de intercambio de mensajes entre dos o más procesos simulando nodos distintos.|

## V. Calendario de entregas

El calendario respeta las semanas de evaluación fijadas en el sílabo (Examen Parcial en la semana 8 y Examen Final en la semana 16) y ubica las cuatro entregas calificadas del proyecto de modo que cada una cierre un bloque temático antes del examen correspondiente.

|Seman a|Unidad del sílabo|Entregable del proyecto|Tipo de evaluación|Peso|
|---|---|---|---|---|
|1|Introducción a los SO|Formación de equipos (3–4 integrantes) y elección del caso a simular. Entrega de ficha técnica del proyecto (alcance y lenguaje: C y/o Python).|Avance sin nota (control de inicio)|—|
|2|Estructura de un SO|Diseño de la arquitectura del simulador: módulos a construir y diagrama de componentes.|Avance sin nota (control de inicio)|—|
|3|Procesos e Hilos|Trabajo en el Módulo 1: creación/terminación de procesos (fork/exec) y simulación de hilos con threading.|Trabajo en clase|—|
|4|Planificación de Procesos|Práctica de Laboratorio 1: Módulo 1 completo — procesos, hilos y planificador (FCFS, SJF, Round Robin, Prioridad) con métricas de tiempo de espera y respuesta.|Práctica escrita/laboratorio N.º 1|12,5 %|
|5|Sincronización de Procesos|Trabajo en el Módulo 2: solución de un problema clásico (productor-consumidor, filósofos o lectores-escritores) con semáforos/mutex.|Trabajo en clase|—|
|6|Gestión de Memoria|Trabajo en el Módulo 3: simulación de asignación contigua, fragmentación y tablas de páginas.|Trabajo en clase|—|
|7|Algoritmos de|Trabajo Domiciliario 1: entrega consolidada|Trabajo domiciliario|12,5 %|

||Reemplazo de Páginas|de los Módulos 2 y 3 — sincronización + gestión de memoria y reemplazo de páginas (FIFO, LRU, Óptimo) con informe comparativo.|N.º 1||
|---|---|---|---|---|
|8|EXAMEN PARCIAL|— (semana de evaluación; puede incluir preguntas sobre el diseño del simulador)|Examen Parcial|según fórmula|
|9|Entrada/Salida (E/S)|Trabajo en el Módulo 4: simulación de manejo de E/S (sondeo, interrupciones, DMA, buffering).|Trabajo en clase|—|
|10|Sistemas de Archivos|Práctica de Laboratorio 2: Módulo 4 completo — E/S simulada + sistema de archivos simplificado (asignación contigua/enlazada/indexada, permisos).|Práctica escrita/laboratorio N.º 2|12,5 %|
|11|Seguridad y Protección|Trabajo en el Módulo 5: autenticación simulada, control de acceso y cifrado básico (uso de GPG u otra librería).|Trabajo en clase|—|
|12|Virtualización|Avance del Módulo 5 y comparación conceptual de virtualización (VM vs. contenedores) aplicada al simulador.|Avance sin nota (control)|—|
|13|SO Distribuidos|Avance del Módulo 6: simulación simplificada de comunicación entre "nodos" (RPC o paso de mensajes).|Avance sin nota (control)|—|
|14|Casos de Estudio|Preparación de la sustentación y del informe final integrador (todos los módulos).|Avance sin nota (control)|—|
|15|Desarrollo Práctico|Trabajo Domiciliario 2: entrega final del simulador integrado (Módulos 1 a 6) + sustentación oral grupal (10–15 min por equipo).|Trabajo domiciliario N.º 2 + sustentación|12,5 %|
|16|EXAMEN FINAL|— (semana de evaluación)|Examen Final|según fórmula|
|17|Examen Sustitutorio|— (aplica solo a quienes rindan sustitutorio)|Examen Sustitutorio|según fórmula|

**Nota:** las cuatro entregas calificadas (semanas 4, 7, 10 y 15) equivalen a las "2 prácticas escritas sobre los

laboratorios" y a los "2 trabajos domiciliarios sobre el análisis del sistema operativo" que exige el sílabo, y su promedio constituye el Promedio de Prácticas de la fórmula oficial:

### Nota Final = (Examen Parcial + Examen Final + Promedio de Prácticas) / 3

## VI. Rúbrica de evaluación

La siguiente rúbrica se aplica, con los mismos criterios y pesos, a cada una de las cuatro entregas calificadas; en las prácticas de laboratorio (semanas 4 y 10) el criterio "Sustentación oral" no aplica y su peso (15 %) se redistribuye proporcionalmente entre los demás criterios. La entrega de la semana 15 es la única que incluye sustentación oral obligatoria.

**Deficiente** **Criterio Peso Excelente (18–20) Bueno (14–17) Regular (11–13)** **(0–10)**

|Correctitud funcional|30 % El módulo|Implementa la|Implementa|No|
|---|---|---|---|---|
|y algorítmica|implementa correctamente todos los algoritmos exigidos (p. ej. FCFS/SJF/RR, FIFO/LRU/Óptimo,|mayoría de los algoritmos con resultados correctos; fallas menores en casos límite.|parcialmente los algoritmos o con errores que afectan algunos resultados.|implementa los algoritmos exigidos o los resultados son incorrectos.|

||||semáforos) y produce resultados verificables.||||
|---|---|---|---|---|---|---|
||Calidad y organización del código|15 %|Código modular, legible, comentado, con manejo de errores y control de versiones (commits claros en Git).|Código ordenado y funcional, con comentarios y control de versiones básico.|Código funcional pero desordenado o con comentarios/version ado insuficientes.|Código difícil de leer, sin comentarios ni control de versiones.|
||Documentación técnica|15 %|Informe completo: diseño, diagramas (procesos, memoria o E/S según el módulo), instrucciones de ejecución y conclusiones claras.|Informe completo con diagramas básicos y conclusiones.|Informe incompleto o con diagramas/explicacio nes insuficientes.|No presenta informe o es mínimo.|
||Análisis y comparación de resultados|15 %|Compara cuantitativamente los algoritmos (tiempos de espera, fallos de página, etc.) con gráficos y una discusión crítica.|Compara los algoritmos con datos, discusión breve.|Presenta datos sin comparación o análisis superficial.|No presenta análisis de resultados.|
||Sustentación oral (aplica en semana 15)|15 %|Explicación clara y ordenada del diseño e implementación; responde con dominio las preguntas del jurado.|Explicación clara; responde la mayoría de las preguntas con seguridad.|Explicación confusa o dominio parcial del tema.|No sustenta o no domina el proyecto desarrollado.|
||Trabajo en equipo y cumplimiento de plazos|10 %|Entrega puntual, participación equilibrada y evidenciada (commits/roles) de todos los integrantes.|Entrega puntual con participación mayoritariamente equilibrada.|Entrega con retraso leve o participación desigual.|Entrega fuera de plazo o participación de un solo integrante.|
|• • • •|fecha de entrega.|VII. Recomendaciones para los docentes antes del Examen Final de la semana 16. evaluación oficial del curso.||Publicar la ficha técnica y las plantillas de informe junto con el sílabo desde la semana 1. Usar las sesiones de laboratorio del sílabo (fork/exec en C, threading en Python, semáforos, simulación de reemplazo de páginas) como espacio guiado para avanzar cada módulo antes de la Reservar 10–15 minutos por equipo en la semana 15 ("Desarrollo Práctico") para la sustentación final, Registrar las notas de las cuatro entregas como las prácticas/trabajos domiciliarios del sistema de|||