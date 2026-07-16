# backend/app/ai/factories.py
from ..core.config import Settings
from .openai_embedding import OpenAIEmbeddingClient
from .qdrant_store import QdrantStore

def create_embedding_client(settings: Settings) -> OpenAIEmbeddingClient:
    return OpenAIEmbeddingClient(
        api_key=settings.OPENAI_API_KEY,
        model=settings.OPENAI_EMBEDDING_MODEL,
    )

def create_qdrant_store(settings: Settings, embedding_client: OpenAIEmbeddingClient) -> QdrantStore:
    return QdrantStore(
        host=settings.QDRANT_HOST,
        port=settings.QDRANT_PORT,
        collection_name=settings.QDRANT_COLLECTION,
        embedding_client=embedding_client,
        # embedding_dim=settings.QDRANT_EMBEDDING_DIM  # если вынесете в настройки
    )
