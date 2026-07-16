from backend.app.core.constants import STATUS_RU


def build_results_list(results) -> list[dict]:
    return [
        {
            "id":           r.id,
            "home_team":    r.home_team,
            "away_team":    r.away_team,
            "home_score":   r.home_score,
            "away_score":   r.away_score,
            "status":       "finished",
            "status_ru":    STATUS_RU["finished"],
            "match_date":   r.match_date,
            "group_letter": (r.group_name or "").replace("Группа ", "").strip() or None,
        }
        for r in results
    ]


def match_to_dict(m, home_team, away_team) -> dict:
    """Формирует словарь матча с полным набором полей для модалки результатов."""
    return {
        "id":           m.id,
        "home_team":    home_team.name if home_team else str(m.home_team_id),
        "away_team":    away_team.name if away_team else str(m.away_team_id),
        "home_score":   m.home_score,
        "away_score":   m.away_score,
        "status":       m.status.value if m.status else "scheduled",
        "match_date":   m.match_date.isoformat() if m.match_date else None,
        "group_letter": m.group_letter,
        "venue":        m.venue,
        "city":         m.city,
        "stats":        m.stats,
    }