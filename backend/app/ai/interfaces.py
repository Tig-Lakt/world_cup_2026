from typing import Protocol, List


class LLMClient(Protocol):
    """Генерирует ответ языковой модели."""
    def generate(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        ...


class EmbeddingClient(Protocol):
    """Возвращает векторы для списка текстов."""
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        ...


class VectorStore(Protocol):
    """Векторное хранилище фактов."""
    def init_collection(self, recreate: bool = False) -> None:
        ...
    def load_facts(self, facts: List[str]) -> int:
        ...
    def search(self, query: str, limit: int) -> List[str]:
        ...