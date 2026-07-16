from fastapi import APIRouter, HTTPException

from ...repositories.match_result import MatchResultRepository
from backend.app.core.dependencies import DbSession
from backend.app.presenters.championat_results import result_to_dict


router = APIRouter()


@router.get("/championat-results")
def get_championat_results(db: DbSession, group: str | None = None):
    """Результаты ЧМ-2026 с championat.com, в хронологическом порядке."""
    repo = MatchResultRepository(db)
    results = repo.get_all(group_name=group)
    return [result_to_dict(r) for r in results]


@router.get("/championat-results/{result_id}")
def get_championat_result_detail(result_id: int, db: DbSession):
    """Детали одного результата — используется модалкой в results.html."""
    repo = MatchResultRepository(db)
    result = repo.get_by_id(result_id)
    if not result:
        raise HTTPException(status_code=404, detail="Результат не найден")
    return result_to_dict(result)