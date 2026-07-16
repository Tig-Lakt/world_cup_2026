from fastapi import APIRouter, Depends
from pydantic import BaseModel

from backend.app.ai.agent import AIAgent
from backend.app.core.dependencies import get_ai_agent


router = APIRouter()


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str


@router.post("/ai/chat", response_model=ChatResponse)
def ai_chat(request: ChatRequest, agent: AIAgent = Depends(get_ai_agent)):
    """Отвечает на вопрос пользователя о ЧМ-2026 через RAG-агента."""
    answer = agent.answer(request.question)
    return ChatResponse(answer=answer)
