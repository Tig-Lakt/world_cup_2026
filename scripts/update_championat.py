#!/usr/bin/env python3
"""
scripts/update_championat.py

Standalone-скрипт для ежедневного обновления результатов и статистики
championat.com. Аналог scripts/update_results.py (Flashscore), но не
требует браузера — championat.com отдаёт статический HTML, парсинг идёт
через httpx + BeautifulSoup.

Использование вручную:
    python scripts/update_championat.py

Установка в crontab (запуск каждый день в 12:00 МСК, вместе с обновлением
результатов Flashscore — можно ставить на то же время или со сдвигом
в несколько минут, чтобы не нагружать сеть одновременно):
    1. Узнать часовой пояс сервера: timedatectl
       Сервер в UTC → 12:00 МСК = 09:00 UTC. Сервер в Europe/Moscow → 12:00.
    2. crontab -e
    3. Добавить строку (вариант для сервера в UTC, со сдвигом +5 минут
       относительно update_results.py, чтобы не дублировать сетевую
       нагрузку в одну секунду):
       5 9 * * * cd /path/to/world-cup-2026_serv && /path/to/venv/bin/python scripts/update_championat.py >> /var/log/wc2026_update_championat.log 2>&1
       Вариант для сервера в Europe/Moscow:
       5 12 * * * cd /path/to/world-cup-2026_serv && /path/to/venv/bin/python scripts/update_championat.py >> /var/log/wc2026_update_championat.log 2>&1

    ВАЖНО про `cd /path/to/world-cup-2026_serv &&`: см. комментарий в
    update_results.py — без него скрипт не найдёт .env.

Код возврата: 0 — успех (даже если обновлять было нечего), 1 — ошибка.
"""

import sys
import os
import logging

# Корень проекта в sys.path, импорт через backend.app.... — см. подробное
# объяснение в update_results.py: иначе создаётся второй экземпляр Base.
PROJECT_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, PROJECT_ROOT)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("update_championat")


def main() -> int:
    from backend.app.core.database import SessionLocal
    from backend.app.services.championat_sync import ChampionatSyncService

    db = SessionLocal()
    try:
        logger.info("🔄 Запуск ежедневного обновления championat.com...")
        service = ChampionatSyncService(db)

        synced = service.sync_results()
        logger.info("✅ Результаты синхронизированы: %d", synced)

        updated_stats = service.sync_all_missing_stats()
        logger.info("✅ Статистика обновлена для %d матчей", updated_stats)

        return 0
    except Exception:
        logger.exception("❌ Ошибка при обновлении championat.com")
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())