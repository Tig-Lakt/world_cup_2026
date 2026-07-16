# backend/app/presenters/match.py
# ---------------------------------------------------------------------------
# Хелпер сборки данных матча
# ---------------------------------------------------------------------------


from backend.app.core.constants import STATUS_RU

def build_match_dict(m, home_team, away_team) -> dict:
    raw_status = m.status.value if m.status else "scheduled"
    return {
        "id":           m.id,
        "home_team":    home_team.name if home_team else str(m.home_team_id),
        "away_team":    away_team.name if away_team else str(m.away_team_id),
        "home_score":   m.home_score,
        "away_score":   m.away_score,
        "status":       raw_status,
        "status_ru":    STATUS_RU.get(raw_status, "Запланирован"),
        "match_date":   m.match_date,
        "group_letter": m.group_letter,
    }