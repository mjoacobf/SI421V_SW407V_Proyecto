# Plan de Implementación Técnica - SO-Sim (NexusOS)

**Contexto del Proyecto:** Este documento detalla la hoja de ruta final para el desarrollo del simulador de sistema operativo "NexusOS-Sim" en Python. El desarrollo será estrictamente modular, aplicando los conceptos teóricos de las primeras 6 semanas del curso SW407. Se utilizará Programación Orientada a Objetos (POO) para aislar responsabilidades en distintos archivos, facilitando la integración y evaluación paso a paso.

## Arquitectura Modular del Sistema
El proyecto se dividirá en los siguientes módulos (archivos Python), los cuales se irán construyendo y conectando progresivamente:
* `main.py`: Punto de entrada del simulador.
* `shell.py`: Interfaz de línea de comandos (CLI) para interactuar con el SO.
* `procesos.py`: Gestión del Bloque de Control de Proceso (PCB) y su ciclo de vida.
* `planificador.py`: Algoritmos de asignación de CPU.
* `sincronizacion.py`: Manejo de concurrencia, semáforos y prevención de interbloqueos.
* `memoria.py`: Traducción de direcciones y asignación de espacio (paginación).

---

## FASE 1: Fundamentos y Arquitectura Base

### Semana 1: Introducción a los Sistemas Operativos
* **Objetivo Teórico:** Comprender el rol del SO como "gerente" de recursos y definir la tipología del sistema.
* **Tareas de Implementación:**
  1. Inicializar el repositorio Git del proyecto.
  2. Crear el entorno virtual en Python y el archivo `requirements.txt`.
  3. Crear la estructura de directorios base (`src/`, `docs/`, `tests/`) y los archivos vacíos de los módulos descritos en la arquitectura para asegurar la separación de responsabilidades desde el día cero.

### Semana 2: Estructura de un Sistema Operativo
* **Objetivo Teórico:** Diferenciar modo kernel de modo usuario, y diseñar la interacción mediante CLI (Línea de Comandos).
* **Módulo principal a desarrollar:** `shell.py` y `main.py`.
* **Tareas de Implementación:**
  1. Diseñar el **Shell (CLI)** del simulador en `shell.py`: un bucle interactivo (`while True`) en consola que actúe como interfaz de usuario.
  2. Implementar comandos básicos simulados (ej. `help`, `clear`, `exit`, y comandos de manipulación de archivos simulados como `ls`, `mkdir`).
  3. Conectar `shell.py` con `main.py` para que el simulador arranque directamente en la consola interactiva.

---

## FASE 2: Gestión del Procesador

### Semana 3: Procesos e Hilos
* **Objetivo Teórico:** Modelar el PCB, el ciclo de vida (5 estados) y diferenciar procesos (`fork`) de hilos (`threads`).
* **Módulo principal a desarrollar:** `procesos.py`.
* **Tareas de Implementación:**
  1. Crear la clase `Proceso` (PCB) con atributos aislados: `PID`, `estado` (Nuevo, Listo, Ejecución, Bloqueado, Terminado), `pc`, y `registros`.
  2. Implementar el gestor de estados: colas (listas en Python) para procesos "Listos" y "Bloqueados", y métodos para mover procesos entre ellas.
  3. Simular `fork()` creando un método que devuelva una copia del objeto `Proceso` con un nuevo PID, y `exec()` que reinicie sus parámetros.
  4. Crear un script de prueba usando el módulo `threading` de Python para instanciar múltiples "hilos" que impriman su ejecución simultánea, demostrando la diferencia con los procesos.

### Semana 4: Planificación de Procesos
* **Objetivo Teórico:** Maximizar el rendimiento y minimizar tiempos de espera simulando la decisión de asignación de CPU.
* **Módulo principal a desarrollar:** `planificador.py` (interactuando con `procesos.py`).
* **Tareas de Implementación:**
  1. Crear la clase `Planificador` que reciba una lista de objetos `Proceso`.
  2. Implementar los 4 algoritmos clásicos como métodos independientes:
     * `fcfs()`: Primero en llegar, primero en ser atendido (FIFO).
     * `sjf()`: El trabajo más corto primero.
     * `round_robin(quantum)`: Asignación por turnos circulares.
     * `prioridad()`: Atención basada en un atributo de prioridad del proceso.
  3. Implementar un generador de reportes que calcule e imprima el **Tiempo de Espera Promedio** y **Tiempo de Respuesta Promedio** para comparar los algoritmos matemáticamente.

---

## FASE 3: Concurrencia y Memoria

### Semana 5: Sincronización de Procesos
* **Objetivo Teórico:** Evitar condiciones de carrera e interbloqueos usando exclusión mutua y semáforos.
* **Módulo principal a desarrollar:** `sincronizacion.py`.
* **Tareas de Implementación:**
  1. **Productor-Consumidor:** Crear una simulación independiente usando `threading.Semaphore`. Implementar un almacén (búfer) acotado protegido por un `mutex`, un semáforo de `vacios` y uno de `llenos`.
  2. **Filósofos Comensales (Deadlock):** Simular 5 hilos (cocineros) compitiendo por 5 recursos (candados/Locks). 
  3. Implementar la estrategia de **asignación asimétrica** en los filósofos (uno toma los recursos en orden inverso) para garantizar y demostrar que no ocurre un interbloqueo.
  4. Agregar comandos al `shell.py` para ejecutar estas simulaciones (ej: `simular_productor`, `simular_filosofos`) y ver los logs en tiempo real.

### Semana 6: Gestión de Memoria
* **Objetivo Teórico:** Traducir direcciones virtuales a físicas y aplicar particionamiento contiguo y paginación.
* **Módulo principal a desarrollar:** `memoria.py`.
* **Tareas de Implementación:**
  1. **Asignación Contigua:** Crear una clase `GestorMemoriaContigua` que simule una lista de bloques, evidenciando la fragmentación externa al intentar asignar procesos de distintos tamaños.
  2. **Paginación:** Crear la clase `GestorPaginacion`. Configurar un tamaño de página fijo, dividir la "RAM" en marcos (frames) y la memoria lógica del proceso en páginas.
  3. Implementar la estructura **Tabla de Páginas** por cada proceso.
  4. Crear la función de traducción `traducir_direccion(proceso, dir_virtual)` que calcule y retorne la dirección física exacta, lanzando un error simulado si hay un fallo (segmentation fault).
  5. Integrar un comando en el shell para visualizar el mapa de memoria actual.