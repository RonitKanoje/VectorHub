from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from threadcore.services.chat.gemini_memory_client import GeminiPersonalMemoryLLM
from threadcore.services.chat.schemas import PersonalMemoryDecision


def test_gemini_memory_client_parses_structured_output():
    response = SimpleNamespace(text='{"should_store": true, "facts": ["User likes cats"], "should_retrieve": false}')
    client = MagicMock()
    client.models.generate_content.return_value = response

    llm = GeminiPersonalMemoryLLM(client=client, model_name="gemini-2.5-flash-lite")
    result = llm.invoke([SimpleNamespace(content="My name is Ronit")])

    assert isinstance(result, PersonalMemoryDecision)
    assert result.should_store is True
    assert result.facts == ["User likes cats"]
    assert result.should_retrieve is False


def test_gemini_memory_client_rejects_invalid_json():
    response = SimpleNamespace(text='{"should_store": true, "facts": [1], "should_retrieve": false}')
    client = MagicMock()
    client.models.generate_content.return_value = response

    llm = GeminiPersonalMemoryLLM(client=client, model_name="gemini-2.5-flash-lite")

    with pytest.raises(ValueError):
        llm.invoke([SimpleNamespace(content="My name is Ronit")])
