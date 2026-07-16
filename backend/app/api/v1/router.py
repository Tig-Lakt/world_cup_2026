from fastapi import APIRouter
from .results import router as results_router
from .championat_results import router as championat_results_router
from .standings import router as standings_router
from .ai_chat import router as ai_chat_router


router = APIRouter(prefix="/api/v1")

router.include_router(results_router, tags=["results"])
router.include_router(championat_results_router, tags=["championat-results"])
router.include_router(standings_router, tags=["standings"])
router.include_router(ai_chat_router, tags=["ai-chat"])