# Деплой Workora на Amvera

## Переменные окружения (панель Amvera)

```
BOT_TOKEN=...
ADMIN_IDS=1494088727
CHANNEL_ID=@Workora_student
CHANNEL_URL=https://t.me/Workora_student
DATABASE_URL=sqlite+aiosqlite:////data/workora.db
LOG_LEVEL=INFO
REMINDER_HOURS=2
FOLLOWUP_MINUTES=30
```

Файл `.env` в репозиторий **не добавлять**.

## Файлы

- `amvera.yml` — конфигурация Amvera
- `main.py` — точка входа
- `assets/` — фото вакансий (в Git)
- База SQLite — только в `/data/workora.db` (постоянное хранилище)

## Запуск

Amvera выполнит: `python3 main.py` (scriptName: main.py)

## Локально

```powershell
copy .env.example .env
py main.py
```

Локально `DATABASE_URL=sqlite+aiosqlite:///./data/workora.db`
