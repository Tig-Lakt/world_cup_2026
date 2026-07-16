import sys
import os
import logging
from contextlib import asynccontextmanager
import asyncio

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend"))

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend.app.core.config import get_settings
from backend.app.core.database import init_db
from backend.app.api.v1.router import router as api_v1_router
from backend.app.api.v1.pages import router as pages_router

from backend.app.core.startup import (
    sync_fixtures_if_empty,
    sync_championat_results_if_empty,
    sync_championat_stats,
    sync_standings,
    init_qdrant
)

# ---------------------------------------------------------------------------
# Логгер
# ---------------------------------------------------------------------------

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Настройки
# ---------------------------------------------------------------------------

settings = get_settings()

# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Создаём таблицы БД, если их нет
    init_db()

    # 2. Первичный парсинг расписания — только если матчей ещё нет в БД.
    #    asyncio.to_thread — потому что sync_fixtures использует синхронный
    #    Playwright, который нельзя вызывать напрямую внутри async lifespan.
    await asyncio.to_thread(sync_fixtures_if_empty)

    # 3. Первичная синхронизация результатов с championat.com — только
    #    если таблица результатов пуста. championat.com не требует
    #    браузера (httpx), но всё равно оборачиваем в to_thread, чтобы
    #    синхронный сетевой вызов не блокировал event loop при старте.
    await asyncio.to_thread(sync_championat_results_if_empty)

    # 4. Догрузка статистики championat.com для уже сыгранных матчей,
    #    у которых её ещё нет. В отличие от шага 3, выполняется при
    #    КАЖДОМ старте, а не только при пустой таблице — после шага 3
    #    могли появиться новые результаты без статистики.
    await asyncio.to_thread(sync_championat_stats)

    # 5. Синхронизация турнирных таблиц с championat.com — ВСЕГДА при
    #    старте (не только при пустой таблице): положение команд должно
    #    отражать актуальный пересчёт championat.com после каждого тура,
    #    а не оставаться "снимком" с момента первого запуска.
    await asyncio.to_thread(sync_standings)

    # 6. Инициализация Qdrant для AI-чата: коллекция пересоздаётся и все
    #    факты (статичные + динамические из БД) загружаются заново при
    #    КАЖДОМ старте — договорились, что это проще, чем инкрементальная
    #    синхронизация фактов в векторном хранилище.
    await asyncio.to_thread(init_qdrant)

    yield  # приложение работает

# ---------------------------------------------------------------------------
# Приложение
# ---------------------------------------------------------------------------

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)
app.mount("/static", StaticFiles(directory="backend/static"), name="static")
app.include_router(api_v1_router)
app.include_router(pages_router)

# ---------------------------------------------------------------------------
# Точка входа
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
