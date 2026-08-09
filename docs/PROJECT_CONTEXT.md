# Contexto vivo del proyecto

Última actualización: 2026-08-09

## Propósito

Budget Lens es un asistente para finanzas personales orientado a entender facturas, estados de cuenta y deudas, y a construir un plan claro para pagarlas más rápido.

## Estado actual

- El proyecto está en implementación inicial del MVP 0.
- Se definió el nombre del repositorio como `budget-lens`.
- La base documental persiste en `AGENTS.md`, `docs/PROJECT_CONTEXT.md`, `docs/DECISIONS.md` y `docs/SESSION_HANDOFF_TEMPLATE.md`.
- La dirección inicial es local-first: primero capturar y entender documentos, después automatizar análisis y recomendaciones.
- Arquitectura inicial aceptada: aplicación local/PWA, SQLite, documentos locales, OCR local y modelo local.
- Integraciones iniciales aceptadas: Binance mediante API de solo lectura y correo como entrada principal para todos los estados de cuenta.
- La primera base ejecutable incluye frontend React/Vite, API local en Python, SQLite y registro manual de cuentas/deudas.
- La aplicación local escucha en `0.0.0.0` por defecto para permitir acceso desde otra ubicación de red; el frontend calcula la API usando el hostname actual.
- Se añadió un despliegue Docker Compose con frontend en `28080` y API interna en `8000`; `18080` queda reservado exclusivamente para Vigilant.
- El MVP 0 también contempla ingresos, gastos recurrentes y metas de ahorro.
- Primera factura procesada: ENSA, gasto recurrente de B/.13.10 con vencimiento el día 29; el modelo conserva proveedor y vencimiento, mientras el consumo histórico queda pendiente de un módulo específico de servicios.
- El frontend aún no tiene build validado porque las dependencias npm no están disponibles en caché y el registro no respondió desde el entorno de ejecución.
- El código está preparado para versionarse en Git; los documentos financieros y artefactos generados quedan excluidos mediante `.gitignore`.
- Se implementó una primera ingestión de correo IMAP sobre TLS y solo lectura: descarga adjuntos permitidos a `data/email-inbox/`, deduplica por hash y los deja como `pending_review`; aún queda por definir el proveedor concreto y los remitentes autorizados.
- Se registró la primera factura estructurada: Tigo, factura `0093522378`, emitida el 2026-07-20 por B/.37.60, con XML como fuente de datos y PDF como respaldo; permanece `pending_payment` y no se convirtió automáticamente en gasto recurrente.
- Codex usa `.codex/config.toml` con `approval_policy = "on-request"` y `sandbox_mode = "workspace-write"`; las acciones fuera del workspace y el acceso de red requieren aprobación.
- `AGENTS.md` permite delegar hasta tres subtareas independientes, priorizando investigación y validaciones; el agente principal conserva decisiones, integración y verificación final.

## Intención del producto

- Ingerir facturas, estados de cuenta y otros documentos financieros.
- Extraer datos útiles con el menor fricción posible.
- Ayudar a priorizar pagos para reducir deuda más rápido.
- Mantener una postura fuerte de privacidad desde el inicio.

## Camino inicial

1. Construir el MVP 0 con cuentas, ingresos, gastos, deudas, vencimientos y metas de ahorro manuales.
2. Añadir carga de PDF/imagen y OCR local con revisión humana obligatoria.
3. Incorporar un modelo de deuda que compare avalanche y snowball.
4. Añadir modelo local para clasificación y explicación, manteniendo los cálculos en reglas verificables.
5. Integrar Binance con una clave restringida a lectura.
6. Integrar un buzón dedicado como entrada de todos los estados de cuenta, incluido ProFuturo, con procesamiento local controlado.
7. Evaluar sincronización bancaria y despliegue remoto solo después de validar el flujo local.

## Preguntas abiertas

- ¿Se prioriza pagar antes la deuda con mayor tasa o la de menor saldo?
- ¿Se aceptará conexión a cuentas bancarias en una fase posterior?
- ¿Qué información debe quedar siempre local y qué podría sincronizarse opcionalmente?
- ¿Qué proveedor de correo se usará para la bandeja financiera dedicada?
- ¿Qué remitentes y formatos de adjuntos se aceptarán inicialmente?
- ¿Qué modelo local se podrá ejecutar razonablemente en el equipo objetivo?
