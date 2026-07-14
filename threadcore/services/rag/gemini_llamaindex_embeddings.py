from typing import Any, List, Optional

from google import genai
from google.genai import types

from llama_index.core.base.embeddings.base import (
    BaseEmbedding,
    Embedding,
)
from pydantic import PrivateAttr
from threadcore.core.config import settings


class GeminiLlamaIndexEmbeddings(BaseEmbedding):
    """Native LlamaIndex embedding model backed by Gemini."""

    model_name: str = settings.gemini_embedding_model

    _client: Any = PrivateAttr()
    _dimension: Optional[int] = PrivateAttr(default=None)

    def __init__(
        self,
        model_name: str | None = None,
        client: Any | None = None,
        **kwargs: Any,
    ) -> None:
        resolved_model_name = model_name or settings.gemini_embedding_model

        super().__init__(model_name=resolved_model_name, **kwargs)

        self._client = client or genai.Client(
            api_key=settings.gemini_api_key,
            vertexai=False,
        )
        self._dimension = None

    @classmethod
    def class_name(cls) -> str:
        return "GeminiLlamaIndexEmbeddings"

    @property
    def dimension(self) -> int:
        if self._dimension is None:
            self._dimension = self._fetch_dimension()
        return self._dimension

    def _fetch_dimension(self) -> int:
        response = self._client.models.embed_content(
            model=self.model_name,
            contents="dimension probe",
            config=types.EmbedContentConfig(),
        )

        emb = self._extract_values(response)

        if not emb:
            raise RuntimeError("Gemini returned empty embedding.")

        return len(emb)

    def _get_query_embedding(self, query: str) -> Embedding:
        response = self._client.models.embed_content(
            model=self.model_name,
            contents=query,
            config=types.EmbedContentConfig(
                outputDimensionality=self.dimension
            ),
        )

        embeddings = getattr(response, "embeddings", None)

        if not embeddings:
            raise RuntimeError("Gemini returned no embedding.")

        return self._extract_values(embeddings[0])

    async def _aget_query_embedding(self, query: str) -> Embedding:
        return self._get_query_embedding(query)

    def _get_text_embedding(self, text: str) -> Embedding:
        return self._get_query_embedding(text)

    async def _aget_text_embedding(self, text: str) -> Embedding:
        return self._get_query_embedding(text)

    def _get_text_embeddings(
        self,
        texts: List[str],
    ) -> List[Embedding]:

        response = self._client.models.embed_content(
            model=self.model_name,
            contents=texts,
            config=types.EmbedContentConfig(
                outputDimensionality=self.dimension
            ),
        )

        embeddings = getattr(response, "embeddings", None) or []

        return [
            self._extract_values(item)
            for item in embeddings
        ]

    async def _aget_text_embeddings(
        self,
        texts: List[str],
    ) -> List[Embedding]:
        return self._get_text_embeddings(texts)

    @staticmethod
    def _extract_values(payload: Any) -> Embedding:
        if payload is None:
            return []

        values = getattr(payload, "values", None)

        if values is not None:
            return [float(x) for x in values]

        if isinstance(payload, dict):

            if "values" in payload:
                return [float(x) for x in payload["values"]]

            if payload.get("embeddings"):
                return GeminiLlamaIndexEmbeddings._extract_values(
                    payload["embeddings"][0]
                )

        embeddings = getattr(payload, "embeddings", None)

        if embeddings:
            return GeminiLlamaIndexEmbeddings._extract_values(
                embeddings[0]
            )

        raise RuntimeError(
            f"Unexpected Gemini embedding payload: {payload}"
        )