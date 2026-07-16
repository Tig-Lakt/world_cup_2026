#!/usr/bin/env python3
"""
scripts/update_standings.py

Standalone-скрипт для ежедневного обновления турнирных таблиц с
championat.com. Полностью пересчитывает таблицу standings (replace_all) —
не upsert, так как позиции команд могут поменяться местами между турами.

Использование вручную:
    python scripts/update_standings.py

Установка в crontab — см. подробные инструкции в update_results.py и
update_championat.py (та же логика с .env и cwd). Пример (сервер в UTC,
со сдвигом +10 минут относительно других cron-задач):
    10 9 * * * cd /path/to/world-cup-2026_serv && /path/to/venv/bin/python scripts/update_standings.py >> /var/log/wc2026_update_standings.log 2>&1

Код возврата: 0 — успех, 1 — ошибка.
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
logger = logging.getLogger("update_standings")


def main() -> int:
    from backend.app.core.database import SessionLocal
    from backend.app.services.championat_standings_sync import ChampionatStandingsSyncService

    db = SessionLocal()
    try:
        logger.info("🔄 Запуск ежедневного обновления турнирных таблиц...")
        service = ChampionatStandingsSyncService(db)
        count = service.sync_standings()
        logger.info("✅ Турнирные таблицы обновлены: %d команд", count)
        return 0
    except Exception:
        logger.exception("❌ Ошибка при обновлении турнирных таблиц")
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())