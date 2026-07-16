from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from backend.app.core.config import get_settings, Settings
from backend.app.core.database import get_db
from backend.app.ai.openai_chat import OpenAIChatClient
from backend.app.ai.agent import AIAgent

from backend.app.ai.factories import create_embedding_client, create_qdrant_store

# Тип для инъекции сессии БД в эндпоинты
DbSession = Annotated[Session, Depends(get_db)]


def get_ai_agent(settings: Settings = Depends(get_settings)):
    embedding_client = create_embedding_client(settings)
    vector_store = create_qdrant_store(settings, embedding_client)
    chat_client = OpenAIChatClient(settings.OPENAI_API_KEY, settings.OPENAI_MODEL)
    return AIAgent(
        llm_client=chat_client,
        vector_store=vector_store,
        context_limit=settings.AI_CONTEXT_LIMIT,
        temperature=settings.AI_TEMPERATURE,
    )
