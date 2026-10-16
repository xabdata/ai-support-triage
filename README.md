# AI Support Triage

API que analiza solicitudes de soporte con un modelo de lenguaje,
guarda los resultados en PostgreSQL y permite consultar el historial.

## Funcionalidades

- Valida el asunto y la descripción de cada solicitud.
- Determina su categoría y prioridad.
- Genera un resumen, recomienda la siguiente acción y propone un borrador de respuesta.
- Guarda la solicitud y el resultado.
- Permite consultar el historial.
- Devuelve respuestas controladas ante fallos de OpenAI o PostgreSQL.

## Tecnologías

Python 3.12, FastAPI, Pydantic, PostgreSQL, SQLAlchemy,
Docker Compose, API de OpenAI y pytest.

## Rutas

| Método | Ruta | Función |
|---|---|---|
| GET | /health | Comprobar que la API responde |
| POST | /triage | Analizar y guardar una solicitud |
| GET | /history | Consultar las solicitudes guardadas |
| GET | /docs | Abrir la documentación interactiva |

## Requisitos

- Docker Desktop instalado y en ejecución.
- Una clave de API de OpenAI con acceso y saldo disponibles.
- Conexión a Internet para descargar las imágenes y consultar OpenAI.

## Configuración

Desde la raíz del proyecto, crea tu archivo de configuración local:

```bash
cp -n .env.example .env
```

La opción `-n` evita sobrescribir un `.env` existente.

Abre `.env` en tu editor y configura:

- `OPENAI_API_KEY`: tu clave real de la API de OpenAI.
- `POSTGRES_DB`: nombre de la base de datos.
- `POSTGRES_USER`: usuario de PostgreSQL.
- `POSTGRES_PASSWORD`: contraseña para PostgreSQL.

Puedes conservar los valores de ejemplo de la base de datos y del usuario.
Debes sustituir los textos de ejemplo de la clave y la contraseña.

Al crear una base de datos nueva, Docker utiliza estas credenciales.
Si ya existe un volumen con datos, cambiar `.env` no cambia la contraseña
almacenada en PostgreSQL.

Nunca publiques `.env` ni incluyas secretos en `.env.example`.

## Ejecución con Docker

Con Docker Desktop abierto y `.env` configurado, ejecuta desde la raíz:

```bash
docker compose up --build --detach --wait
```

Este comando construye la imagen de la API y arranca los servicios
de FastAPI y PostgreSQL en segundo plano.

Comprueba que la API responde:

```bash
curl --fail --show-error http://127.0.0.1:8000/health
```

Respuesta esperada:

```json
{"status":"ok"}
```

Abre http://127.0.0.1:8000/docs para consultar la documentación
interactiva y probar las rutas.

Para detener los servicios conservando los datos:

```bash
docker compose down
```

Los registros permanecen en el volumen de PostgreSQL.

## Ejemplo de uso

Con los servicios en ejecución, envía una solicitud desde el terminal:

```bash
curl --include --request POST http://127.0.0.1:8000/triage --header 'Content-Type: application/json' --data '{"subject":"Necesito una copia de mi factura","description":"Quiero descargar una copia de la factura del mes pasado. No hay errores en el cobro y puedo seguir usando el servicio."}'
```

Esta petición realiza una llamada real a OpenAI y consume crédito.
Si termina correctamente, devuelve `200 OK` con estos campos:

- `category`
- `priority`
- `summary`
- `next_action`
- `draft_response`

Para este ejemplo se espera categoría `billing` y prioridad `low`.
El texto generado puede variar. El borrador requiere revisión humana.

Consulta el historial para comprobar que la solicitud quedó guardada:

```bash
curl --include http://127.0.0.1:8000/history
```

Los registros se muestran del más reciente al más antiguo.
Cada envío correcto a `/triage` crea un registro nuevo.

## Pruebas automáticas

Para ejecutar las pruebas localmente necesitas Conda.
Desde la raíz del proyecto, crea el entorno si todavía no lo tienes:

```bash
conda env create -f environment.yml
```

Si el entorno `ai_support_triage` ya existe, omite su creación.

Ejecuta la suite:

```bash
conda run -n ai_support_triage python -m pytest
```

Resultado verificado: **28 pruebas superadas**.

Las pruebas comprueban la validación de datos, las rutas HTTP,
la integración simulada con OpenAI, las operaciones de persistencia,
la gestión de errores y las funciones de evaluación.

Los servicios externos se simulan: estas pruebas no requieren
OpenAI ni PostgreSQL en ejecución y no consumen crédito de la API.
La evaluación real del modelo se ejecuta por separado.

## Evaluación del modelo

El proyecto incluye 20 casos en `evals/cases.json`.
Se comparan la categoría y la prioridad generadas con las esperadas.

Resultados registrados con `gpt-5.4-nano`:

| Métrica | Prompt inicial | Prompt con rúbrica |
|---|---:|---:|
| Categoría correcta | 80 % | 95 % |
| Prioridad correcta | 55 % | 70 % |
| Ambas correctas en el mismo caso | 45 % | 65 % |

Informes conservados:

- `evals/baseline_results.json`: resultado inicial.
- `evals/results.json`: resultado posterior a incorporar la rúbrica.

### Repetir la evaluación

Con el entorno Conda creado y la clave real configurada en `.env`,
ejecuta desde la raíz del proyecto:

```bash
set -a
source .env
set +a
conda run -n ai_support_triage python -m evals.run_evaluation
```

`set -a` permite que el proceso de Python reciba las variables cargadas.
`set +a` desactiva esa exportación automática después de cargar `.env`.

Esta operación realiza 20 llamadas reales a OpenAI, consume crédito
y sobrescribe `evals/results.json`. Los resultados pueden variar.

### Limitaciones

Los mismos 20 casos se utilizaron para evaluar y ajustar el prompt.
Los porcentajes no constituyen una evaluación independiente ni una
garantía de rendimiento en producción.

Las métricas automáticas solo puntúan categoría y prioridad.
El resumen, la siguiente acción y el borrador requieren revisión cualitativa.
La prioridad obtuvo un 70 % de acierto en la evaluación registrada.

## Respuestas HTTP

| Código | Significado |
|---|---|
| 200 | Operación completada correctamente |
| 422 | La solicitud no cumple el modelo de entrada |
| 405 | Se utilizó un método HTTP no permitido para esa ruta |
| 503 | Se capturó un error de OpenAI o de PostgreSQL |

Los errores controlados de las dependencias devuelven:

```json
{"detail":"Triage service is temporarily unavailable"}
```

La ruta `/health` comprueba que la API responde.
La conexión con PostgreSQL se comprueba consultando `/history`.
El recorrido completo se comprueba enviando una solicitud a `/triage`
y recuperándola después desde `/history`.

## Alcance de esta versión

El sistema clasifica solicitudes y propone textos para revisión humana.
No consulta cuentas reales, no realiza devoluciones y no envía respuestas
a clientes. Las acciones mencionadas en los borradores son propuestas,
no operaciones ejecutadas por la API.

La demostración está configurada para ejecutarse localmente.
