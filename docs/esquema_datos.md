# Esquema de datos

La base `research.sqlite3` contiene:

- `tweets`: ID, fecha, texto, idioma, URL, métricas, conversación y referencias a respuestas,
  citas y retuits;
- `users`: usuario y metadatos públicos observados;
- `user_snapshots`: estado diario de esos metadatos;
- `jobs`: consulta, intervalo, límite, estado, intentos, resultados y avisos;
- `captures`: procedencia de cada tuit (`search` o `reply`) y raíz descargada;
- `relationships`: vínculos de respuesta, cita y retuit;
- `job_events`: errores, avisos y decisiones de filtrado.

Los identificadores se guardan como texto para evitar pérdida de precisión. `tweets.tweet_id` es
único, mientras que `captures` permite que un mismo tuit pertenezca a varias consultas sin
duplicarlo.

## Exportaciones

`tweets.csv` contiene una fila por tuit único. `threads.csv` ordena por conversación, profundidad,
fecha e ID, e informa si están presentes el padre y la raíz. Ambos archivos incluyen encabezados
aunque la consulta no haya obtenido resultados.
