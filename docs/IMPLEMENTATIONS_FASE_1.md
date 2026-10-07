# IMPLEMENTATIONS_FASE_1 — Fundamentos y Arquitectura Base

Cubre las Semanas 1 y 2 del [PLAN_IMPLEMENTACIÓN_1](PLAN_IMPLEMENTACIÓN_1.md).

## Semana 1 — Estructura del proyecto

| Cambio | Archivo | Detalle |
|---|---|---|
| Repositorio Git | — | Ya estaba inicializado (`main`). |
| Dependencias | `requirements.txt` | Solo biblioteca estándar (Python ≥ 3.10); no se creó `venv` porque no hay paquetes externos que aislar. Las pruebas usan `unittest`. |
| Directorios | `src/`, `docs/`, `tests/` | Creados según el plan. |
| Módulos base | `src/procesos.py`, `planificador.py`, `sincronizacion.py`, `memoria.py` | Creados vacíos (solo docstring) para fijar la separación de responsabilidades; se completan en las Fases 2 y 3. |
| Paquete | `src/__init__.py` | Vacío. |

## Semana 2 — Shell (CLI) y punto de entrada

### `src/shell.py`
* **`Shell`**: bucle interactivo `while self.activo` con prompt `nexus@sim:<ruta>$`. Lee de `entrada` y escribe en `salida` (inyectables, lo que permite probarlo sin consola real).
* **Tabla de comandos extensible**: `registrar(nombre, función, ayuda)`. Cada fase posterior añade sus comandos sin tocar el bucle.
* **Aislamiento modo usuario / kernel**: toda excepción lanzada por un comando se captura en `ejecutar_linea` y se muestra como `error: ...`; el shell no se cae.
* Tokenización con `shlex.split`; comandos desconocidos y EOF (Ctrl+D / fin de pipe) manejados.
* **`SistemaArchivosSimulado`**: árbol de directorios en memoria (`/bin /home /var /tmp`) con `ls`, `mkdir`, `cd` (`..` y `/`) y `pwd`.
* Comandos: `help`, `clear`, `exit`, `ls`, `mkdir`, `cd`, `pwd`.

### `src/main.py`
Punto de entrada: `python src/main.py`. Reconfigura stdin/stdout a UTF-8 (en Windows los pipes usan otra codificación y rompían los acentos) y lanza `Shell().ejecutar()`.

### Pruebas — `tests/test_shell.py` (4)
`help`/`exit`, `mkdir`+`ls`+`cd`+`pwd`, `mkdir` duplicado sin romper el shell, comando desconocido.

## Cómo ejecutar
```
python src/main.py
python -m unittest discover -s tests
```

## Decisiones
* El sistema de archivos de esta fase es solo de directorios; el sistema de archivos con permisos corresponde al Módulo 4 de la propuesta.
* `from __future__ import annotations` y tipos modernos (`X | None`) → requiere Python ≥ 3.10.
