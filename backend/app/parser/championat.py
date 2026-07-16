"""
backend/app/parser/championat.py

Парсер результатов ЧМ-2026 с championat.com. В отличие от Flashscore
(parser/flashscore_fifa.py, требует Playwright+Xvfb), эта страница отдаёт
статический HTML — подтверждено прямым curl-запросом, поэтому здесь
достаточно httpx + BeautifulSoup, без браузера.
"""

import re
import logging
from datetime import datetime
from typing import List, Dict, Optional

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class ChampionatParser:
    """Парсер календаря/результатов ЧМ-2026 с championat.com."""

    CALENDAR_URL = "https://www.championat.com/football/_worldcup/tournament/6858/calendar/"
    BASE_URL = "https://www.championat.com"

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "ru-RU,ru;q=0.9",
    }

    # ------------------------------------------------------------------
    # Результаты (календарь)
    # ------------------------------------------------------------------

    @classmethod
    def fetch_results(cls) -> List[Dict]:
        """
        Загружает страницу календаря и парсит все строки матчей.
        Возвращает только сыгранные матчи (со счётом) — строки с "- : -"
        пропускаются, так как это означает, что матч ещё не состоялся.
        """
        html = cls._fetch_html(cls.CALENDAR_URL)
        return cls.parse_results(html)

    @staticmethod
    def parse_results(html: str) -> List[Dict]:
        """Парсит HTML страницы календаря, возвращает список сыгранных матчей."""
        soup = BeautifulSoup(html, "lxml")
        rows = soup.select("tr.stat-results__row")
        logger.info("🔗 Найдено строк календаря: %d", len(rows))

        results = []
        skipped_unplayed = 0

        for row in rows:
            score_el = row.select_one(".stat-results__count-main")
            score_text = score_el.get_text(strip=True) if score_el else ""
            home_score, away_score = ChampionatParser._parse_score(score_text)

            # "- : -" означает, что матч ещё не сыграл — пропускаем,
            # как договорились: нет смысла хранить пустые результаты.
            if home_score is None or away_score is None:
                skipped_unplayed += 1
                continue

            link_el = row.select_one(".stat-results__link a")
            match_url = link_el.get("href", "") if link_el else ""
            championat_id = ChampionatParser._extract_match_id(match_url)
            if not championat_id:
                logger.warning("⚠️ Пропущена строка без ID матча: %s", match_url)
                continue

            teams = row.select(".stat-results__title-teams .table-item__name")
            home_team = teams[0].get_text(strip=True) if len(teams) >= 1 else ""
            away_team = teams[1].get_text(strip=True) if len(teams) >= 2 else ""
            if not home_team or not away_team:
                logger.warning("⚠️ Пропущена строка без названий команд: id=%s", championat_id)
                continue

            date_el = row.select_one(".stat-results__date-time")
            date_text = date_el.get_text(separator=" ", strip=True) if date_el else ""
            date_text = re.sub(r"\s+", " ", date_text).strip()
            match_date = ChampionatParser._parse_date(date_text)
            if not match_date:
                logger.warning(
                    "⚠️ Не удалось распознать дату %r для матча id=%s — пропущен",
                    date_text, championat_id,
                )
                continue

            group_el = row.select_one(".stat-results__group")
            group_name = group_el.get_text(strip=True) if group_el else None

            tour_el = row.select_one(".stat-results__tour-num")
            tour_text = tour_el.get_text(strip=True) if tour_el else ""
            tour_number = int(tour_text) if tour_text.isdigit() else None

            full_url = ChampionatParser._absolute_url(match_url)

            results.append({
                "championat_id": championat_id,
                "match_url": full_url,
                "home_team": home_team,
                "away_team": away_team,
                "home_score": home_score,
                "away_score": away_score,
                "match_date": match_date,
                "group_name": group_name,
                "tour_number": tour_number,
            })

        logger.info(
            "✅ Сыгранных матчей: %d, пропущено несыгранных: %d",
            len(results), skipped_unplayed,
        )
        return results

    # ------------------------------------------------------------------
    # Статистика одного матча
    # ------------------------------------------------------------------

    @classmethod
    def fetch_match_stats(cls, match_url: str) -> Dict:
        """Загружает страницу матча и парсит блок статистики (stat-graph)."""
        html = cls._fetch_html(match_url)
        return cls.parse_match_stats(html)

    @staticmethod
    def parse_match_stats(html: str) -> Dict:
        """
        Парсит блок .stat-graph на странице матча: пары значений
        "слева/справа" под общим заголовком в .stat-graph__title.
        Возвращает {"атаки": {"home": "69", "away": "119"}, ...}.
        """
        soup = BeautifulSoup(html, "lxml")
        stats = {}

        rows = soup.select(".stat-graph__row")
        for row in rows:
            title_el = row.select_one(".stat-graph__title")
            left_el = row.select_one(".stat-graph__value._left strong")
            right_el = row.select_one(".stat-graph__value._right strong")

            if not (title_el and left_el and right_el):
                continue

            key = (
                title_el.get_text(strip=True)
                .lower()
                .replace(" ", "_")
                .replace("%", "pct")
                .replace("/", "_")
            )
            stats[key] = {
                "home": left_el.get_text(strip=True),
                "away": right_el.get_text(strip=True),
            }

        return stats

    # ------------------------------------------------------------------
    # Вспомогательные методы
    # ------------------------------------------------------------------

    @classmethod
    def _fetch_html(cls, url: str) -> str:
        """Загружает HTML по URL с браузерными заголовками (без них — 403)."""
        response = httpx.get(url, headers=cls.HEADERS, timeout=15, follow_redirects=True)
        response.raise_for_status()
        return response.text

    @classmethod
    def _absolute_url(cls, path: str) -> str:
        """Достраивает относительный путь до полного URL championat.com."""
        if path.startswith("http"):
            return path
        return cls.BASE_URL + path

    @staticmethod
    def _extract_match_id(url: str) -> Optional[str]:
        """Извлекает числовой ID матча из URL вида .../match/1310352/."""
        m = re.search(r"/match/(\d+)/?", url)
        return m.group(1) if m else None

    @staticmethod
    def _parse_score(score_text: str) -> tuple[Optional[int], Optional[int]]:
        """Парсит '1 : 1' → (1, 1). '- : -' (несыгранный матч) → (None, None)."""
        m = re.match(r"^(\d+)\s*:\s*(\d+)$", score_text)
        if m:
            return int(m.group(1)), int(m.group(2))
        return None, None

    @staticmethod
    def _parse_date(date_text: str) -> Optional[datetime]:
        """Парсит '18.06.2026 19:00' → datetime. championat.com всегда отдаёт год."""
        try:
            return datetime.strptime(date_text, "%d.%m.%Y %H:%M")
        except ValueError:
            return None