# FSM Platform Frontend

Консоль арендатора: лендинг → регистрация домена → личный кабинет.

## Локально

```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

http://localhost:3000

На платформе: `CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000` и
`TENANT_AUTH_EXPOSE_TOKENS=1`.

## Страницы

| Путь | Назначение |
|------|------------|
| `/` | Public Auth |
| `/domain-registration` | Token → register domain → secrets → connect (автоскролл) |
| `/dashboard` | ЛК: плитки |
| `/playground` | Операции: catalog/invoke, сущности, events |

После connect флаг `fsm_domain_connected` ведёт на `/dashboard` при следующем login.
