# Arquitectura de la interfaz

## Capas

1. `app.py` presenta campañas, cuentas, progreso, hilos y exportaciones.
2. `ui.runtime` inicia procesos separados y mantiene registros locales.
3. `x_research.campaign` transforma campañas en trabajos temporales exactos.
4. `x_research.collector` consulta X y persiste cada resultado inmediatamente.
5. `x_research.storage` mantiene tuits, usuarios, capturas, relaciones, eventos y trabajos en
   SQLite.

La interfaz no guarda cookies. Solo muestra nombre, estado y último uso leyendo `accounts.db`.

## Estados de un trabajo

- `pending`: planificado;
- `running`: iniciado;
- `completed`: terminado y omitido al reanudar;
- `failed`: interrumpido o fallido, se vuelve a intentar en la próxima ejecución.

Cada captura se identifica por trabajo, tuit, tipo y raíz. Las restricciones únicas de SQLite
impiden duplicados aunque una consulta se repita.

## Fechas

Las campañas expresan un inicio inclusivo y un final exclusivo. La interfaz solicita al usuario un
último día inclusivo y suma un día al guardar la configuración. El motor transforma los límites a
épocas Unix con la zona `America/Argentina/Buenos_Aires` y vuelve a validar la fecha de cada tuit.

## Procesos

Al presionar **Iniciar o reanudar**, la interfaz crea un proceso de Python independiente, registra
su PID y envía la salida a `data/runtime/<campaña>.log`. Por eso una actualización o el cierre de
la pestaña no elimina el trabajo. La computadora sí debe permanecer encendida y conectada.

El botón de detención envía una interrupción al grupo del proceso. Los trabajos completos y todas
las capturas escritas antes de la interrupción permanecen en SQLite y JSONL.

## Datos directos e hilos

La campaña principal crea capturas `search`. La pestaña de hilos genera trabajos separados por
`conversation_id` y crea capturas `reply`. Ambas capas comparten la tabla de tuits, pero conservan
su procedencia en `captures` y `jobs`.
