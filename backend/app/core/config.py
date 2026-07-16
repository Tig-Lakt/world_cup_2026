from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # База данных
    DATABASE_URL: str

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: str

    # Парсер Flashscore
    FLASHSCORE_REQUEST_DELAY: float = 1.5

    # Парсер championat.com (результаты + статистика, этап 2.5/3)
    CHAMPIONAT_REQUEST_DELAY: float = 1.5

    # API
    PROJECT_NAME: str = "World Cup 2026 Tracker"

    # Qdrant — не используется на этапе 1 (расписание), но поле оставлено
    # опциональным, чтобы .env можно было заполнять по мере готовности этапов.
    QDRANT_HOST: str
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION: str = "wc2026_knowledge"

    # OpenAI — не используется на этапе 1, см. комментарий выше.
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"

    # AI Agent
    AI_CONTEXT_LIMIT: int = 5
    AI_TEMPERATURE: float = 0.3

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()
