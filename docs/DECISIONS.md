# Registro de decisiones

Este archivo registra decisiones duraderas. Estados permitidos: `propuesta`, `aceptada`, `reemplazada` y `descartada`.

## D-001 — Nombre del repositorio

- Fecha: 2026-08-09
- Estado: aceptada
- Decisión: usar `budget-lens` como nombre del repo.
- Razón: suena a producto y funciona bien como nombre corto para GitHub.
- Consecuencias: todos los artefactos persistentes del proyecto deben referirse a ese nombre.

## D-002 — Base documental persistente

- Fecha: 2026-08-09
- Estado: aceptada
- Decisión: mantener `AGENTS.md`, `docs/PROJECT_CONTEXT.md`, `docs/DECISIONS.md` y `docs/SESSION_HANDOFF_TEMPLATE.md` como fuente de continuidad entre sesiones.
- Razón: evitar perder contexto y separar estado vivo de decisiones duraderas.
- Consecuencias: cualquier cambio relevante debe reflejarse también en estos documentos.

## D-003 — Enfoque local-first inicial

- Fecha: 2026-08-09
- Estado: aceptada
- Decisión: comenzar sin depender de integraciones bancarias ni credenciales externas.
- Razón: reducir riesgo de privacidad y simplificar el primer ciclo del producto.
- Consecuencias: el MVP inicial debe funcionar con documentos cargados manualmente o mediante mecanismos equivalentes controlados por el usuario.

## D-004 — Doble estrategia de pago de deuda

- Fecha: 2026-08-09
- Estado: propuesta
- Decisión: evaluar tanto avalanche como snowball antes de fijar una estrategia por defecto.
- Razón: son las dos heurísticas principales para acelerar pagos y el valor real depende del perfil del usuario.
- Consecuencias: el producto debe poder comparar ambas y explicar el efecto esperado.

## D-005 — Permisos interactivos y sandbox de Codex

- Fecha: 2026-08-09
- Estado: aceptada
- Decisión: configurar Codex con `approval_policy = "on-request"`, escritura limitada al workspace y red desactivada dentro del sandbox.
- Razón: permitir trabajo local normal y solicitar confirmación cuando una acción requiera red o escritura fuera del proyecto.
- Consecuencias: hay que abrir `budget-lens` como proyecto confiable y reiniciar Codex después de cambiar `.codex/config.toml`.

## D-006 — Delegación acotada con subagentes

- Fecha: 2026-08-09
- Estado: aceptada
- Decisión: usar hasta tres subagentes solo para subtareas independientes, con alcances y archivos exclusivos; el agente principal mantiene las decisiones, integración y validación final.
- Razón: aprovechar el paralelismo sin contaminar el contexto principal ni provocar conflictos de escritura.
- Consecuencias: se priorizan exploración, investigación, pruebas y revisiones; las implementaciones paralelas deben estar claramente separadas y ningún resultado se acepta sin revisión del agente principal.

## D-007 — Arquitectura inicial del producto

- Fecha: 2026-08-09
- Estado: aceptada
- Decisión: iniciar con una aplicación local/PWA, SQLite, documentos locales, OCR local y un modelo local. Binance se conectará mediante API de solo lectura. Todos los estados de cuenta se incorporarán mediante un buzón financiero dedicado.
- Razón: maximizar privacidad y reducir dependencia de servicios externos, manteniendo automatización suficiente para el primer ciclo útil.
- Consecuencias: los cálculos financieros deben ejecutarse en reglas verificables; el modelo local se usará para clasificación y explicación, no como autoridad de saldos. El buzón debe aceptar únicamente remitentes y formatos definidos, descargar los adjuntos para procesamiento local, conservarlos cifrados y aplicar una política de retención y limpieza. No se guardarán credenciales de portales financieros. La clave de Binance no puede tener permisos de trading ni retiros.

## D-008 — Correo como entrada principal de estados de cuenta

- Fecha: 2026-08-09
- Estado: aceptada
- Decisión: utilizar una bandeja de correo dedicada como canal principal para recibir los estados de cuenta de bancos, tarjetas, ProFuturo y otros proveedores.
- Razón: el usuario ya recibe todos los estados de cuenta por correo, por lo que este canal reduce carga manual y permite una ingestión uniforme.
- Consecuencias: el proveedor de correo tendrá acceso temporal a documentos financieros. La aplicación debe procesar localmente, evitar guardar credenciales del usuario, filtrar remitentes y adjuntos, registrar el origen y fecha del documento, detectar duplicados y requerir revisión humana antes de actualizar saldos. La lectura de correo debe ser de mínimo privilegio y no debe enviar mensajes ni borrar correos automáticamente durante el primer MVP.
