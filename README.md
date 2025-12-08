# FSM Delivery Platform

**FSM (Finite State Machine) Delivery Platform** — это backend-система для управления логистикой курьерской доставки с использованием постаматов. Реализована на FastAPI с автоматизированной обработкой состояний заказов через фоновый воркер FSM.

Система полностью поддерживает жизненный цикл заказа: от создания и резервирования ячеек постамата, до доставки и подтверждения получения посылки разными участниками (клиент, курьеры, водитель, оператор).

## Стек технологий

- **Python 3.11** + FastAPI
- **MySQL 8.x** (база данных с полной схемой FSM)
- **Systemd** (управление сервисами)
- **Caddy** (reverse proxy + HTTPS)

## Предварительные требования

- Ubuntu 22.04/24.04 LTS
- Права sudo для установки пакетов
- Доменное имя (например, `api.xn--8-ytbb.store`)
- Cloudflare API token (для автоматической выдачи SSL-сертификатов)
- Git установлен

## Структура проекта

```
FSM/
├── main.py                 # FastAPI приложение с REST API
├── db_layer.py             # Слой доступа к БД (63 KB)
├── fsm_actions.py          # Действия FSM (смена состояний)
├── fsm_engine.py           # Ядро FSM логики
├── fsm_worker.py           # Фоновый воркер (постоянно крутится в фоне)
├── models.py               # SQLAlchemy модели
├── requirements.txt        # Python-зависимости
├── .gitignore              # Git исключения
├── Dockerfile              # Конфиг Docker (опционально)
├── database/               # SQL-дампы для восстановления БД
│   └── Dump*.sql           # Дампы базы данных
└── __pycache__/            # Кэш Python (игнорируется в git)
```

## Архитектура базы данных

### Основные таблицы

**FSM и состояния:**
- `fsmstates` — Состояния (ordercreated, ordercourierreserved, ordercompleted и т.д.) — 103+ состояния
- `fsmactions` — Действия/переходы (orderassigncourier, tripstarttrip и т.д.) — 105+ действий
- `fsmtransitions` — Переходы между состояниями и действиями
- `buttonstates` — Связь кнопок UI с ролями и состояниями (63 конфигурации)

**Доставка:**
- `orders` — Заказы с источником/назначением, статусом, типом доставки
- `trips` — Рейсы водителей (Мск → Спб и т.д.)
- `stageorders` — Связь заказов и рейсов (pickup/delivery этап, назначенный курьер)
- `orderrequests` — Запросы на создание заказа с обработкой ошибок

**Постаматы:**
- `lockers` — Постаматы (4+ штук, Мск и регионы)
- `lockercells` — Ячейки постаматов (S/M/L/P размеры) — 46+ ячеек
- `lockermodels` — Модели постаматов с конфигурацией размеров

**Пользователи и роли:**
- `users` — Пользователи (client, courier, driver, operator, recipient) — 305+ пользователей

**Логирование:**
- `fsmactionlogs` — История всех FSM-действий с временными метками
- `fsmerrorslog` — Логи ошибок FSM с обработкой
- `hardwarecommandlog` — История команд к оборудованию (открыть/закрыть ячейку)

**Управление состояниями:**
- `serverfsminstances` — Текущие экземпляры FSM-процессов для отслеживания

### Особенности базы

- **Транзакции на уровне БД** — Triggers для проверки корректности состояний
- **Автоматическая очистка** — Events для удаления старых логов (>90 дней)
- **Таймауты** — Events для обработки таймаутов резервирования и доставки
- **Stored Procedures** — `fsmperformaction` — основная процедура для всех переходов FSM

## Пошаговая установка на Linux VPS

### Шаг 1. Подготовка системы и установка Python 3.11

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.11 python3.11-venv python3.11-dev build-essential libmysqlclient-dev git curl
python3.11 --version
```

### Шаг 2. Установка MySQL и создание базы данных

```bash
sudo apt install -y mysql-server
sudo systemctl enable --now mysql

# Создание БД и пользователя
sudo mysql -u root <<EOF
CREATE DATABASE testdb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'fsm'@'localhost' IDENTIFIED BY 'YOUR_STRONG_PASSWORD';
GRANT ALL PRIVILEGES ON testdb.* TO 'fsm'@'localhost';
FLUSH PRIVILEGES;
EXIT;
EOF
```

### Шаг 3. Клонирование проекта с GitHub

```bash
cd /opt
sudo git clone https://github.com/Maskit26/FSM.git
cd FSM
sudo chown -R $USER:$USER /opt/FSM
```

### Шаг 4. Восстановление БД из дампа

В папке `database/` находится SQL-дамп со всей схемой, данными и процедурами:

```bash
cd /opt/FSM
mysql -u fsm -pYOUR_STRONG_PASSWORD testdb < database/Dump20251207-3.sql
```

Это создаст:
- **Все таблицы** (orders, trips, lockers, users, FSM tables)
- **Triggers** для валидации состояний
- **Events** для таймаутов и очистки
- **Stored Procedure** `fsmperformaction` для FSM переходов
- **Тестовые данные** (4 постамата, 46 ячеек, 305+ пользователей, 10 заказов)

### Шаг 5. Создание виртуального окружения

```bash
cd /opt/FSM
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Шаг 6. Настройка переменных окружения

Создайте файл `/opt/FSM/.env`:

```env
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=fsm
DB_PASSWORD=YOUR_STRONG_PASSWORD
DB_NAME=testdb
```

Убедитесь, что `db_layer.py` и `main.py` читают эти переменные через `os.getenv()` или `python-dotenv`.

### Шаг 7. Создание systemd-сервисов

#### 7.1 FastAPI-сервис

Создайте файл `/etc/systemd/system/fsm-api.service`:

```ini
[Unit]
Description=FSM FastAPI API Service
After=network.target mysql.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/opt/FSM
Environment="PATH=/opt/FSM/venv/bin"
ExecStart=/opt/FSM/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
Restart=always
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

#### 7.2 FSM Worker-сервис

**ВАЖНО:** `fsm_worker.py` должен крутиться постоянно в фоне для обработки FSM-событий (таймауты, смена состояний и т.д.).

Создайте файл `/etc/systemd/system/fsm-worker.service`:

```ini
[Unit]
Description=FSM Background Worker
After=network.target mysql.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/FSM
Environment="PATH=/opt/FSM/venv/bin"
ExecStart=/opt/FSM/venv/bin/python fsm_worker.py
Restart=always
RestartSec=5s
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

#### 7.3 Активация сервисов

```bash
sudo systemctl daemon-reload
sudo systemctl enable fsm-api.service fsm-worker.service
sudo systemctl start fsm-api.service fsm-worker.service

# Проверка статуса
sudo systemctl status fsm-api.service
sudo systemctl status fsm-worker.service

# Просмотр логов воркера (очень важно для отладки)
sudo journalctl -u fsm-worker.service -f
```

### Шаг 8. Установка и настройка Caddy (reverse proxy + HTTPS)

```bash
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list

sudo apt update
sudo apt install -y caddy
```

Создайте файл `/etc/caddy/Caddyfile`:

```caddyfile
# FastAPI backend
api.xn--8-ytbb.store {
    reverse_proxy localhost:8000
    
    tls {
        dns cloudflare YOUR_CLOUDFLARE_API_TOKEN
        propagation_delay 60s
    }
    
    encode gzip
}
```

**Замените `YOUR_CLOUDFLARE_API_TOKEN`** на ваш реальный токен.

Запустите Caddy:

```bash
sudo systemctl restart caddy
sudo systemctl enable caddy
sudo systemctl status caddy
```

### Шаг 9. Проверка работоспособности

```bash
# Проверить, что API отвечает
curl http://localhost:8000/docs

# Проверить Swagger UI через HTTPS
curl https://api.xn--8-ytbb.store/docs

# Проверить логи FastAPI
sudo journalctl -u fsm-api.service -n 50 -f

# Проверить логи воркера (самый важный! Здесь видна обработка FSM)
sudo journalctl -u fsm-worker.service -n 50 -f
```

### Шаг 10. Настройка firewall (UFW)

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
sudo ufw status
```

## Примеры использования API

### Получить список заказов с фильтром по городам

```bash
curl https://api.xn--8-ytbb.store/api/orders?fromcity=Msk&tocity=Spb
```

### Получить ячейки конкретного постамата

```bash
curl https://api.xn--8-ytbb.store/api/lockers/1/cells
```

### Создать заказ

```bash
curl -X POST "https://api.xn--8-ytbb.store/api/orders/create?sourcecellid=2&destcellid=5&fromcity=Msk&tocity=Spb&title=Order&pickuptype=courier&deliverytype=courier"
```

### Получить триггеры FSM для заказа

```bash
curl "https://api.xn--8-ytbb.store/api/fsm-buttons?userrole=client&entitytype=order&entityid=1"
```

### Выполнить FSM-действие (смена состояния)

```bash
curl -X POST "https://api.xn--8-ytbb.store/api/fsm-action?entitytype=order&entityid=1&action=orderassigncourier&userid=20"
```

## Управление сервисами

### Просмотр статуса

```bash
sudo systemctl status fsm-api.service
sudo systemctl status fsm-worker.service
sudo systemctl status caddy
```

### Перезапуск после изменений кода

```bash
# Перезапустить FastAPI
sudo systemctl restart fsm-api.service

# Перезапустить воркер (очень важно при изменении fsm_worker.py)
sudo systemctl restart fsm-worker.service

# Перезапустить оба сервиса
sudo systemctl restart fsm-api.service fsm-worker.service
```

### Просмотр логов в реальном времени

```bash
# Логи API (REST запросы)
sudo journalctl -u fsm-api.service -f

# Логи воркера (FSM обработка — таймауты, переходы)
sudo journalctl -u fsm-worker.service -f

# Логи Caddy (HTTPS, reverse proxy)
sudo journalctl -u caddy -f
```

### Остановка сервисов

```bash
sudo systemctl stop fsm-api.service fsm-worker.service
```

## Мониторинг FSM

### Проверить текущие FSM-экземпляры в БД

```sql
mysql -u fsm -pYOUR_STRONG_PASSWORD -e "SELECT * FROM testdb.serverfsminstances;"
```

### Посмотреть историю FSM-действий

```sql
mysql -u fsm -pYOUR_STRONG_PASSWORD -e "SELECT * FROM testdb.fsmactionlogs ORDER BY createdat DESC LIMIT 20;"
```

### Посмотреть ошибки FSM

```sql
mysql -u fsm -pYOUR_STRONG_PASSWORD -e "SELECT * FROM testdb.fsmerrorslog ORDER BY errortime DESC LIMIT 10;"
```

### Посмотреть статус ячеек постамата

```sql
mysql -u fsm -pYOUR_STRONG_PASSWORD -e "SELECT id, cellcode, status, currentorderid FROM testdb.lockercells WHERE lockerid=1;"
```

## Резервное копирование БД

Создайте скрипт `/opt/FSM/backup.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/backup/fsm"
mkdir -p $BACKUP_DIR
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mysqldump -u fsm -pYOUR_STRONG_PASSWORD testdb | gzip > $BACKUP_DIR/fsm_$TIMESTAMP.sql.gz

# Удалить дампы старше 7 дней
find $BACKUP_DIR -name "fsm_*.sql.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_DIR/fsm_$TIMESTAMP.sql.gz"
```

Добавьте в crontab:

```bash
sudo crontab -e
```

И добавьте строку:

```
0 2 * * * /opt/FSM/backup.sh
```

## Обновление кода с GitHub

```bash
cd /opt/FSM
git pull origin main

# Если изменились зависимости
source venv/bin/activate
pip install -r requirements.txt

# Перезапустить сервисы
sudo systemctl restart fsm-api.service fsm-worker.service
```

## Решение проблем

### Воркер не запускается

```bash
sudo journalctl -u fsm-worker.service -n 100
# Проверьте ошибки в логах — часто это проблемы с подключением к БД
```

### API не отвечает

```bash
curl http://localhost:8000/health
sudo journalctl -u fsm-api.service -n 50
```

### Ошибка подключения к БД

```bash
# Проверить статус MySQL
sudo systemctl status mysql

# Проверить права пользователя fsm
mysql -u fsm -pYOUR_STRONG_PASSWORD -e "SELECT 1"

# Проверить переменные окружения в .env
cat /opt/FSM/.env
```

### FSM-переходы не работают

```bash
# Проверить, что stored procedure создалась в БД
mysql -u fsm -pYOUR_STRONG_PASSWORD -e "SHOW PROCEDURE STATUS WHERE Db='testdb';"

# Проверить логи воркера
sudo journalctl -u fsm-worker.service -f

# Проверить таблицу ошибок FSM
mysql -u fsm -pYOUR_STRONG_PASSWORD -e "SELECT * FROM testdb.fsmerrorslog ORDER BY errortime DESC LIMIT 5;"
```

### Caddy не выдаёт сертификат

```bash
# Проверить синтаксис Caddyfile
sudo caddy validate --config /etc/caddy/Caddyfile

# Перезапустить
sudo systemctl restart caddy
sudo journalctl -u caddy -n 50
```

## Требования к серверу

- **CPU:** 2 vCPU (для разработки/тестирования)
- **RAM:** 4 GB (для стабильной работы всех компонентов + БД)
- **Storage:** 50+ GB SSD (для БД + логов + резервных копий)
- **Порты:** 22 (SSH), 80 (HTTP), 443 (HTTPS)

## Переменные окружения (опционально)

Если нужны дополнительные конфигурации, добавьте в `.env`:

```env
# Database
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=fsm
DB_PASSWORD=YOUR_STRONG_PASSWORD
DB_NAME=testdb

# FastAPI
FASTAPI_ENV=production
LOG_LEVEL=info

# Worker
WORKER_INTERVAL=5       # Интервал обработки задач в секундах
WORKER_TIMEOUT=30       # Таймаут обработки одной задачи
FSM_CHECK_INTERVAL=10   # Интервал проверки FSM-событий
```

## Лицензия

MIT License

---

**Важно:** 
- Замените все `YOUR_STRONG_PASSWORD` на реальные пароли перед запуском в production
- Замените `YOUR_CLOUDFLARE_API_TOKEN` на ваш реальный токен
- Убедитесь, что DNS-запись вашего домена указывает на IP вашего VPS
- **Проверяйте логи воркера регулярно** для отладки FSM-переходов: `sudo journalctl -u fsm-worker.service -f`
- Сохраняйте регулярные резервные копии БД (минимум 1 раз в день)
- При разработке новых FSM-переходов тестируйте через БД: `CALL fsmperformaction('order', ID, 'action_name', userid, NULL)`
