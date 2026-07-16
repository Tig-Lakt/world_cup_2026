from typing import Annotated

from fastapi import APIRouter, Query, Request
from fastapi.templating import Jinja2Templates

from backend.app.repositories.match import MatchRepository
from backend.app.repositories.team import TeamRepository
from backend.app.repositories.match_result import MatchResultRepository
from backend.app.repositories.standing import StandingRepository
from backend.app.core.constants import GROUPS
from backend.app.presenters.match import build_match_dict  # переименуйте
from backend.app.presenters.results import build_results_list
from backend.app.presenters.standings import build_standings_list
from backend.app.core.dependencies import DbSession


router = APIRouter()
templates = Jinja2Templates(directory="backend/templates")   # можно оставить, если устраивает глобальная переменная


@router.get("/")
def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/schedule")
def schedule_page(
    request: Request,
    db: DbSession,
    group: Annotated[str | None, Query(min_length=1, max_length=1)] = None,
):
    match_repo = MatchRepository(db)
    team_repo = TeamRepository(db)

    matches = match_repo.get_matches(group=group)
    remaining = match_repo.count_remaining(group=group)

    result = [
        build_match_dict(m, team_repo.get_by_id(m.home_team_id), team_repo.get_by_id(m.away_team_id))
        for m in matches
    ]

    return templates.TemplateResponse("schedule.html", {
        "request":       request,
        "matches":       result,
        "total":         len(result),
        "remaining":     remaining,
        "groups":        GROUPS,
        "current_group": group,
    })


@router.get("/results")
def results_page(
    request: Request, 
    db: DbSession
):
    result_repo = MatchResultRepository(db)
    results = result_repo.get_all()

    return templates.TemplateResponse("results.html", {
        "request": request,
        "matches": build_results_list(results),
        "total":   len(results),
    })


@router.get("/standings")
def standings_page(
    request: Request, 
    db: DbSession
):
    standing_repo = StandingRepository(db)
    grouped = standing_repo.get_all_grouped()
    return templates.TemplateResponse("standings.html", {
        "request": request,
        "standings": build_standings_list(grouped),
    })


@router.get("/ai-chat")
def ai_chat_page(
    request: Request
):
    return templates.TemplateResponse("ai-chat.html", {"request": request})