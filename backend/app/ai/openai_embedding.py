from typing import List
from openai import OpenAI
from .interfaces import EmbeddingClient


class OpenAIEmbeddingClient:
    """Клиент для получения эмбеддингов через OpenAI API."""

    def __init__(self, api_key: str, model: str):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        response = self.client.embeddings.create(
            model=self.model,
            input=texts,
        )
        return [item.embedding for item in response.data]