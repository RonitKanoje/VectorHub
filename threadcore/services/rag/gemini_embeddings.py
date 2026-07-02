from typing import Any

from langchain_core.embeddings import Embeddings
from google import genai
from google.genai import types

from threadcore.core.config import settings


class GeminiEmbeddingsAdapter(Embeddings):
    """Gemini-backed embedding adapter that reads the output dimension from the SDK response."""

    def __init__(self, model_name: str | None = None, client: Any | None = None) -> None:
        self.model_name = model_name or settings.gemini_embedding_model
        self.client = client or genai.Client(api_key=settings.gemini_api_key)
        self._dimension = None

    @property
    def dimension(self) -> int:
        if self._dimension is None:
            self._dimension = self._fetch_dimension()
        return self._dimension

    def _fetch_dimension(self) -> int:
        response = self.client.models.embed_content(
            model=self.model_name,
            contents="dimension probe",
            config=types.EmbedContentConfig(),
        )
        embedding = self._extract_values(response)
        if not embedding:
            raise RuntimeError("Gemini embedding probe returned no embeddings")
        return len(embedding)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        response = self.client.models.embed_content(
            model=self.model_name,
            contents=texts,
            config=types.EmbedContentConfig(outputDimensionality=self.dimension),
        )
        embeddings = getattr(response, "embeddings", None) or []
        return [self._extract_values(item) for item in embeddings]

    def embed_query(self, text: str) -> list[float]:
        response = self.client.models.embed_content(
            model=self.model_name,
            contents=text,
            config=types.EmbedContentConfig(outputDimensionality=self.dimension),
        )
        embeddings = getattr(response, "embeddings", None) or []
        if not embeddings:
            raise RuntimeError("Gemini embedding request returned no embeddings")
        return self._extract_values(embeddings[0])

    @staticmethod
    def _extract_values(payload: Any) -> list[float]:
        if payload is None:
            return []

        if isinstance(payload, dict):
            if "values" in payload:
                return [float(value) for value in payload["values"]]
            if "embeddings" in payload and payload["embeddings"]:
                return GeminiEmbeddingsAdapter._extract_values(payload["embeddings"][0])

        values = getattr(payload, "values", None)
        if values is not None:
            return [float(value) for value in values]

        embeddings = getattr(payload, "embeddings", None)
        if embeddings:
            return GeminiEmbeddingsAdapter._extract_values(embeddings[0])

        raise RuntimeError(f"Gemini embedding payload did not include values: {payload}")
