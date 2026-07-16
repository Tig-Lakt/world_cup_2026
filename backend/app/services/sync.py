import logging
import re
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from ..parser.browser import Browser
from ..parser.flashscore_fifa import FIFAWorldCupParser
from ..repositories.match import MatchRepository
from ..repositories.team import TeamRepository
from ..models.match import Match, MatchStatus
from ..core.team_groups import get_group_letter

logger = logging.getLogger(__name__)

# Год турнира фиксирован — Flashscore в большинстве форматов дат его не отдаёт.
TOURNAMENT_YEAR = 2026


class SyncService:
    """Сервис синхронизации с Flashscore в БД: расписание (этап 1), результаты и статистика (этап 2)."""

    def __init__(self, db: Session):
        self.db = db
        self.match_repo = MatchRepository(db)
        self.team_repo = TeamRepository(db)
        self.parser = FIFAWorldCupParser()

    # ------------------------------------------------------------------
    # Расписание
    # ------------------------------------------------------------------

    def sync_fixtures(self, headless: bool = True) -> int:
        """
        Разовая синхронизация расписания матчей (используется при первом
        старте приложения, см. main.py: _sync_fixtures_if_empty).
        Запускает браузер, парсит фикстуры и сохраняет через upsert по
        flashscore_id — не очищает таблицу, безопасно вызывать повторно.
        Возвращает количество синхронизированных матчей.
        """
        browser = Browser(headless=headless)
        synced = 0

        try:
            page = browser.start()
            matches_data = self.parser.parse_fixtures_with_browser(page)

            for match_data in matches_data:
                try:
                    self._upsert_match(match_data)
                    synced += 1
                except Exception as e:
                    logger.warning(
                        "⚠️ Ошибка сохранения матча %s: %s",
                        match_data.get("flashscore_id"), e,
                    )

            self.db.commit()
            logger.info("✅ Синхронизировано матчей: %d", synced)

        finally:
            browser.stop()

        return synced

    def replace_fixtures(self, headless: bool = True) -> int:
        """
        Полная пересинхронизация расписания для периодического
        cron-обновления (см. scripts/update_schedule.py).

        В отличие от sync_fixtures (upsert по flashscore_id, используется
        при первом старте), здесь таблица matches очищается перед
        вставкой — это нужно, чтобы матчи, исчезнувшие со страницы
        Flashscore /fixtures/ (например, перенесённые далеко вперёд так,
        что выпали из выдачи), не оставались в БД устаревшими записями.

        ВАЖНО: очистка происходит ТОЛЬКО если парсинг прошёл успешно и
        вернул непустой список матчей. Если Flashscore недоступен, или
        вёрстка страницы изменилась и парсер вернул пустой список —
        существующие данные в БД не трогаются, метод поднимает
        исключение, чтобы вызывающий код (cron-скрипт) узнал о сбое и
        не подумал, что обновление прошло успешно с 0 матчей.
        """
        browser = Browser(headless=headless)

        try:
            page = browser.start()
            matches_data = self.parser.parse_fixtures_with_browser(page)
        finally:
            browser.stop()

        if not matches_data:
            raise RuntimeError(
                "Парсинг расписания вернул пустой список — таблица matches "
                "НЕ очищена, чтобы не потерять существующие данные при сбое "
                "парсера (изменилась вёрстка Flashscore, сайт недоступен и т.п.)"
            )

        # Парсинг успешен и непуст — теперь безопасно очистить и вставить.
        deleted = self.db.query(Match).delete()
        self.db.flush()
        logger.info("🗑️ Удалено старых записей расписания: %d", deleted)

        synced = 0
        for match_data in matches_data:
            try:
                self._upsert_match(match_data)
                synced += 1
            except Exception as e:
                logger.warning(
                    "⚠️ Ошибка сохранения матча %s: %s",
                    match_data.get("flashscore_id"), e,
                )

        self.db.commit()
        logger.info("✅ Расписание пересинхронизировано: %d матчей", synced)
        return synced

    # ------------------------------------------------------------------
    # Приватные методы
    # ------------------------------------------------------------------

    def _upsert_match(self, match_data: dict) -> None:
        """Создать или обновить матч и связанные команды."""
        home_name = match_data.get("home_team", "")
        away_name = match_data.get("away_team", "")

        if not home_name or not away_name:
            return

        if not match_data.get("flashscore_id"):
            # Без id матч не на что upsert-ить — пропускаем, иначе
            # MatchRepository.upsert создаст дубликат с пустым flashscore_id.
            logger.warning(
                "⚠️ Пропущен матч без flashscore_id: %s vs %s", home_name, away_name
            )
            return

        home_team = self.team_repo.get_or_create(name=home_name)
        away_team = self.team_repo.get_or_create(name=away_name)

        match_date = self._parse_time(match_data.get("time_display", ""))

        status_str = match_data.get("status", "scheduled")
        try:
            status = MatchStatus(status_str)
        except ValueError:
            status = MatchStatus.SCHEDULED

        group_letter = get_group_letter(home_name) or get_group_letter(away_name)
        if not group_letter:
            logger.warning(
                "⚠️ group_letter не определён для команд: %s / %s — "
                "проверьте написание в team_groups.py",
                home_name, away_name,
            )

        data: dict = {
            "home_team_id": home_team.id,
            "away_team_id": away_team.id,
            "match_date": match_date,
            "status": status,
            "match_url": match_data.get("match_url", ""),
            "group_letter": group_letter,
        }

        if "home_score" in match_data:
            data["home_score"] = match_data["home_score"]
        if "away_score" in match_data:
            data["away_score"] = match_data["away_score"]

        self.match_repo.upsert(match_data["flashscore_id"], data)

    def _parse_time(self, time_str: str) -> Optional[datetime]:
        """
        Преобразует время матча с Flashscore в datetime.

        Flashscore в фикстурах отдаёт время в нескольких форматах в одном
        и том же столбце .event__time, в зависимости от того, насколько
        матч близко к "сегодня":
          - "20.06."        — только дата, время неизвестно (далёкий матч)
          - "20.06. 22:00"   — дата и время (обычный случай)
          - "22:00"          — только время, если матч сегодня
          - "Не начался" / "Отложен" и т.п. — не дата вообще

        Год не передаётся никогда — фиксируем TOURNAMENT_YEAR.
        """
        if not time_str:
            return None

        text = time_str.strip()

        # "20.06. 22:00" или "20.06 22:00"
        m = re.match(r"^(\d{1,2})\.(\d{1,2})\.?\s+(\d{1,2}):(\d{2})$", text)
        if m:
            day, month, hour, minute = map(int, m.groups())
            try:
                return datetime(TOURNAMENT_YEAR, month, day, hour, minute)
            except ValueError:
                return None

        # "20.06." или "20.06" — только дата, время неизвестно, ставим 00:00
        m = re.match(r"^(\d{1,2})\.(\d{1,2})\.?$", text)
        if m:
            day, month = map(int, m.groups())
            try:
                return datetime(TOURNAMENT_YEAR, month, day, 0, 0)
            except ValueError:
                return None

        # "22:00" — только время, значит матч сегодня
        m = re.match(r"^(\d{1,2}):(\d{2})$", text)
        if m:
            hour, minute = map(int, m.groups())
            today = datetime.now()
            return today.replace(hour=hour, minute=minute, second=0, microsecond=0)

        # Текстовые статусы вида "Не начался" — это не дата
        logger.debug("⚠️ Нераспознанный формат времени Flashscore: %r", text)
        return None
