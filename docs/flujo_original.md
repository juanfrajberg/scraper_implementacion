# Flujo original basado en JSONL

> Documento histórico. El flujo recomendado y mantenido actualmente es la interfaz descrita en
> el [README](../README.md). Estos scripts se conservan para reproducir las primeras descargas en
> formato JSONL, pero no comparten la base SQLite ni el seguimiento de campañas de la interfaz.

# Análisis de conversaciones sobre Argentina en X

Proyecto académico de **recolección y análisis de publicaciones públicas de X (Twitter)** relacionadas con Argentina durante un período determinado.

El proyecto utiliza **Python** y **twscrape** para realizar búsquedas, almacenar tweets en formato JSONL y reconstruir las conversaciones asociadas a los tweets encontrados.

---

# Objetivo

El objetivo principal es construir un pipeline reproducible para recolectar publicaciones públicas de X y estudiar:

* publicaciones relacionadas con Argentina;
* autores y fechas de publicación;
* interacciones entre publicaciones;
* conversaciones y respuestas;
* estructura temporal de las conversaciones.

La recolección se realiza dentro de ventanas temporales definidas mediante consultas de X.

---

# Tecnologías

| Tecnología | Uso                                        |
| ---------- | ------------------------------------------ |
| Python     | Implementación                             |
| twscrape   | Acceso y recolección de publicaciones de X |
| JSONL      | Almacenamiento de datos                    |
| Git        | Control de versiones                       |

---

# Estructura del proyecto

```text
scraper_implementacion/
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
│   ├── collector.py
│   ├── threads.py
│   └── main.py
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

Los directorios de datos y resultados se mantienen separados del código fuente para facilitar las pruebas y el análisis posterior.

---

# Componentes principales

## `src/config.py`

Contiene la configuración general del experimento:

* período de búsqueda;
* consultas;
* cantidad máxima de tweets por búsqueda;
* rutas de almacenamiento.

Ejemplo:

```python
DATE_FROM = "2026-07-19"
DATE_TO = "2026-07-20"

SEARCHES = [
    '"Argentina"',
    '"España Argentina"',
    '"Argentina España"',
    '"Argentina campeón"',
]

MAX_TWEETS_PER_SEARCH = 100
```

---

## `src/client.py`

Se encarga de crear el cliente de `twscrape`.

El cliente utiliza la base de cuentas configurada para `twscrape`.

---

## `src/collector.py`

Es el componente principal de recolección.

Sus responsabilidades son:

1. ejecutar una búsqueda;
2. obtener los tweets;
3. convertir los objetos de `twscrape` a diccionarios;
4. guardar los tweets en JSONL;
5. identificar conversaciones;
6. reconstruir los hilos;
7. guardar los hilos obtenidos.

Los tweets individuales se almacenan en:

```text
data/tweets.jsonl
```

Los hilos reconstruidos se almacenan en:

```text
data/threads.jsonl
```

Los archivos de datos locales no forman parte del repositorio.

---

## `src/threads.py`

Contiene la lógica utilizada para reconstruir conversaciones.

Utiliza:

```python
api.tweet_thread(...)
```

para recuperar los tweets pertenecientes a una conversación.

Los tweets recuperados se ordenan cronológicamente antes de almacenarse.

El límite utilizado al reconstruir un hilo es configurable:

```python
limit = 500
```

Este límite es importante porque una conversación puede contener una cantidad considerable de tweets.

---

## `src/main.py`

Es el punto de entrada de la aplicación.

Ejecuta el cliente y comienza la recolección utilizando la consulta configurada.

Para ejecutar el programa:

```bash
python -m src.main
```

---

# Flujo de recolección

El funcionamiento general es:

```text
              X
              │
              ▼
          twscrape
              │
              ▼
        client.py
              │
              ▼
       collector.py
          │       │
          │       │
          ▼       ▼
      tweets   conversaciones
       JSONL        │
                    ▼
               threads.py
                    │
                    ▼
              threads.jsonl
```

El proceso permite conservar tanto los tweets encontrados directamente mediante una búsqueda como las conversaciones reconstruidas a partir de ellos.

---

# Búsqueda de tweets

Las búsquedas pueden utilizar los operadores disponibles en X.

Por ejemplo:

```text
Argentina since:2026-07-19 until:2026-07-20
```

La consulta permite limitar la recolección a una ventana temporal.

El programa muestra durante la ejecución información como:

```text
Iniciando cliente...
Buscando: "Argentina since:2026-07-19 until:2026-07-20"
Tweets encontrados: 24
```

---

# Datos recolectados

Cada tweet se convierte a un registro JSON.

Ejemplo:

```json
{
    "tweet_id": "123456789",
    "username": "usuario",
    "displayname": "Nombre",
    "date": "2026-07-20T22:59:28+00:00",
    "text": "Texto del tweet",
    "likes": 100,
    "retweets": 20,
    "replies": 15,
    "quotes": 3,
    "views": 5000,
    "conversation_id": "123456789",
    "in_reply_to": null,
    "in_reply_to_user": null,
    "mentioned_users": [],
    "hashtags": [],
    "lang": "es",
    "url": "https://x.com/..."
}
```

---

# Campos principales

| Campo              | Descripción                      |
| ------------------ | -------------------------------- |
| `tweet_id`         | Identificador del tweet          |
| `username`         | Usuario que publicó el tweet     |
| `displayname`      | Nombre mostrado                  |
| `date`             | Fecha y hora de publicación      |
| `text`             | Contenido del tweet              |
| `likes`            | Cantidad de likes                |
| `retweets`         | Cantidad de retweets             |
| `replies`          | Cantidad de respuestas           |
| `quotes`           | Cantidad de citas                |
| `views`            | Cantidad de visualizaciones      |
| `conversation_id`  | Identificador de la conversación |
| `in_reply_to`      | Tweet al que responde            |
| `in_reply_to_user` | Usuario del tweet respondido     |
| `mentioned_users`  | Usuarios mencionados             |
| `hashtags`         | Hashtags utilizados              |
| `lang`             | Idioma detectado                 |
| `url`              | URL del tweet                    |

---

# Conversaciones

Cada tweet puede pertenecer a una conversación identificada mediante `conversation_id`.

Por ejemplo:

```text
Tweet A
conversation_id = 100

    │
    ├── Tweet B
    │   in_reply_to = A
    │
    ├── Tweet C
    │   in_reply_to = A
    │
    └── Tweet D
        in_reply_to = B
```

Esto permite reconstruir la estructura de un hilo.

---

# Reconstrucción de hilos

Para reconstruir una conversación se utiliza:

```python
async for tweet in api.tweet_thread(
    int(tweet_id),
    limit=500,
):
    ...
```

El resultado se ordena por fecha.

El formato almacenado es:

```json
{
    "conversation_id": "123456789",
    "tweets": [
        {
            "tweet_id": "123456789",
            "username": "usuario1"
        },
        {
            "tweet_id": "123456790",
            "username": "usuario2"
        }
    ]
}
```

Una conversación puede contener más tweets que los encontrados originalmente mediante la búsqueda.

Por este motivo, la reconstrucción del hilo se realiza como una etapa independiente de la búsqueda.

---

# Almacenamiento JSONL

Los datos se almacenan utilizando **JSON Lines (JSONL)**.

Cada línea representa un registro independiente.

Ejemplo:

```text
{"tweet_id":"1", ...}
{"tweet_id":"2", ...}
{"tweet_id":"3", ...}
```

Esto permite:

* procesar los registros individualmente;
* agregar nuevos datos sin reconstruir todo el archivo;
* trabajar con datasets grandes;
* conservar una estructura sencilla y portable.

Para leer los tweets:

```python
import json

with open(
    "data/tweets.jsonl",
    encoding="utf-8"
) as file:

    for line in file:

        tweet = json.loads(line)

        print(tweet["username"])
        print(tweet["text"])
```

---

# Evitar duplicados

La función de almacenamiento comprueba los identificadores existentes antes de agregar nuevos registros.

Para los tweets se utiliza:

```text
tweet_id
```

Para las conversaciones se utiliza:

```text
conversation_id
```

De esta forma, ejecutar nuevamente una búsqueda no debería agregar registros idénticos al archivo existente.

---

# Configuración de cuentas

`twscrape` utiliza cuentas de X para realizar las solicitudes.

Las cuentas se administran mediante la base local de cuentas de `twscrape`.

Las credenciales y datos de autenticación son información privada y **no deben subirse al repositorio**.

Si una cuenta deja de estar disponible temporalmente debido a límites de solicitudes, `twscrape` puede esperar hasta que una cuenta vuelva a estar disponible.

El uso de varias cuentas permite distribuir las solicitudes entre las cuentas configuradas.

---

# Instalación

Crear un entorno virtual:

```bash
python -m venv .venv
```

Activarlo:

```bash
source .venv/bin/activate
```

Instalar las dependencias:

```bash
pip install -r requirements.txt
```

---

# Configuración de twscrape

Las cuentas pueden administrarse utilizando la interfaz de línea de comandos de `twscrape`.

Para consultar las opciones disponibles:

```bash
twscrape --help
```

Para consultar las cuentas configuradas:

```bash
twscrape accounts
```

También pueden consultarse las estadísticas:

```bash
twscrape stats
```

El procedimiento exacto de autenticación depende de la configuración de las cuentas y de los mecanismos de autenticación disponibles en X.

---

# Ejecución

Con el entorno virtual activado:

```bash
python -m src.main
```

El programa realiza la búsqueda configurada y muestra información sobre el proceso.

Ejemplo:

```text
Iniciando cliente...
Buscando: "Argentina since:2026-07-19 until:2026-07-20"
Tweets encontrados: 24
Tweets guardados en: data/tweets.jsonl
Conversaciones únicas: 24
Reconstruyendo conversación ...
...
Hilos guardados en: data/threads.jsonl

Proceso terminado.
```

---

# Pruebas de reconstrucción de conversaciones

Durante el desarrollo se utiliza un script independiente para comprobar la cantidad de tweets recuperados de una conversación:

```text
test_thread_info.py
```

Este script permite probar distintos valores de `limit`.

Por ejemplo:

```text
limit=50  -> tweets=95
limit=100 -> tweets=131
limit=200 -> tweets=222
limit=300 -> tweets=311
limit=500 -> tweets=315
limit=1000 -> tweets=316
```

Esto permite determinar experimentalmente cuándo `tweet_thread()` deja de devolver nuevos tweets para una conversación determinada.

El script es una herramienta de prueba y no forma parte del pipeline principal.

---

# Reproducibilidad

Para facilitar la reproducción del experimento se mantienen separadas:

* la configuración;
* el código de recolección;
* los datos recolectados;
* la documentación.

Las consultas y ventanas temporales utilizadas se encuentran en:

```text
src/config.py
```

Los datos obtenidos durante las pruebas se almacenan localmente en:

```text
data/
```

---

# Privacidad y seguridad

El proyecto trabaja con información pública de X, pero los datos recolectados pueden contener identificadores, nombres de usuario y contenido publicado.

Por este motivo:

* no se deben almacenar credenciales en Git;
* no se deben publicar cookies;
* no se deben publicar bases de autenticación;
* no se deben subir datasets innecesarios;
* se debe revisar qué información es necesaria para el análisis;
* se debe considerar la anonimización antes de distribuir los datos;
* se deben respetar las condiciones de uso de la plataforma y la legislación aplicable.

---

# Archivos que no deben subirse

El repositorio no debe contener información privada ni datos generados localmente durante las pruebas.

Entre ellos:

```text
.env
accounts.db
cookies.json
```

Tampoco deberían subirse los datasets recolectados:

```text
data/*.jsonl
data/*.db
```

El archivo `.gitignore` se utiliza para evitar incluir estos archivos accidentalmente.

El archivo:

```text
.env.example
```

puede utilizarse como referencia para documentar las variables necesarias sin incluir valores privados.

---

# Estado del proyecto

Actualmente el pipeline permite:

* [x] Configuración de búsquedas
* [x] Cliente `twscrape`
* [x] Recolección de tweets
* [x] Conversión a JSONL
* [x] Detección de conversaciones
* [x] Reconstrucción de conversaciones
* [x] Ordenamiento cronológico de los tweets
* [x] Prevención de tweets duplicados
* [x] Prevención de conversaciones duplicadas
* [x] Uso de múltiples cuentas mediante `twscrape`

---

# Posibles extensiones

Una vez establecida la recolección básica pueden implementarse:

## Recolección

* más consultas;
* más ventanas temporales;
* recolección por intervalos;
* recuperación de conversaciones más profundas;
* manejo de errores y reintentos.

## Análisis

* análisis temporal;
* análisis de usuarios;
* análisis de hashtags;
* análisis de menciones;
* análisis de respuestas;
* análisis del contenido textual;
* clasificación de publicaciones.

## Visualización

Los datos almacenados en JSONL pueden utilizarse posteriormente para generar tablas, estadísticas y visualizaciones sin modificar el proceso de recolección.

---

# Documentación

La documentación adicional se encuentra en:

```text
docs/
├── metodologia.md
└── esquema_datos.md
```

Estos documentos describen la metodología del proyecto y la estructura de los datos utilizados.
