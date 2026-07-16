import logging

from .interfaces import LLMClient, VectorStore
from .prompts import SYSTEM_PROMPT, build_user_prompt

logger = logging.getLogger(__name__)


class AIAgent:
    """RAG-агент для чата о ЧМ-2026."""

    def __init__(
        self,
        llm_client: LLMClient,
        vector_store: VectorStore,
        context_limit: int = 5,
        temperature: float = 0.3,
    ):
        self.llm_client = llm_client
        self.vector_store = vector_store
        self.context_limit = context_limit
        self.temperature = temperature

    def answer(self, question: str) -> str:
        """Отвечает на вопрос пользователя с привлечением фактов из Qdrant."""
        try:
            context_facts = self.vector_store.search(question, self.context_limit)
        except Exception as e:
            logger.warning("⚠️ Поиск в Qdrant не удался: %s — отвечаем без контекста", e)
            context_facts = []

        user_prompt = build_user_prompt(question, context_facts)

        try:
            return self.llm_client.generate(SYSTEM_PROMPT, user_prompt, self.temperature)
        except Exception as e:
            logger.error("Ошибка OpenAI: %s", e)
            return "Извините, сервис AI временно недоступен."