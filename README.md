# LeadFlow Bot

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![aiogram](https://img.shields.io/badge/aiogram-3.x-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)

**LeadFlow Bot** — Telegram-бот для автоматизации сбора и обработки заявок (лидов).

Пользователь заполняет форму прямо в Telegram, данные сохраняются в PostgreSQL, администратор получает уведомление с возможностью сменить статус заявки, а данные автоматически передаются в Make (Integromat) и Google Sheets.

---

## Функционал

- **Сбор заявок через Telegram** — пошаговая форма на основе FSM
- **Валидация данных** — проверка формата телефона и email на стороне бота
- **Сохранение в PostgreSQL** — асинхронная работа через SQLAlchemy 2.0
- **Уведомление администратора** — мгновенное сообщение при поступлении заявки
- **Управление статусами** — inline-кнопки в уведомлении: `Новая → В работе → Закрыта / Отклонена`
- **Уведомление пользователя** — при смене статуса пользователь получает сообщение в бот
- **Команда `/leads`** — просмотр заявок с пагинацией прямо в Telegram (только для админов)
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
    ├──► Уведомление администратору
    │         │
    │         └──► Смена статуса (inline-кнопки)
    │                   │
    │                   └──► Уведомление пользователю
    │
    └──► Webhook → Make (Integromat)
                        │
                        └──► Google Sheets
```

---

## Структура проекта

```
leadflow-bot/
│
├── bot/
│   ├── handlers/
│   │   ├── start.py          # /start, приветствие
│   │   ├── form.py           # FSM-форма сбора заявки
│   │   ├── admin.py          # /leads, смена статусов (только для админов)
│   │   └── common.py         # отмена, помощь
│   │
│   ├── keyboards/
│   │   ├── menu.py           # главное меню
│   │   ├── form_kb.py        # клавиатуры шагов формы
│   │   └── admin_kb.py       # статусы и пагинация для админа
│   │
│   ├── filters/
│   │   └── admin.py          # фильтр: проверка admin_ids
│   │
│   ├── services/
│   │   ├── lead_service.py           # создание, список, обновление статуса
│   │   ├── google_sheets_service.py  # запись в Google Sheets
│   │   ├── notify_service.py         # уведомления администратору
│   │   └── webhook_service.py        # отправка POST-запроса в Make
│   │
│   ├── integrations/
│   │   ├── google_sheets.py   # клиент Google Sheets API
│   │   └── webhook_sender.py  # HTTP-клиент (httpx)
│   │
│   ├── database/
│   │   ├── models.py     # SQLAlchemy-модели
│   │   ├── schemas.py    # Pydantic-схемы
│   │   ├── enums.py      # LeadStatus: new / in_progress / closed / rejected
│   │   ├── db_helper.py  # фабрика сессий
│   │   └── base.py       # базовый класс
│   │
│   ├── states/
│   │   └── lead_form.py  # состояния FSM
│   │
│   ├── utils/
│   │   └── validators.py # валидаторы телефона и email
│   │
│   └── config.py         # настройки (pydantic-settings)
│
├── migrations/            # Alembic-миграции
├── main.py
├── Dockerfile
├── docker-compose.yml
├── .env.template
├── pyproject.toml
└── README.md
```

---

## Переменные окружения

Скопируйте `.env.template` в `.env` и заполните значения:

```bash
cp .env.template .env
```

Ключевые переменные:

| Переменная | Описание |
|---|---|
| `APP_BOT__TOKEN` | Токен бота от @BotFather |
| `APP_BOT__ADMIN_IDS` | Список Telegram ID администраторов, например `[123456789]` |
| `APP_WEBHOOK__URL` | URL вебхука из Make |
| `APP_GOOGLE__SHEET_NAME` | Название листа в Google Sheets |
| `APP_DB__URL` | Строка подключения к PostgreSQL |

> ⚠️ Никогда не добавляйте `.env` и `credentials.json` в git. Убедитесь, что они указаны в `.gitignore`.

---

## Управление заявками (для администратора)

### Уведомление при поступлении заявки

При каждой новой заявке администратор получает сообщение:

```
📥 Новая заявка #42

👤 Имя: Иван Иванов
📞 Телефон: +79991234567
📧 Email: ivan@example.com
💬 Сообщение: Хочу узнать подробнее

📊 Статус: 🆕 Новая
🕐 Время: 15.03.2026 14:30
```

Под сообщением — inline-кнопки смены статуса. При нажатии:
- сообщение обновляется с новым статусом
- пользователь получает уведомление в бот

### Команда /leads

Просмотр последних заявок с пагинацией (5 штук на странице) — только для администраторов.

---

## Настройка webhook (Make / Integromat)

Webhook — это механизм, при котором бот сам инициирует HTTP-запрос на внешний URL сразу после сохранения заявки.

### Шаг 1. Создание сценария в Make

1. Зайдите в [make.com](https://make.com) и создайте новый сценарий
2. В качестве триггера выберите **Webhooks → Custom webhook**
3. Нажмите **Add → Save** — Make сгенерирует URL вида `https://hook.eu1.make.com/...`
4. Скопируйте URL в `.env` как `APP_WEBHOOK__URL`

### Шаг 2. Структура запроса

Бот отправляет POST-запрос с JSON:

```json
{
  "user_id": 123456789,
  "name": "Иван Иванов",
  "phone": "+79991234567",
  "email": "ivan@example.com",
  "message": "Хочу узнать подробнее",
  "created_at": "2026-03-15 14:30:00"
}
```

### Шаг 3. Подключение Google Sheets в Make

Добавьте следующий модуль в цепочку: **Google Sheets → Add a Row**. Сопоставьте поля из webhook с колонками таблицы и активируйте сценарий.

---

## Настройка Google Sheets API

1. Откройте [Google Cloud Console](https://console.cloud.google.com/)
2. Создайте проект и включите **Google Sheets API**
3. Создайте сервисный аккаунт, скачайте JSON-ключ и сохраните как `bot/google/creds.json`
4. Добавьте email сервисного аккаунта как редактора в вашу таблицу
5. Укажите название листа в `APP_GOOGLE__SHEET_NAME`

---

## Запуск

```bash
# 1. Клонируйте репозиторий
git clone https://github.com/NVLev/leadflow-bot.git
cd leadflow-bot

# 2. Создайте .env
cp .env.template .env
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

### Миграции

```bash
# Применить миграции
docker-compose exec app alembic upgrade head

# Создать новую миграцию после изменения моделей
docker-compose exec app alembic revision --autogenerate -m "описание"
```

---

## Стек технологий

| Компонент | Технология |
|-----------|------------|
| Язык | Python 3.11+ |
| Telegram | aiogram 3.x |
| База данных | PostgreSQL 16 + SQLAlchemy 2.0 (async) |
| Миграции | Alembic |
| Валидация / конфиг | Pydantic v2, pydantic-settings |
| HTTP-клиент | httpx (async) |
| Интеграции | Make (Integromat), Google Sheets API |
| Инфраструктура | Docker, Docker Compose |