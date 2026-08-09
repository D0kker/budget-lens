# Instrucciones persistentes del proyecto

## Al comenzar una sesión

- Lee `docs/PROJECT_CONTEXT.md` antes de proponer o realizar cambios.
- Lee `docs/DECISIONS.md` cuando la tarea afecte arquitectura, ingestión de documentos, seguridad, persistencia o automatización.
- Comprueba el estado real del repositorio; la documentación orienta, pero el código es la evidencia final.
- Responde en español salvo que el usuario pida otro idioma.

## Forma de trabajo

- Prioriza una arquitectura local-first mientras el alcance siga siendo exploratorio.
- No guardes credenciales, tokens, números de cuenta ni documentos financieros crudos en el repositorio, logs o prompts persistidos.
- Antes de conectar servicios externos, sincronización bancaria o almacenamiento en la nube, explica el impacto de privacidad y los datos que saldrían del equipo.
- Para cambios funcionales, implementa y valida en proporción al riesgo.
- Conserva los cambios existentes del usuario y evita operaciones destructivas sin autorización explícita.

## Delegación con subagentes

- Para tareas simples o secuenciales, trabaja con un solo agente.
- Delega cuando la tarea sea compleja y tenga al menos dos subtareas independientes que puedan avanzar en paralelo sin editar los mismos archivos.
- Prioriza subagentes para exploración del repositorio, investigación, análisis de documentos, revisión de seguridad, ejecución de pruebas y comprobaciones mecánicas.
- Evita delegar escrituras simultáneas sobre archivos o módulos relacionados. Si hay implementación paralela, asigna a cada subagente un alcance y archivos exclusivos.
- Usa como máximo tres subagentes a la vez salvo que el usuario solicite explícitamente otra cosa.
- Entrega a cada subagente un objetivo concreto, contexto mínimo, restricciones, archivos permitidos y evidencia esperada.
- Los subagentes no toman decisiones arquitectónicas duraderas ni realizan acciones externas, destructivas o sensibles sin autorización del agente principal y del usuario cuando corresponda.
- El agente principal revisa los resultados, resuelve contradicciones, integra los cambios y ejecuta la validación final. No presenta como terminado trabajo que solo fue reportado por un subagente.
- Los subagentes devuelven resúmenes concisos con hallazgos, archivos modificados, pruebas ejecutadas, riesgos y asuntos pendientes; evita copiar logs extensos al hilo principal.

### Prompt reutilizable para trabajo complejo

```text
Trabaja como agente principal en este repositorio. Lee primero AGENTS.md y los documentos de contexto aplicables. Analiza la tarea y delega únicamente las subtareas que sean realmente independientes.

Puedes usar hasta tres subagentes en paralelo. Da a cada uno un objetivo acotado, archivos exclusivos, restricciones y la evidencia que debe devolver. Prioriza la delegación para investigación, exploración, pruebas y revisiones; evita que dos agentes editen los mismos archivos.

Mantén en el agente principal las decisiones de arquitectura, privacidad, integración y alcance. Revisa personalmente cada resultado, integra los cambios, ejecuta la validación final del proyecto y actualiza PROJECT_CONTEXT.md o DECISIONS.md cuando corresponda.

Tarea: <describe aquí el resultado deseado, restricciones y criterios de aceptación>.
```

## Mantener la continuidad

- Si una tarea cambia el estado, los comandos, la arquitectura o el roadmap, actualiza `docs/PROJECT_CONTEXT.md` en el mismo cambio.
- Si se toma una decisión duradera o se reemplaza una anterior, regístrala en `docs/DECISIONS.md` con fecha, estado, razón y consecuencias.
- No conviertas ideas tentativas en decisiones aceptadas. Regístralas como preguntas abiertas.
- Mantén estos documentos concisos y elimina información que haya quedado obsoleta.

## Verificación mínima

- Documentación o configuración solamente: revisa enlaces, comandos y `git diff --check`.
- Cuando exista código ejecutable, agrega validación específica del cambio antes de cerrar la sesión.
