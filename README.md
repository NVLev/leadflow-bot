
## 🏗️  Структура проекта
```bash
leadflow-bot
│
├── bot
│   │
│   ├── handlers
│   │   ├── start.py
│   │   ├── form.py
│   │   └── admin.py
│   │
│   ├── keyboards
│   │   ├── menu.py
│   │   └── form_kb.py
│   │
│   ├── services
│   │   ├── lead_service.py
│   │   └── notification_service.py
│   │
│   ├── integrations
│   │   ├── google_sheets.py
│   │   └── webhook_sender.py
│   │
│   ├── database
│   │   ├── models.py
│   │   ├── db_helper.py
│   │   └── base.py
│   │
│   ├── states
│   │   └── lead_form.py
│   │
│   └── config.py
│
├── migrations
│
├── main.py
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── README.md
```