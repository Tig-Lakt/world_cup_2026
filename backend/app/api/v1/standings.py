from fastapi import APIRouter, HTTPException

from ...repositories.standing import StandingRepository
from backend.app.core.dependencies import DbSession
from backend.app.presenters.standings import standing_to_dict

router = APIRouter()


@router.get("/standings")
def get_all_standings(db: DbSession):
    """Все турнирные таблицы, сгруппированные по группам."""
    repo = StandingRepository(db)
    grouped = repo.get_all_grouped()
    return [
        {"group": g["group"], "teams": [standing_to_dict(t) for t in g["teams"]]}
        for g in grouped
    ]


@router.get("/standings/{group_name}")
def get_group_standings(group_name: str, db: DbSession):
    """Турнирная таблица одной группы, например 'Группа A'."""
    repo = StandingRepository(db)
    teams = repo.get_by_group(group_name)
    if not teams:
        raise HTTPException(status_code=404, detail="Группа не найдена")
    return {"group": group_name, "teams": [standing_to_dict(t) for t in teams]}