# LeadFlow Bot

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![aiogram](https://img.shields.io/badge/aiogram-3.x-blue)
![FastAPI](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)

**LeadFlow Bot** — Telegram-бот для автоматизации сбора и обработки заявок (лидов).

Пользователь заполняет форму прямо в Telegram, данные сохраняются в PostgreSQL, администратор получает уведомление, а заявка автоматически передаётся во внешние сервисы через webhook — в Make (Integromat) и далее в Google Sheets.

---

## Функционал

- **Сбор заявок через Telegram** — пошаговая форма на основе FSM (Finite State Machine)
- **Валидация данных** — проверка формата телефона и email на стороне бота
- **Сохранение в PostgreSQL** — асинхронная работа с базой через SQLAlchemy 2.0
- **Уведомление администратора** — мгновенное сообщение при поступлении новой заявки
- **Webhook-интеграция** — автоматическая отправка данных в Make (Integromat)
- **Экспорт в Google Sheets** — запись лидов в таблицу через Google Sheets API

---

## Архитектура и поток данных

```
Пользователь
    │
    ▼
Telegram Bot (aiogram 3.x, FSM)
    │
    ├──► PostgreSQL (сохранение заявки)
    │
    ├──► Уведомление администратору (Telegram)
    │
    └──► Webhook → Make (Integromat)
                        │
                        └──► Google Sheets (новая строка с данными лида)
```

**Описание шагов:**

1. Пользователь запускает бота командой `/start`
2. Бот запускает FSM-форму: имя → телефон → email → комментарий
3. После завершения формы данные валидируются и сохраняются в БД
4. Одновременно:
   - администратор получает Telegram-уведомление с данными заявки
   - сервис отправляет POST-запрос на webhook-URL (Make)
5. Make обрабатывает входящий запрос и записывает данные в Google Sheets

---

## Структура проекта

```
leadflow-bot/
│
├── bot/
│   ├── handlers/
│   │   ├── start.py          # Обработчик /start, приветствие
│   │   ├── form.py           # FSM-форма сбора заявки
│   │   └── common.py         # Общие обработчики (отмена, помощь)
│   │
│   ├── keyboards/
│   │   ├── menu.py           # Главное меню
│   │   └── form_kb.py        # Клавиатуры для шагов формы
│   │
│   ├── services/
│   │   ├── lead_service.py           # Бизнес-логика: создание лида
│   │   ├── google_sheets_service.py  # Запись в Google Sheets
│   │   └── notification_service.py   # Уведомления администратору
│   │
│   ├── integrations/
│   │   ├── google_sheets.py   # Клиент Google Sheets API
│   │   └── webhook_sender.py  # HTTP-клиент для отправки webhook
│   │
│   ├── database/
│   │   ├── models.py     # SQLAlchemy-модели
│   │   ├── schemas.py    # Pydantic-схемы
│   │   ├── enums.py      # Перечисления (статусы лидов и т.д.)
│   │   ├── db_helper.py  # Фабрика сессий, движок
│   │   └── base.py       # Базовый класс моделей
│   │
│   ├── states/
│   │   └── lead_form.py  # Состояния FSM-формы
│   │
│   ├── utils/
│   │   └── validators.py # Валидаторы телефона и email
│   │
│   └── config.py         # Настройки приложения (pydantic-settings)
│
├── migrations/            # Alembic-миграции
├── main.py                # Точка входа
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

---

## Переменные окружения

Создайте файл `.env` в корне проекта на основе примера ниже:

```env
# Telegram
BOT_TOKEN=your_telegram_bot_token

# База данных
POSTGRES_DB=leadflow_bot
POSTGRES_USER=leadflow_bot_user
POSTGRES_PASSWORD=your_secure_password

# Администратор
ADMIN_CHAT_ID=123456789

# Webhook (Make / Integromat)
WEBHOOK_URL=https://hook.eu2.make.com/your_webhook_id

# Google Sheets
GOOGLE_SHEET_ID=your_spreadsheet_id
GOOGLE_CREDENTIALS_PATH=credentials.json

# pgAdmin (опционально)
PGADMIN_DEFAULT_EMAIL=admin@admin.org
PGADMIN_DEFAULT_PASSWORD=admin
```

> ⚠️ Никогда не добавляйте `.env` и `credentials.json` в git. Убедитесь, что они указаны в `.gitignore`.

---

## Настройка webhook (Make / Integromat)

Webhook — это механизм, при котором бот сам инициирует HTTP-запрос на внешний URL сразу после сохранения заявки. Вам не нужно опрашивать бота вручную: данные поступают в Make мгновенно.

### Шаг 1. Создание сценария в Make

1. Зайдите в [make.com](https://make.com) и создайте новый сценарий
2. В качестве триггера выберите модуль **Webhooks → Custom webhook**
3. Нажмите **Add** → **Save** — Make сгенерирует уникальный URL вида:
   ```
   https://hook.eu2.make.com/abcdef1234567890
   ```
4. Скопируйте этот URL и вставьте в `.env` как значение `WEBHOOK_URL`

### Шаг 2. Структура запроса

Бот отправляет POST-запрос с JSON-телом:

```json
{
  "name": "Иван Иванов",
  "phone": "+79991234567",
  "email": "ivan@example.com",
  "comment": "Хочу узнать подробнее",
  "created_at": "2026-03-15T14:30:00"
}
```

### Шаг 3. Обработка данных в Make

После первого запроса Make автоматически определит структуру данных.
Добавьте следующий модуль в цепочку:

- **Google Sheets → Add a Row** — укажите таблицу и сопоставьте поля из webhook с колонками

### Шаг 4. Активация сценария

Переключите сценарий в режим **On** — теперь каждая новая заявка будет автоматически появляться в таблице.

---

## Настройка Google Sheets API

1. Откройте [Google Cloud Console](https://console.cloud.google.com/)
2. Создайте проект и включите **Google Sheets API**
3. Создайте сервисный аккаунт и скачайте JSON-ключ как `credentials.json`
4. Добавьте email сервисного аккаунта как редактора в вашу Google-таблицу
5. Укажите ID таблицы в переменной `GOOGLE_SHEET_ID` (часть URL после `/d/`)

---

## Запуск

### Через Docker Compose (рекомендуется)

```bash
# 1. Клонируйте репозиторий
git clone https://github.com/NVLev/leadflow-bot.git
cd leadflow-bot

# 2. Создайте .env файл
cp .env.example .env
# Заполните значения в .env

# 3. Запустите
docker-compose up --build
```

Сервисы после запуска:
| Сервис | URL |
|--------|-----|
| Бот | работает в фоне |
| Adminer | http://localhost:8080 |
| pgAdmin | http://localhost:5050 |



---

## Применение миграций

```bash
# Внутри контейнера
docker-compose exec app alembic upgrade head

# Создание новой миграции после изменения моделей
docker-compose exec app alembic revision --autogenerate -m "description"
```

---

## Стек технологий

| Компонент | Технология |
|-----------|-----------|
| Язык | Python 3.11+ |
| Telegram | aiogram 3.x |
| База данных | PostgreSQL 16 + SQLAlchemy 2.0 (async) |
| Миграции | Alembic |
| Валидация | Pydantic v2 |
| Интеграции | Make (Integromat), Google Sheets API |
| Инфраструктура | Docker, Docker Compose |