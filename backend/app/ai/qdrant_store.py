import logging
import uuid
from typing import List

from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

from .interfaces import EmbeddingClient

from backend.app.core.constants import DEFAULT_EMBEDDING_DIM

logger = logging.getLogger(__name__)


class QdrantStore:
    """Векторное хранилище фактов в Qdrant."""

    def __init__(
        self,
        host: str,
        port: int,
        collection_name: str,
        embedding_client: EmbeddingClient,
        embedding_dim: int = DEFAULT_EMBEDDING_DIM,
    ):
        self.client = QdrantClient(host=host, port=port)
        self.collection_name = collection_name
        self.embedding_client = embedding_client
        self.embedding_dim = embedding_dim

    def init_collection(self, recreate: bool = False) -> None:
        """Создаёт коллекцию, при recreate=True удаляет существующую."""
        exists = self.client.collection_exists(self.collection_name)

        if exists and recreate:
            logger.info("🗑️ Удаляем существующую коллекцию %s перед перезаливкой", self.collection_name)
            self.client.delete_collection(self.collection_name)
            exists = False

        if not exists:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=self.embedding_dim, distance=Distance.COSINE),
            )
            logger.info("✅ Коллекция %s создана", self.collection_name)
        else:
            logger.info("ℹ️ Коллекция %s уже существует", self.collection_name)

    def load_facts(self, facts: List[str]) -> int:
        """Загружает факты в Qdrant батчами, возвращает количество загруженных."""
        if not facts:
            logger.warning("⚠️ Список фактов пуст, ничего не загружено")
            return 0

        BATCH_SIZE = 100
        total_loaded = 0

        for i in range(0, len(facts), BATCH_SIZE):
            batch = facts[i:i + BATCH_SIZE]
            embeddings = self.embedding_client.get_embeddings(batch)

            points = [
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=embedding,
                    payload={"text": text},
                )
                for text, embedding in zip(batch, embeddings)
            ]

            self.client.upsert(collection_name=self.collection_name, points=points)
            total_loaded += len(points)
            logger.info("📥 Загружено фактов: %d/%d", total_loaded, len(facts))

        return total_loaded

    def search(self, query: str, limit: int = 5) -> List[str]:
        """Ищет наиболее релевантные факты, возвращает их тексты."""
        query_embedding = self.embedding_client.get_embeddings([query])[0]

        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_embedding,
            limit=limit,
        ).points

        return [point.payload["text"] for point in results if point.payload]
