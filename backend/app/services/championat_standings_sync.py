import logging

from sqlalchemy.orm import Session

from ..parser.championat_standings import ChampionatStandingsParser
from ..repositories.standing import StandingRepository

logger = logging.getLogger(__name__)


class ChampionatStandingsSyncService:
    """
    Синхронизация турнирных таблиц ЧМ-2026 с championat.com в таблицу
    standings. Отдельный сервис от ChampionatSyncService (результаты) —
    логика принципиально другая: полная замена снимка таблицы при каждом
    обновлении (replace_all), а не построчный upsert.
    """

    def __init__(self, db: Session):
        self.db = db
        self.standing_repo = StandingRepository(db)

    def sync_standings(self) -> int:
        """
        Загружает все 12 групповых таблиц и полностью заменяет таблицу
        standings новым снимком. Возвращает количество строк (команд).
        """
        entries = ChampionatStandingsParser.fetch_standings()
        count = self.standing_repo.replace_all(entries)
        self.db.commit()
        logger.info("✅ Турнирные таблицы обновлены: %d команд", count)
        return count