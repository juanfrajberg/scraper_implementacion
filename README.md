# Análisis de conversaciones sobre Argentina en X

Proyecto académico de **recolección, procesamiento y análisis de publicaciones públicas de X (Twitter)** relacionadas con Argentina durante la final de 2026.

El proyecto utiliza **Python y herramientas FOSS** para construir un dataset estructurado que posteriormente puede analizarse mediante expresiones regulares, análisis temporal, análisis de redes y visualización de grafos.

---

# Descripción del proyecto

Este proyecto implementa un pipeline de recolección y análisis de publicaciones públicas de X (Twitter), utilizando Python y Twikit, con fines académicos y de investigación.

El sistema permite realizar búsquedas dentro de una ventana temporal determinada, recolectar publicaciones relacionadas con consultas específicas y almacenar información estructurada sobre cada publicación, incluyendo autor, fecha, contenido, likes, retweets, respuestas, citas y datos de conversación.

El flujo general del proyecto es:

X (Twitter)
     │
     ▼
Recolección mediante Twikit
     │
     ▼
Datos RAW (JSONL)
     │
     ▼
Procesamiento y SQLite
     │
     ├──────────────┬──────────────┐
     ▼              ▼              ▼
Análisis textual   Análisis       Análisis
   (Regex)         temporal       de redes
                                    │
                                    ▼
                                  Grafo

Los datos recolectados se conservan inicialmente en formato RAW, permitiendo reproducir diferentes etapas de procesamiento sin necesidad de realizar nuevamente la recolección. Posteriormente, los datos se normalizan y almacenan en SQLite para facilitar consultas y análisis.

El proyecto también permite reconstruir relaciones entre publicaciones y usuarios —por ejemplo, respuestas, menciones y citas— para generar posteriormente representaciones de red mediante NetworkX y Gephi.

La recolección se realiza utilizando una única cuenta, respetando los límites y mecanismos de control establecidos por la plataforma. En caso de alcanzarse un límite de solicitudes, el proceso se pausa y reanuda cuando sea posible continuar.

El objetivo final es obtener un dataset reproducible que permita estudiar la evolución temporal, el contenido y la estructura de las conversaciones relacionadas con Argentina durante el período seleccionado.

---

# Objetivos

El objetivo principal es construir un pipeline reproducible para estudiar conversaciones relacionadas con Argentina durante un evento deportivo.

El proyecto busca recolectar y analizar:

* publicaciones;
* autores;
* fechas y horarios;
* cantidad de likes;
* cantidad de retweets;
* cantidad de respuestas;
* cantidad de citas;
* visualizaciones, cuando estén disponibles;
* identificadores de conversación;
* relaciones de respuesta;
* menciones;
* hashtags;
* contenido textual.

A partir de estos datos se pretende estudiar:

1. **Actividad temporal**
2. **Contenido textual**
3. **Usuarios más activos**
4. **Publicaciones con mayor interacción**
5. **Estructura de conversaciones**
6. **Relaciones entre usuarios**
7. **Comunidades**
8. **Centralidad de usuarios**
9. **Evolución del contenido durante el evento**

---

# Arquitectura

El proyecto está diseñado como un pipeline:

```text
                         X / Twitter
                              │
                              ▼
                         ┌─────────┐
                         │ Twikit  │
                         └────┬────┘
                              │
                              ▼
                     ┌────────────────┐
                     │  Datos RAW     │
                     │    JSONL       │
                     └───────┬────────┘
                             │
                             ▼
                       ┌────────────┐
                       │  SQLite    │
                       └─────┬──────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
            Regex         pandas        NetworkX
              │              │              │
              ▼              ▼              ▼
          contenido      estadísticas     grafo
                                             │
                                             ▼
                                           Gephi
```

La separación entre datos RAW y datos procesados permite modificar el procesamiento sin necesidad de volver a realizar la recolección.

---

# Tecnologías

El proyecto utiliza herramientas de código abierto o de distribución libre.

| Herramienta   | Función                 |
| ------------- | ----------------------- |
| Python        | Lenguaje principal      |
| Twikit        | Recolección             |
| python-dotenv | Variables de entorno    |
| SQLite        | Base de datos           |
| pandas        | Análisis de datos       |
| JupyterLab    | Análisis interactivo    |
| NetworkX      | Análisis de redes       |
| Matplotlib    | Gráficos                |
| Gephi         | Visualización de grafos |
| Git           | Control de versiones    |

---

# Estructura del proyecto

```text
twitter_argentina/
│
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
│
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── client.py
│   ├── models.py
│   ├── collector.py
│   ├── database.py
│   ├── process.py
│   ├── graph.py
│   └── main.py
│
├── notebooks/
│   ├── 01_exploracion.ipynb
│   ├── 02_regex.ipynb
│   ├── 03_analisis_temporal.ipynb
│   └── 04_grafo.ipynb
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── exports/
│
├── results/
│   ├── figures/
│   └── graphs/
│
└── docs/
    ├── metodologia.md
    └── esquema_datos.md
```

## Descripción

### `src/`

Contiene el código fuente.

### `notebooks/`

Contiene los análisis exploratorios y experimentos.

### `data/raw/`

Contiene los datos originales obtenidos durante la recolección.

### `data/processed/`

Contiene datos limpiados y normalizados.

### `data/exports/`

Contiene archivos destinados a otras herramientas.

### `results/`

Contiene gráficos, resultados y archivos de grafos.

### `docs/`

Contiene la metodología y documentación del dataset.

---

# Requisitos

Se recomienda:

* Linux;
* Python 3.11 o superior;
* Git;
* una cuenta de X válida para utilizar Twikit;
* Gephi, si se desea realizar análisis visual de redes.

El proyecto fue diseñado para ejecutarse localmente.

---

# Instalación

## 1. Clonar el repositorio

```bash
git clone https://github.com/USUARIO/scraper_implementacion.git
cd scraper_implementacion
```

Reemplazar la dirección anterior por la URL real del repositorio.

---

## 2. Crear entorno virtual

```bash
python -m venv .venv
```

Activarlo:

```bash
source .venv/bin/activate
```

En Windows:

```powershell
.venv\Scripts\activate
```

---

## 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

# Configuración

El proyecto utiliza variables de entorno para las credenciales.

Crear un archivo:

```text
.env
```

a partir de:

```text
.env.example
```

Por ejemplo:

```env
TWITTER_USERNAME=mi_usuario
TWITTER_EMAIL=correo@example.com
TWITTER_PASSWORD=mi_password
```

El archivo `.env` está incluido en `.gitignore` y **no debe subirse al repositorio**.

---

# Autenticación

La primera ejecución utiliza las credenciales configuradas en `.env`.

Después de autenticarse, el proyecto guarda las cookies localmente:

```text
cookies.json
```

Este archivo también está excluido mediante `.gitignore`.

Las cookies no deben compartirse ni subirlas a Git.

---

# Configuración del experimento

La configuración principal está en:

```text
src/config.py
```

Ejemplo:

```python
DATE_FROM = "2026-07-19"
DATE_TO = "2026-07-20"

SEARCHES = [
    "Argentina",
    '"España Argentina"',
    '"Argentina España"',
    '"Argentina campeón"',
]

MAX_TWEETS_PER_SEARCH = 100
```

Esto define:

* fecha inicial;
* fecha final;
* consultas;
* cantidad máxima de resultados por consulta.

---

# Ejecutar el MVP

Una vez configurado el proyecto:

```bash
source .venv/bin/activate
```

Ejecutar:

```bash
python -m src.main
```

El programa:

1. crea la base SQLite;
2. inicia el cliente de Twikit;
3. realiza las búsquedas;
4. pagina los resultados;
5. elimina duplicados;
6. normaliza los tweets;
7. guarda los resultados en JSONL;
8. inserta los datos en SQLite.

---

# Ejemplo de ejecución

Una ejecución podría producir:

```text
Cargando cookies...

Buscando: Argentina since:2026-07-19 until:2026-07-20

[1] @usuario1: Argentinaaaaa 🇦🇷🇦🇷🇦🇷
[2] @usuario2: QUÉ PARTIDO
[3] @usuario3: No puedo creerlo
[4] @usuario4: Argentina campeón!!!

Buscando: "España Argentina" since:2026-07-19 until:2026-07-20

[1] @usuario5: ...
[2] @usuario6: ...

Tweets únicos: 327

Datos procesados correctamente.

Proyecto finalizado.
```

---

# Datos recolectados

Cada tweet se normaliza mediante `TweetData`.

El modelo contiene:

```text
tweet_id
author_id
author_username
author_name
created_at
text
like_count
retweet_count
reply_count
quote_count
view_count
conversation_id
parent_tweet_id
url
search_query
```

---

# Significado de los campos

| Campo             | Descripción                           |
| ----------------- | ------------------------------------- |
| `tweet_id`        | Identificador del tweet               |
| `author_id`       | Identificador del autor               |
| `author_username` | Nombre de usuario                     |
| `author_name`     | Nombre visible                        |
| `created_at`      | Fecha y hora                          |
| `text`            | Contenido textual                     |
| `like_count`      | Cantidad de likes                     |
| `retweet_count`   | Cantidad de retweets                  |
| `reply_count`     | Cantidad de respuestas                |
| `quote_count`     | Cantidad de citas                     |
| `view_count`      | Visualizaciones, si están disponibles |
| `conversation_id` | Identificador de conversación         |
| `parent_tweet_id` | Tweet al que responde                 |
| `url`             | URL del tweet                         |
| `search_query`    | Consulta que produjo el resultado     |

---

# Formato JSONL

Los datos RAW se guardan en:

```text
data/raw/tweets.jsonl
```

JSONL significa que cada línea contiene un objeto JSON independiente.

Ejemplo:

```json
{"tweet_id":"1001","author_id":"50","author_username":"usuario1","author_name":"Juan","created_at":"...","text":"Argentina!!!","like_count":1500,"retweet_count":200,"reply_count":50}
{"tweet_id":"1002","author_id":"51","author_username":"usuario2","author_name":"Ana","created_at":"...","text":"Qué partido","like_count":300,"retweet_count":20,"reply_count":5}
```

Esto permite procesar grandes cantidades de datos sin tener que cargar todo el dataset en memoria.

---

# Leer el JSONL con Python

```python
import json

with open(
    "data/raw/tweets.jsonl",
    encoding="utf-8"
) as file:

    for line in file:

        tweet = json.loads(line)

        print(tweet["author_username"])
        print(tweet["text"])
```

---

# Base de datos SQLite

Los datos procesados se almacenan en:

```text
data/twitter.db
```

La base contiene tres tablas principales.

## `users`

```text
user_id
username
display_name
```

## `tweets`

```text
tweet_id
author_id
created_at
text
like_count
retweet_count
reply_count
quote_count
view_count
conversation_id
parent_tweet_id
url
search_query
```

## `relationships`

```text
source_id
target_id
relationship_type
tweet_id
```

---

# Consultar SQLite

SQLite puede consultarse desde Python:

```python
import sqlite3

db = sqlite3.connect(
    "data/twitter.db"
)

cursor = db.execute(
    """
    SELECT *
    FROM tweets
    LIMIT 10
    """
)

for row in cursor:
    print(row)
```

---

# Ejemplo: tweets con más likes

```python
import sqlite3

db = sqlite3.connect(
    "data/twitter.db"
)

rows = db.execute(
    """
    SELECT
        author_id,
        text,
        like_count
    FROM tweets
    ORDER BY like_count DESC
    LIMIT 20
    """
)

for row in rows:
    print(row)
```

---

# Ejemplo: usuarios más activos

```sql
SELECT
    author_id,
    COUNT(*) AS tweet_count
FROM tweets
GROUP BY author_id
ORDER BY tweet_count DESC
LIMIT 20;
```

---

# JupyterLab

Para iniciar JupyterLab:

```bash
jupyter lab
```

Se pueden ejecutar los notebooks:

```text
notebooks/
├── 01_exploracion.ipynb
├── 02_regex.ipynb
├── 03_analisis_temporal.ipynb
└── 04_grafo.ipynb
```

---

# 01 - Exploración

El primer notebook permite conocer el dataset.

Ejemplo:

```python
import sqlite3
import pandas as pd

db = sqlite3.connect(
    "../data/twitter.db"
)

tweets = pd.read_sql_query(
    "SELECT * FROM tweets",
    db
)

tweets.head()
```

Cantidad de tweets:

```python
len(tweets)
```

Cantidad de usuarios:

```python
tweets["author_id"].nunique()
```

Tweets con mayor interacción:

```python
tweets.sort_values(
    "like_count",
    ascending=False
).head(20)
```

---

# 02 - Análisis mediante Regex

El contenido textual puede analizarse mediante expresiones regulares.

Por ejemplo, encontrar menciones de Argentina:

```python
import re

pattern = re.compile(
    r"\b(argentina|argentino|argentina|argentinos)\b",
    re.IGNORECASE
)

tweets["mentions_argentina"] = (
    tweets["text"]
    .fillna("")
    .apply(
        lambda text: bool(
            pattern.search(text)
        )
    )
)
```

Extraer hashtags:

```python
tweets["hashtags"] = (
    tweets["text"]
    .fillna("")
    .apply(
        lambda text: re.findall(
            r"#\w+",
            text
        )
    )
)
```

Extraer menciones:

```python
tweets["mentions"] = (
    tweets["text"]
    .fillna("")
    .apply(
        lambda text: re.findall(
            r"@\w+",
            text
        )
    )
)
```

Extraer URLs:

```python
tweets["urls"] = (
    tweets["text"]
    .fillna("")
    .apply(
        lambda text: re.findall(
            r"https?://\S+",
            text
        )
    )
)
```

---

# 03 - Análisis temporal

Convertir fechas:

```python
tweets["created_at"] = pd.to_datetime(
    tweets["created_at"],
    errors="coerce"
)
```

Cantidad de tweets por hora:

```python
tweets.set_index(
    "created_at"
).resample(
    "1H"
).size()
```

Cantidad cada 15 minutos:

```python
tweets.set_index(
    "created_at"
).resample(
    "15min"
).size()
```

Esto permite estudiar picos de actividad.

---

# Visualización temporal

Ejemplo:

```python
import matplotlib.pyplot as plt

activity = (
    tweets
    .set_index("created_at")
    .resample("15min")
    .size()
)

activity.plot()

plt.title(
    "Actividad relacionada con Argentina"
)

plt.xlabel("Fecha")
plt.ylabel("Cantidad de tweets")

plt.tight_layout()

plt.show()
```

Los gráficos pueden guardarse en:

```text
results/figures/
```

---

# 04 - Análisis de grafos

El proyecto utiliza NetworkX para representar relaciones.

Un ejemplo de relación:

```text
Usuario A
    │
    │ reply
    ▼
Usuario B
```

Puede representarse como:

```text
source = A
target = B
type = reply
```

---

# Crear el grafo

El módulo:

```text
src/graph.py
```

construye un grafo dirigido.

Ejecutar:

```python
from src.graph import export_graph

export_graph()
```

Esto genera:

```text
results/graphs/reply_graph.gexf
```

---

# Abrir el grafo con Gephi

Instalar Gephi y abrir:

```text
results/graphs/reply_graph.gexf
```

Gephi permite estudiar:

* grado;
* centralidad;
* comunidades;
* modularidad;
* componentes;
* distribución de conexiones.

---

# Centralidad con NetworkX

Ejemplo:

```python
import networkx as nx

graph = nx.read_gexf(
    "results/graphs/reply_graph.gexf"
)

centrality = nx.degree_centrality(
    graph
)

ranking = sorted(
    centrality.items(),
    key=lambda x: x[1],
    reverse=True
)

for user, score in ranking[:20]:
    print(user, score)
```

---

# Modelo conceptual del grafo

El proyecto puede producir una estructura como:

```text
                 Usuario A
                /         \
               /           \
            reply         reply
             /               \
            ▼                 ▼
       Usuario B          Usuario C
            │
           reply
            │
            ▼
       Usuario D
```

Posteriormente se pueden agregar otras relaciones:

```text
reply
mention
quote
retweet
```

---

# Reconstrucción de conversaciones

Los tweets contienen:

```text
conversation_id
parent_tweet_id
```

Estos campos permiten reconstruir conversaciones.

Ejemplo:

```text
Tweet A
conversation_id = 100
parent = NULL

Tweet B
conversation_id = 100
parent = A

Tweet C
conversation_id = 100
parent = B

Tweet D
conversation_id = 100
parent = A
```

La conversación se representa como:

```text
A
├── B
│   └── C
└── D
```

---

# Reproducibilidad

El experimento debe documentar:

```text
Fecha de recolección
Hora de inicio
Hora de finalización
Consultas
Ventana temporal
Cantidad máxima de resultados
Criterios de inclusión
Criterios de exclusión
Método de deduplicación
Versión de Python
Versión de Twikit
```

La configuración del experimento está centralizada en:

```text
src/config.py
```

---

# Ejemplo de experimento

Un experimento podría utilizar:

```text
Ventana:

2026-07-19 00:00
hasta
2026-07-20 00:00
```

Consultas:

```text
Argentina
"España Argentina"
"Argentina España"
"Argentina campeón"
```

Máximo inicial:

```text
100 tweets por consulta
```

Esto permite obtener un dataset inicial de tamaño reducido para validar el pipeline.

Una vez validado el MVP, se puede aumentar progresivamente el tamaño del dataset.

---

# Privacidad

El dataset puede contener identificadores y nombres de usuario.

Por ese motivo:

* no se deben almacenar credenciales en Git;
* no se deben publicar cookies;
* no se deben publicar datos innecesarios;
* se debe considerar la legislación aplicable;
* se debe revisar qué datos son realmente necesarios para el análisis;
* se debe evaluar la anonimización antes de distribuir datasets.

El repositorio contiene principalmente **código y metodología**.

---

# Qué NO subir al repositorio

No deben subirse:

```text
.env
cookies.json
```

Tampoco se recomienda subir directamente:

```text
data/raw/
data/twitter.db
```

si contienen datos recolectados que no se desea redistribuir.

El `.gitignore` está configurado para evitarlo.

---

# Posibles extensiones

Una vez completado el MVP se pueden implementar:

## Recolección

* mayor cantidad de consultas;
* más ventanas temporales;
* recolección por intervalos;
* control de duplicados;
* registro de errores;
* logs;
* metadatos del experimento.

## Conversaciones

* reconstrucción automática de hilos;
* identificación de tweets raíz;
* profundidad de conversación;
* cantidad de respuestas;
* árboles de conversación.

## Texto

* hashtags;
* menciones;
* URLs;
* emojis;
* palabras frecuentes;
* expresiones regulares;
* clasificación temática;
* análisis de sentimiento;
* detección de entidades.

## Redes

* replies;
* mentions;
* quotes;
* retweets;
* comunidades;
* centralidad;
* influencia;
* evolución temporal de la red.

## Visualización

* actividad por minuto;
* actividad por hora;
* distribución de likes;
* distribución de retweets;
* evolución de hashtags;
* grafos temporales;
* comunidades.

---

# Estado del proyecto

## MVP

* [x] Estructura del proyecto
* [x] Entorno virtual
* [x] Configuración mediante `.env`
* [x] Cliente Twikit
* [x] Búsqueda
* [x] Paginación
* [x] Deduplicación
* [x] Normalización
* [x] JSONL
* [x] SQLite
* [ ] Reconstrucción completa de hilos
* [ ] Extracción de relaciones
* [ ] Análisis completo mediante Regex
* [ ] Análisis temporal
* [ ] Grafo completo
* [ ] Visualización Gephi

---

# Licencia

TBD

---

# Autor

TBD

```text
Python
Twikit
SQLite
pandas
NetworkX
JupyterLab
Gephi
Git
```
