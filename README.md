# ⚽ World Cup 2026 Tracker

Проект доступен по адресу https://worldcup-2026.tech/

Демонстрационный full-stack проект для отслеживания чемпионата мира по футболу FIFA 2026.  
Разработан как портфолио-проект, демонстрирующий навыки backend Python-разработки.

---

## Стек технологий

| Слой | Технологии |
|---|---|
| Бэкенд | Python 3.10, FastAPI, Uvicorn |
| База данных | PostgreSQL 15, SQLAlchemy ORM |
| Векторная БД | Qdrant |
| AI | OpenAI API (GPT-4o-mini + text-embedding-3-small) |
| Парсинг | Playwright + Xvfb (Chrome), httpx, BeautifulSoup4 |
| Фронтенд | Jinja2, HTML5, CSS3, ванильный JS |
| Контейнеризация | Docker, Docker Compose |
| Веб-сервер | Nginx (reverse proxy) |

---

## Архитектура

```
world-cup-2026/
├── main.py                          # Точка входа FastAPI
├── docker-compose.yml               # PostgreSQL + Qdrant + Backend + Nginx
├── Dockerfile
├── .env                             # Переменные окружения
│
├── backend/
│   └── app/
│       ├── core/                    # Конфиг, БД, зависимости
│       ├── models/                  # SQLAlchemy ORM (Match, Team)
│       ├── schemas/                 # Pydantic схемы
│       ├── repositories/            # Слой доступа к данным
│       ├── services/                # Бизнес-логика, планировщик
│       ├── parser/                  # Playwright + httpx парсеры
│       ├── ai/                      # AI-агент, RAG, Qdrant
│       └── api/v1/                  # REST API роуты
│
├── scripts/                         # Скрипты обновления данных (cron)
│   ├── update_championat.py         # Обновление результатов матчей
│   ├── update_schedule.py           # Обновление расписания
│   └── update_standings.py          # Обновление турнирных таблиц
│
├── nginx/
│   ├── nginx.conf
│   └── default.conf
│
└── logs/                            # Логи cron-задач
```

---

## Страницы

| URL | Описание |
|---|---|
| `/` | Главная — презентация проекта |
| `/schedule?group=A` | Расписание с фильтром по группе |
| `/results` | Результаты завершённых матчей |
| `/standings` | Турнирные таблицы всех 12 групп |
| `/ai-chat` | Чат с AI-ассистентом |
| `/docs` | Swagger UI |

---

## API

| Метод | Путь | Описание |
|---|---|---|
| GET | `/api/v1/schedule` | Расписание (фильтры: `group`, `date_from`, `date_to`) |
| GET | `/api/v1/results` | Результаты (фильтр: `group`) |
| GET | `/api/v1/results/{id}` | Детали матча |
| GET | `/api/v1/standings` | Все группы |
| GET | `/api/v1/standings/{letter}` | Одна группа |
| POST | `/api/v1/ai/chat` | Вопрос AI-агенту `{"question": "..."}` |

---

## Быстрый старт

### 1. Клонировать репозиторий

```bash
git clone <repo-url>
cd world-cup-2026
```

### 2. Создать `.env`

```env
DATABASE_URL=postgresql://wc2026:wc2026pass@localhost:5432/worldcup2026
POSTGRES_USER=wc2026
POSTGRES_PASSWORD=wc2026pass
POSTGRES_DB=worldcup2026
POSTGRES_PORT=5432

FLASHSCORE_BASE_URL=https://www.flashscorekz.com
FLASHSCORE_REQUEST_DELAY=1.5
FLASHSCORE_MAX_RETRIES=3

QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION=wc2026_knowledge

OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

### 3. Поднять контейнеры

```bash
docker compose up -d --build
```

При первом запуске автоматически:
- Создаются таблицы БД
- Парсится расписание матчей с Flashscore
- Инициализируется коллекция Qdrant и загружаются факты

### 4. Открыть в браузере

```
http://localhost:8000
```

---

## Автоматическое обновление данных

Обновление данных выполняется через **cron-задачи**, которые запускают скрипты внутри Docker-контейнера.

### Настройка cron

Добавить в `crontab -e` на хосте:

```cron
# Обновление результатов матчей
30 * * * * docker exec -i wc2026_backend /usr/local/bin/python3 /app/scripts/update_championat.py >> /path/project/wc_2026_serv/logs/app0.log 2>&1 || echo "[ERROR] $(date) - exit code $?" >> /path/project/wc_2026_serv/scripts/logs/error0.log

# Обновление расписания
30 * * * * docker exec -i wc2026_backend /usr/local/bin/python3 /app/scripts/update_schedule.py >> /path/project/wc_2026_serv/logs/app1.log 2>&1 || echo "[ERROR] $(date) - exit code $?" >> /path/project/wc_2026_serv/scripts/logs/error1.log

# Обновление турнирных таблиц
30 * * * * docker exec -i wc2026_backend /usr/local/bin/python3 /app/scripts/update_standings.py >> /path/project/wc_2026_serv/logs/app2.log 2>&1 || echo "[ERROR] $(date) - exit code $?" >> /path/project/wc_2026_serv/scripts/logs/error2.log
```

Все три задачи запускаются раз в час, в 30 минут каждого часа.

### Логи

```bash
# Просмотр логов обновления результатов
tail -f /path/project/wc_2026_serv/logs/app0.log

# Просмотр ошибок
tail -f /path/project/wc_2026_serv/scripts/logs/error0.log
```

---

## Особенности реализации

- **Слоистая архитектура:** API → Services → Repositories → Models — чёткое разделение ответственности
- **Парсер:** Playwright + Xvfb для динамических JS-страниц Flashscore, httpx для статических
- **Upsert-логика:** матчи и команды создаются или обновляются по `flashscore_id` — без дублирования
- **RAG:** векторный поиск по Qdrant → формирование контекста → OpenAI → ответ пользователю
- **Lifespan FastAPI:** инициализация БД, парсинг расписания при первом старте и инициализация Qdrant — через `asynccontextmanager lifespan`
- **Относительные импорты** внутри пакета `backend/app/` — устойчивы к любому способу запуска

---

## Турнир

- 📅 Старт: 11 июня 2026
- 🏟️ 48 команд, 104 матча, 12 групп
- 🌎 США 🇺🇸 · Мексика 🇲🇽 · Канада 🇨🇦