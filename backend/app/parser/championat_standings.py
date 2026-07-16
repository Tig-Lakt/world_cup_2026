"""
backend/app/parser/championat_standings.py

Парсер турнирных таблиц ЧМ-2026 с championat.com. Страница /table/
содержит 12 таблиц подряд (одна на группу), каждая со своим заголовком
"Группа A".."Группа L" в .tournament-title внутри <thead>.

Структура строки команды (<tbody><tr>):
  td[0]            — позиция в группе
  td[1]            — название команды (внутри <a><span class="table-item__name">)
  td[2..N-8]       — переменное число колонок "очных встреч" с другими
                     командами группы (зависит от размера группы, для 4
                     команд — 3 колонки) — не нужны для таблицы, пропускаем
  td[-7]..td[-1]   — статистика, ВСЕГДА фиксированные 7 колонок в конце:
                     И, В, Н, П, Мячи ("3-0"), О, % очков
                     Это надёжнее, чем парсинг по фиксированному индексу
                     с начала строки, так как количество "очных встреч"
                     меняется с размером группы.
"""

import re
import logging
from typing import List, Dict, Optional

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class ChampionatStandingsParser:
    """Парсер турнирных таблиц ЧМ-2026 с championat.com."""

    TABLE_URL = "https://www.championat.com/football/_worldcup/tournament/6858/table/"

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "ru-RU,ru;q=0.9",
    }

    @classmethod
    def fetch_standings(cls) -> List[Dict]:
        """Загружает страницу таблиц и парсит все группы. Возвращает плоский список строк."""
        html = cls._fetch_html(cls.TABLE_URL)
        return cls.parse_standings(html)

    @staticmethod
    def parse_standings(html: str) -> List[Dict]:
        """
        Парсит HTML страницы /table/. Возвращает список словарей —
        одна запись на команду, с полем group_name у каждой.
        """
        soup = BeautifulSoup(html, "lxml")
        tables = soup.select("table.results-table")
        logger.info("🔗 Найдено таблиц групп: %d", len(tables))

        standings = []

        for table in tables:
            group_el = table.select_one(".tournament-title")
            group_name = group_el.get_text(strip=True) if group_el else None
            if not group_name:
                logger.warning("⚠️ Таблица без названия группы — пропущена")
                continue

            rows = table.select("tbody tr")
            for row in rows:
                entry = ChampionatStandingsParser._parse_row(row, group_name)
                if entry:
                    standings.append(entry)

            logger.info("✅ %s: %d команд", group_name, len(rows))

        return standings

    @staticmethod
    def _parse_row(row, group_name: str) -> Optional[Dict]:
        """Парсит одну строку таблицы (одну команду)."""
        # recursive=False — берём только прямых детей <tr>, не td, случайно
        # затянутые из вложенных структур (на этой странице их нет, но
        # это защищает от будущих изменений вёрстки).
        cells = row.find_all("td", recursive=False)

        # Минимум: позиция + команда + 7 колонок статистики = 9.
        if len(cells) < 9:
            logger.warning(
                "⚠️ Строка таблицы %s с недостаточным числом колонок (%d) — пропущена",
                group_name, len(cells),
            )
            return None

        position_text = cells[0].get_text(strip=True)
        if not position_text.isdigit():
            return None
        position = int(position_text)

        name_el = cells[1].select_one(".table-item__name")
        team_name = name_el.get_text(strip=True) if name_el else cells[1].get_text(strip=True)
        if not team_name:
            return None

        # Статистика — фиксированный хвост из 7 ячеек, независимо от
        # количества колонок "очных встреч" перед ними.
        stats_cells = cells[-7:]
        played = ChampionatStandingsParser._parse_int(stats_cells[0].get_text(strip=True))
        won = ChampionatStandingsParser._parse_int(stats_cells[1].get_text(strip=True))
        drawn = ChampionatStandingsParser._parse_int(stats_cells[2].get_text(strip=True))
        lost = ChampionatStandingsParser._parse_int(stats_cells[3].get_text(strip=True))
        goals_text = stats_cells[4].get_text(strip=True)
        points = ChampionatStandingsParser._parse_int(stats_cells[5].get_text(strip=True))
        points_pct = ChampionatStandingsParser._parse_float(stats_cells[6].get_text(strip=True))

        goals_for, goals_against = ChampionatStandingsParser._parse_goals(goals_text)

        return {
            "group_name": group_name,
            "position": position,
            "team_name": team_name,
            "played": played,
            "won": won,
            "drawn": drawn,
            "lost": lost,
            "goals_for": goals_for,
            "goals_against": goals_against,
            "points": points,
            "points_pct": points_pct,
        }

    # ------------------------------------------------------------------
    # Вспомогательные методы
    # ------------------------------------------------------------------

    @classmethod
    def _fetch_html(cls, url: str) -> str:
        """Загружает HTML по URL с браузерными заголовками (без них — 403)."""
        response = httpx.get(url, headers=cls.HEADERS, timeout=15, follow_redirects=True)
        response.raise_for_status()
        return response.text

    @staticmethod
    def _parse_int(text: str) -> int:
        """Парсит целое число из текста ячейки, 0 при неудаче."""
        try:
            return int(text)
        except ValueError:
            return 0

    @staticmethod
    def _parse_float(text: str) -> float:
        """Парсит дробное число из текста ячейки (например '16.7'), 0.0 при неудаче."""
        try:
            return float(text)
        except ValueError:
            return 0.0

    @staticmethod
    def _parse_goals(text: str) -> tuple[int, int]:
        """Парсит 'Мячи' вида '3-0' → (забито=3, пропущено=0)."""
        m = re.match(r"^(\d+)-(\d+)$", text)
        if m:
            return int(m.group(1)), int(m.group(2))
        return 0, 0