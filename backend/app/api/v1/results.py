from fastapi import APIRouter

from ...repositories.match import MatchRepository
from ...repositories.team import TeamRepository
from backend.app.core.dependencies import DbSession
from backend.app.presenters.results import match_to_dict


router = APIRouter()


@router.get("/results")
def get_results(db: DbSession, group: str | None = None):
    """Список завершённых матчей, опционально по группе."""
    match_repo = MatchRepository(db)
    team_repo = TeamRepository(db)

    matches = match_repo.get_finished_matches()
    if group:
        matches = [m for m in matches if m.group_letter == group.upper()]

    return [
        match_to_dict(m, team_repo.get_by_id(m.home_team_id), team_repo.get_by_id(m.away_team_id))
        for m in matches
    ]