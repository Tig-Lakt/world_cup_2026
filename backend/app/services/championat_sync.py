import logging

from sqlalchemy.orm import Session

from ..parser.championat import ChampionatParser
from ..repositories.match_result import MatchResultRepository

logger = logging.getLogger(__name__)


class ChampionatSyncService:
    """
    Синхронизация результатов ЧМ-2026 с championat.com в таблицу
    match_results. Отдельный сервис от SyncService (Flashscore) — другой
    источник, другая технология получения HTML (httpx, без браузера).
    """

    def __init__(self, db: Session):
        self.db = db
        self.result_repo = MatchResultRepository(db)

    def sync_results(self) -> int:
        """
        Загружает календарь, сохраняет все сыгранные матчи (с счётом).
        Возвращает количество синхронизированных записей.
        """
        results_data = ChampionatParser.fetch_results()
        synced = 0

        for data in results_data:
            try:
                championat_id = data.pop("championat_id")
                self.result_repo.upsert(championat_id, data)
                synced += 1
            except Exception as e:
                logger.warning("⚠️ Ошибка сохранения результата: %s", e)

        self.db.commit()
        logger.info("✅ Синхронизировано результатов championat.com: %d", synced)
        return synced

    def sync_stats_for_match(self, result_id: int, match_url: str) -> bool:
        """
        Загружает и сохраняет статистику для одного матча по его странице.
        Возвращает True, если статистика найдена и сохранена.
        """
        stats = ChampionatParser.fetch_match_stats(match_url)
        if not stats:
            logger.warning("⚠️ Статистика не найдена: %s", match_url)
            return False

        self.result_repo.update_stats(result_id, stats)
        self.db.commit()
        return True

    def sync_all_missing_stats(self) -> int:
        """
        Проходит по всем результатам без статистики и догружает её.
        Возвращает количество обновлённых записей.
        """
        results = self.result_repo.get_all()
        updated = 0

        for result in results:
            if result.stats:
                continue
            if not result.match_url:
                continue
            try:
                if self.sync_stats_for_match(result.id, result.match_url):
                    updated += 1
            except Exception as e:
                logger.error(
                    "❌ Ошибка загрузки статистики для %s: %s",
                    result.championat_id, e,
                )

        logger.info("✅ Обновлена статистика для %d матчей", updated)
        return updated