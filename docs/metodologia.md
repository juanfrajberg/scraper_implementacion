# Metodología de recolección

## Unidad de trabajo

Cada campaña define consultas, un comienzo inclusivo, un final exclusivo, una zona horaria y un
límite por trabajo. El plan divide ese período en ventanas independientes. Las campañas incluidas
usan días completos en `America/Argentina/Buenos_Aires`.

## Inclusión y exclusión

Un resultado directo se incluye cuando X lo devuelve para la consulta y su fecha pertenece al
intervalo exacto `[since, until)`. El recolector vuelve a comprobar localmente esa fecha y descarta
resultados externos al intervalo. Las respuestas obtenidas al reconstruir conversaciones se
identifican como contexto (`reply`) y no como coincidencias directas (`search`).

## Límites y cobertura

Alcanzar el máximo configurado marca el trabajo como saturado. Si se activa el refinamiento, el
intervalo se divide hasta el mínimo configurado. Esto reduce la concentración temporal, pero no
garantiza exhaustividad: X puede ordenar, limitar o bloquear resultados.

## Persistencia y deduplicación

Cada captura se escribe inmediatamente en SQLite y JSONL. `tweet_id` identifica publicaciones
únicas; una tabla separada conserva todas las consultas y trabajos que capturaron cada una. Los
trabajos completados se omiten al reanudar y los fallidos o interrumpidos se vuelven a intentar.

## Reproducibilidad

Se conservan la consulta completa, los límites temporales, la capa del corpus, el equipo, la
versión de `twscrape`, los intentos, los avisos y el estado de cada trabajo. Las campañas versionadas
en `config/` permiten volver a generar el mismo plan.
