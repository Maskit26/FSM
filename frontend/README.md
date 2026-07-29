# FSM Platform Frontend

Консоль арендатора для [Vercel](https://vercel.com/): лендинг (Public Auth) и дашборд (Tenant Account).

## Локально

```bash
cd frontend
cp .env.example .env.local
# NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
npm install
npm run dev
```

Откройте http://localhost:3000

На платформе (`.env`) задайте:

```
CORS_ORIGINS=http://localhost:3000
TENANT_AUTH_EXPOSE_TOKENS=1
```

## Vercel

1. Root Directory: `frontend`
2. Env: `NEXT_PUBLIC_API_BASE_URL` — публичный URL platform API
3. На API: `CORS_ORIGINS=https://<your-app>.vercel.app`

## Страницы

| Путь | API |
|------|-----|
| `/` | `POST /v1/auth/register`, `verify-email`, `login` |
| `/dashboard` | `GET/POST /v1/tenant/admin-tokens…`, `POST /v1/tenant/domains`, `PUT/GET /v1/{service_id}/secrets`, `POST /v1/{service_id}/connect` |
