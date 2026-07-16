#!/usr/bin/env python3
"""
scripts/update_schedule.py

Standalone-скрипт для периодического обновления расписания с Flashscore.

Полностью пересинхронизирует таблицу matches: парсит /fixtures/ заново,
и ТОЛЬКО при успешном непустом результате очищает старые записи и
вставляет новые (см. SyncService.replace_fixtures). Если парсинг
не удался (сеть, изменилась вёрстка сайта) — существующие данные в БД
не трогаются, скрипт завершается с кодом ошибки.

В отличие от lifespan-логики в main.py (_sync_fixtures_if_empty — парсит
расписание только если таблица matches пуста, один раз при первом
старте), этот скрипт предназначен для регулярного запуска по cron, чтобы
подхватывать переносы матчей и матчи, исчезнувшие со страницы Flashscore.

Использование вручную:
    python scripts/update_schedule.py

Установка в crontab — расписание ЧМ-2026 меняется редко (переносы
матчей — исключение, не норма), поэтому крутить чаще раза в день не
нужно. Пример (сервер в UTC, можно ставить на любое удобное время,
не обязательно совпадающее с обновлением результатов/таблиц):
    15 9 * * * cd /path/to/world-cup-2026_serv && /path/to/venv/bin/python scripts/update_schedule.py >> /var/log/wc2026_update_schedule.log 2>&1

См. подробные инструкции про .env и cwd в update_results.py — та же
логика применима здесь.

Использует Playwright (тот же Browser, что и для результатов Flashscore),
поэтому медленнее, чем championat-скрипты — это нормально для расписания,
оно не нужно обновлять часто.

Код возврата: 0 — успех, 1 — ошибка (в том числе если парсинг вернул
пустой список — таблица matches в этом случае НЕ тронута).
"""

import sys
import os
import logging

PROJECT_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, PROJECT_ROOT)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("update_schedule")


def main() -> int:
    from backend.app.core.database import SessionLocal
    from backend.app.services.sync import SyncService

    db = SessionLocal()
    try:
        logger.info("🔄 Запуск периодического обновления расписания...")
        service = SyncService(db)
        synced = service.replace_fixtures()
        logger.info("✅ Расписание пересинхронизировано, матчей: %d", synced)
        return 0
    except Exception:
        logger.exception("❌ Ошибка при обновлении расписания — таблица matches не изменена")
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())