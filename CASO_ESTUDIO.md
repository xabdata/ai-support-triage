# AI Support Triage

Proyecto personal de una API que analiza solicitudes de soporte con un modelo de lenguaje, conserva los resultados y permite consultar el historial.

## Problema y solución

El proyecto aborda la clasificación inicial de solicitudes de soporte. A partir de un asunto y una descripción, determina la categoría y prioridad, genera un resumen y propone una siguiente acción y un borrador de respuesta para revisión humana.

## Implementación

FastAPI recibe las solicitudes y Pydantic valida los datos. La integración directa con la API de OpenAI devuelve resultados estructurados. SQLAlchemy guarda la solicitud y el resultado en PostgreSQL.

La aplicación incluye consulta del historial, gestión básica de errores y rollback ante fallos durante la transacción de guardado. Docker Compose permite ejecutar la API y PostgreSQL localmente.

Tecnologías: Python 3.12, FastAPI, Pydantic, OpenAI, SQLAlchemy, PostgreSQL, Docker Compose y pytest.

## Validación y resultados

La suite cuenta con 28 pruebas superadas que utilizan servicios simulados. El recorrido completo también se verificó manualmente con OpenAI y PostgreSQL reales.

En un conjunto de 20 casos, incorporar una rúbrica al prompt mejoró el acierto de categoría del 80 % al 95 %, la prioridad del 55 % al 70 % y ambas etiquetas simultáneamente del 45 % al 65 %.

Los mismos casos se utilizaron para ajustar y evaluar el prompt; los resultados no constituyen una evaluación independiente ni garantizan rendimiento en producción. Los textos generados requieren revisión humana.

## Repositorio y demostración

Código e instrucciones para reproducir la demostración local:

https://github.com/xabdata/ai-support-triage
