import json
import logging
from typing import Any, Sequence

from google import genai
from google.genai import types
from pydantic import ValidationError

from threadcore.core.config import settings
from threadcore.services.chat.schemas import PersonalMemoryDecision

logger = logging.getLogger(__name__)


class GeminiPersonalMemoryLLM:
    """Dedicated Gemini client for personal-memory extraction."""

    def __init__(self, client: Any | None = None, model_name: str | None = None) -> None:
        self.client = client or genai.Client(api_key=settings.gemini_api_key)
        self.model_name = model_name or settings.gemini_memory_model

    def invoke(self, messages: Sequence[Any]) -> PersonalMemoryDecision:
        prompt = self._build_prompt(messages)
        logger.info("=========================\nMemory Extraction\n=========================")
        logger.info("User message:\n%s", prompt)

        config = types.GenerateContentConfig(
            temperature=0.0,
            responseMimeType="application/json",
            responseSchema=PersonalMemoryDecision.model_json_schema(),
        )

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config,
            )
        except TypeError:
            fallback_prompt = (
                f"{prompt}\n\nReturn only strict JSON matching this schema:"
                f" {json.dumps(PersonalMemoryDecision.model_json_schema())}"
            )
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=fallback_prompt,
                config=types.GenerateContentConfig(temperature=0.0),
            )
        except Exception as exc:
            logger.exception("Gemini memory extraction failed")
            raise RuntimeError(f"Gemini memory extraction failed: {exc}") from exc

        raw_text = getattr(response, "text", None)
        logger.info("Gemini raw response:\n%s", raw_text)

        parsed = self._parse_response(raw_text)
        logger.info("Parsed PersonalMemoryDecision:\n%s", parsed)
        logger.info("should_store: %s", parsed.should_store)
        logger.info("facts: %s", parsed.facts)
        logger.info("should_retrieve: %s", parsed.should_retrieve)
        return parsed

    def _build_prompt(self, messages: Sequence[Any]) -> str:
        parts: list[str] = []
        for message in messages:
            content = getattr(message, "content", None)
            if isinstance(content, str) and content.strip():
                parts.append(content.strip())
        return "\n".join(parts)

    def _parse_response(self, raw_text: Any) -> PersonalMemoryDecision:
        if not raw_text:
            raise ValueError("Gemini memory extraction returned empty content")

        text = str(raw_text).strip()
        try:
            payload = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Gemini memory extraction returned invalid JSON: {text}") from exc

        try:
            return PersonalMemoryDecision.model_validate(payload)
        except ValidationError as exc:
            raise ValueError(f"Gemini memory extraction returned invalid PersonalMemoryDecision: {payload}") from exc

