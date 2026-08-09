# Budget Lens

MVP 0 local-first para registrar cuentas y deudas y obtener una primera recomendación explicable.

## Desarrollo

```bash
python3 backend/app.py
npm install
npm run dev
```

Abrir `http://127.0.0.1:5173` desde el equipo local o `http://IP_DEL_EQUIPO:5173` desde la red. La API escucha en el puerto `8000` y el frontend la busca en el mismo host.

Por defecto escucha en `0.0.0.0` para permitir acceso de red. Úsalo únicamente en una LAN/VPN confiable mientras no exista autenticación. Los datos se guardan en `backend/budget-lens.sqlite` y no deben versionarse.

Variables opcionales: `BUDGET_LENS_HOST`, `BUDGET_LENS_PORT`, `BUDGET_LENS_DB` y `BUDGET_LENS_CORS_ORIGIN`.

## Entrada por correo

La sincronización usa IMAP sobre TLS y solo lectura. Configura una bandeja dedicada y una contraseña de aplicación en el entorno donde corre la API; nunca guardes estos valores en el repositorio:

```bash
export BUDGET_LENS_IMAP_HOST=imap.example.com
export BUDGET_LENS_EMAIL_USER=finanzas@example.com
export BUDGET_LENS_EMAIL_PASSWORD='contraseña-de-aplicación'
export BUDGET_LENS_EMAIL_ALLOWED_SENDERS='banco@example.com,tarjeta@example.com'
python3 backend/app.py
```

Opcionales: `BUDGET_LENS_IMAP_PORT` (993), `BUDGET_LENS_IMAP_FOLDER` (INBOX) y `BUDGET_LENS_EMAIL_INBOX` (`data/email-inbox`). Solo se aceptan adjuntos PDF/JPG/PNG; se descargan localmente y quedan como `pending_review`. La aplicación no marca, borra ni responde correos.

## Acceso por Docker

Para usar el mismo patrón de despliegue que Vigilant:

```bash
docker compose up --build -d
```

La interfaz queda en `http://IP_DEL_SERVIDOR:28080` y la API se mantiene interna al compose. El puerto `18080` continúa perteneciendo exclusivamente a Vigilant.
