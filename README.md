# Contexto del Proyecto: Simulador "NexusOS" para NexusBank

## 1. El Escenario: La Crisis de NexusBank
**NexusBank** es una institución financiera de rápido crecimiento en América Latina. Durante los últimos cinco años, ha pasado de ser un banco tradicional a una plataforma digital que procesa millones de transacciones diarias (transferencias, pagos de servicios, consultas de saldo y operaciones en bolsa). 

Sin embargo, el éxito ha traído consigo una crisis operativa. El núcleo de su sistema heredado (*legacy system*) está colapsando. Durante los picos de demanda (como quincenas y cierres de mes), la aplicación móvil se congela, los cajeros automáticos muestran tiempos de espera inaceptables y, lo que es peor, la semana pasada se detectaron inconsistencias temporales en los saldos de los usuarios debido a transferencias simultáneas no gestionadas correctamente.

## 2. El Problema Técnico a Nivel de Sistema Operativo
Una auditoría técnica externa identificó que los problemas de NexusBank no son de interfaz o red, sino de la gestión de recursos a nivel del sistema operativo que sostiene sus servidores centrales:

1. **Cuellos de botella en el procesamiento:** El sistema actual procesa las peticiones (procesos) en el orden de llegada (FCFS), lo que provoca que transacciones pesadas bloqueen consultas de saldo simples (efecto convoy).
2. **Condiciones de Carrera (Race Conditions):** Las inconsistencias de saldo ocurrieron porque múltiples hilos intentaron modificar la misma cuenta bancaria al mismo tiempo sin los mecanismos de exclusión mutua adecuados.
3. **Colapso de Memoria RAM:** Los servidores se quedan sin memoria física y la paginación a disco es extremadamente ineficiente. El algoritmo actual reemplaza en caché datos vitales de usuarios activos por datos antiguos.
4. **I/O Lento y Desorganizado:** Los registros (logs) de auditoría se escriben en disco de forma secuencial y desorganizada, ralentizando las confirmaciones de las transferencias.
5. **Vulnerabilidades de Seguridad:** La comunicación entre las sucursales y la central no está cifrada a nivel de sistema, y carece de un modelo robusto de control de acceso a los archivos de transacciones.

## 3. La Solución: El Proyecto "NexusOS-Sim"
Para solucionar esta crisis, la junta directiva ha contratado a nuestro equipo de ingeniería (curso SW407) para rediseñar el núcleo del sistema. Sin embargo, implementar cambios directamente en los servidores de producción o en un entorno real sin pruebas previas sería catastrófico.

Por lo tanto, la decisión técnica ha sido construir **"NexusOS-Sim"**: un simulador de sistema operativo desarrollado íntegramente en Python. Este simulador no procesará dinero real, sino que nos permitirá **modelar, evaluar y comparar** diferentes algoritmos de gestión de recursos bajo estrés bancario.

### Argumentación Técnica (Por qué simular):
* **Benchmarking de Planificación:** Nos permitirá probar si un algoritmo *Round Robin* o por *Prioridades* (dando prioridad alta a transferencias internacionales) reduce el tiempo de respuesta frente al actual FCFS.
* **Prueba de Sincronización:** Simularemos el problema clásico de "Lectores-Escritores" (múltiples usuarios leyendo su saldo, uno modificándolo) usando semáforos, garantizando matemáticamente que no haya saldos erróneos.
* **Optimización de Memoria:** Simularemos el acceso a memoria de las transacciones para probar si un algoritmo de reemplazo *LRU (Least Recently Used)* mantiene en RAM a los clientes más activos, reduciendo los fallos de página.
* **Escalabilidad Segura:** Nos permitirá probar permisos de archivos y simular la comunicación distribuida entre las diferentes agencias del banco antes de invertir en infraestructura real.

**Conclusión:** Al final del proyecto, NexusBank tendrá un reporte fundamentado en datos cuantitativos generados por nuestro simulador en Python, determinando exactamente qué algoritmos debe adoptar el nuevo SO de sus servidores centrales para garantizar rapidez, coherencia y seguridad a sus millones de clientes.

---

## 4. Requisitos y Entorno
* **Python**: 3.10 o superior
* **Control de versiones**: Git & GitHub

