import json
import logging
from typing import Any, Sequence

from langchain_core.messages import HumanMessage
from pydantic import ValidationError

from threadcore.services.chat.llm_config import llm
from threadcore.services.chat.schemas import PersonalMemoryDecision

logger = logging.getLogger(__name__)


class GeminiPersonalMemoryLLM:
    """
    Temporary implementation backed by the shared LangChain LLM.
    The class name is intentionally kept unchanged so the rest of
    the codebase does not need to change.
    """

    def __init__(self):
        self.structured_llm = llm.with_structured_output(PersonalMemoryDecision)

    def invoke(self, messages: Sequence[Any]) -> PersonalMemoryDecision:

        prompt = self._build_prompt(messages)

        logger.info("=========================")
        logger.info("Memory Extraction")
        logger.info("=========================")
        logger.info(prompt)

        try:
            response = self.structured_llm.invoke(
                HumanMessage(content=prompt)
            )

            logger.info(response)

            return response

        except ValidationError as exc:
            raise ValueError(
                f"Invalid PersonalMemoryDecision: {exc}"
            ) from exc

        except Exception as exc:
            logger.exception("Memory extraction failed")
            raise RuntimeError(
                f"Memory extraction failed: {exc}"
            ) from exc

    def _build_prompt(self, messages: Sequence[Any]) -> str:
        parts = []

        for message in messages:
            content = getattr(message, "content", None)

            if isinstance(content, str) and content.strip():
                parts.append(content.strip())

        return "\n".join(parts)