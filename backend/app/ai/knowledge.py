"""
backend/app/ai/knowledge.py

Сборщик фактов для RAG-агента AI-чата. Собирает два типа фактов:
  - статичные: формат турнира, состав групп (фиксированы, см.
    core/team_groups.py) — не меняются в течение турнира;
  - динамические: результаты сыгранных матчей (match_results,
    championat.com), текущее турнирное положение (standings,
    championat.com), ближайшие предстоящие матчи (matches, Flashscore).

Каждый факт — отдельная короткая текстовая строка на русском, пригодная
для прямой вставки в промпт после векторного поиска в Qdrant.
"""

from datetime import datetime
from typing import List

from sqlalchemy.orm import Session
from sqlalchemy import and_

from ..core.team_groups import GROUPS
from ..models.match import Match, MatchStatus
from ..models.match_result import MatchResult
from ..models.standing import Standing


def build_static_facts() -> List[str]:
    """
    Статичные факты о турнире: формат, состав групп. Не зависят от БД —
    фиксированы на весь турнир (жребий проведён заранее).
    """
    facts = [
        "Чемпионат мира по футболу 2026 года (ЧМ-2026) проходит в США, "
        "Канаде и Мексике — это первый турнир с 48 командами-участницами.",
        "На групповом этапе ЧМ-2026 48 команд разделены на 12 групп "
        "по 4 команды (группы A-L). Каждая команда играет 3 матча "
        "в группе по круговой системе.",
        "По итогам группового этапа в плей-офф выходят команды, "
        "занявшие 1-е и 2-е места в группе, а также 8 лучших команд, "
        "занявших 3-е место среди всех 12 групп.",
    ]

    for letter, teams in GROUPS.items():
        teams_text = ", ".join(teams)
        facts.append(f"Группа {letter} ЧМ-2026: {teams_text}.")

    return facts


def build_dynamic_facts(db: Session) -> List[str]:
    """
    Динамические факты, собранные из текущего состояния БД: результаты
    сыгранных матчей, турнирное положение по группам, ближайшие
    предстоящие матчи расписания.
    """
    facts: List[str] = []
    facts.extend(_build_result_facts(db))
    facts.extend(_build_standings_facts(db))
    facts.extend(_build_upcoming_facts(db))
    return facts


def _build_result_facts(db: Session) -> List[str]:
    """Факт на каждый сыгранный матч из match_results (championat.com)."""
    results = (
        db.query(MatchResult)
        .order_by(MatchResult.match_date)
        .all()
    )

    facts = []
    for r in results:
        date_text = r.match_date.strftime("%d.%m.%Y") if r.match_date else "дата неизвестна"
        group_text = f" ({r.group_name})" if r.group_name else ""
        facts.append(
            f"Результат матча{group_text}: {r.home_team} {r.home_score}:{r.away_score} "
            f"{r.away_team}, сыграно {date_text}."
        )
    return facts


def _build_standings_facts(db: Session) -> List[str]:
    """
    Факт на каждую группу: полное турнирное положение в виде одной
    строки (компактнее, чем по факту на команду — экономит количество
    точек в Qdrant и сохраняет связность таблицы при поиске).
    """
    standings = (
        db.query(Standing)
        .order_by(Standing.group_name, Standing.position)
        .all()
    )

    grouped: dict[str, list[Standing]] = {}
    for s in standings:
        grouped.setdefault(s.group_name, []).append(s)

    facts = []
    for group_name, teams in grouped.items():
        rows = "; ".join(
            f"{t.position}. {t.team_name} — {t.points} очков "
            f"({t.won}В {t.drawn}Н {t.lost}П, мячи {t.goals_for}-{t.goals_against})"
            for t in teams
        )
        facts.append(f"Турнирное положение {group_name}: {rows}.")
    return facts


def _build_upcoming_facts(db: Session, limit: int = 60) -> List[str]:
    """
    Факт на каждый предстоящий матч расписания (matches, Flashscore),
    дата которых ещё не наступила. Ограничено limit — на случай, если
    расписание содержит много будущих матчей далеко вперёд, не нужно
    раздувать коллекцию фактами, которые скоро устареют без обновления.
    """
    from ..repositories.team import TeamRepository

    now = datetime.now()
    team_repo = TeamRepository(db)

    matches = (
        db.query(Match)
        .filter(
            and_(
                Match.status == MatchStatus.SCHEDULED,
                Match.match_date.isnot(None),
                Match.match_date >= now,
            )
        )
        .order_by(Match.match_date)
        .limit(limit)
        .all()
    )

    facts = []
    for m in matches:
        # Match не имеет SQLAlchemy relationship на Team (только
        # ForeignKey на home_team_id/away_team_id) — команды подгружаем
        # отдельным запросом через TeamRepository, как и main.py делает
        # в _build_match_dict.
        home_team = team_repo.get_by_id(m.home_team_id)
        away_team = team_repo.get_by_id(m.away_team_id)
        if not (home_team and away_team):
            continue

        date_text = m.match_date.strftime("%d.%m.%Y %H:%M")
        group_text = f" (группа {m.group_letter})" if m.group_letter else ""
        facts.append(
            f"Предстоящий матч{group_text}: {home_team.name} — "
            f"{away_team.name}, {date_text}."
        )
    return facts