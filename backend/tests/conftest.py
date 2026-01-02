from dataclasses import dataclass, field
from typing import Any, Dict, Iterator, List, Optional

import pytest

import app.core.settings as settings_module
import app.services.gemini as gemini_module


@pytest.fixture(autouse=True)
def set_dummy_gemini_key(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """
    Ensure a dummy GEMINI_API_KEY is available for all tests.

    The production code creates a `settings` instance at import time, so
    mutating that instance is sufficient for tests.

    Args:
        monkeypatch: pytest's MonkeyPatch fixture used to set attributes/env vars.

    Yields:
        None
    """
    monkeypatch.setattr(settings_module.settings, "GEMINI_API_KEY", "dummy-key", raising=False)
    yield


# Mocks for the genai.Client and its response structure.


@dataclass
class GenaiResponse:
    """
    Top-level response dataclass. Subtypes are nested dataclasses to keep the
    structure grouped and readable (use as `Response.Part`, `Response.Content`, etc.).
    """

    candidates: Optional[List["GenaiResponse.Candidate"]] = None

    @dataclass
    class Part:
        text: Optional[str] = None

    @dataclass
    class Content:
        parts: List["GenaiResponse.Part"] = field(default_factory=list)

    @dataclass
    class Candidate:
        content: Optional["GenaiResponse.Content"] = None


class MockGenaiClient:
    """
    Mock of genai.Client with only the parts needed for testing.
    """
    
    class MockModels:
        def __init__(self, response: Optional[GenaiResponse]) -> None:
            self._response: Optional[GenaiResponse] = response
            self.last_call: Optional[Dict[str, Any]] = None

        def generate_content(self, model: str, contents: Any, config: Any) -> Optional[GenaiResponse]:
            # Record the call so tests can assert on the model/args used
            self.last_call = {"model": model, "contents": contents, "config": config}
            return self._response

    def __init__(self, response: Optional[GenaiResponse]) -> None:
        self.models = self.MockModels(response)


# Helpers to configure the mock genai client for a desired response.


def mock_genai_client_with_response(monkeypatch: pytest.MonkeyPatch, response: Optional[GenaiResponse]) -> MockGenaiClient:
    """
    Create a MockClient with `response`, patch `gemini_module.genai.Client` to
    return that instance, and return the instance for optional inspection.
    """
    client_instance = MockGenaiClient(response)
    # Patch the Client constructor used in the module under test to always return our instance
    monkeypatch.setattr(gemini_module.genai, "Client", lambda api_key, inst=client_instance: inst)
    return client_instance


def mock_genai_client_with_response_success(monkeypatch: pytest.MonkeyPatch, text: str) -> MockGenaiClient:
    """Build a successful response and configure the mocked client."""
    response = GenaiResponse(candidates=[GenaiResponse.Candidate(content=GenaiResponse.Content(parts=[GenaiResponse.Part(text=text)]))])
    return mock_genai_client_with_response(monkeypatch, response)


def mock_genai_client_with_response_no_candidates(monkeypatch: pytest.MonkeyPatch) -> MockGenaiClient:
    """Configure the mocked client to return a response with no candidates."""
    response = GenaiResponse(candidates=[])
    return mock_genai_client_with_response(monkeypatch, response)


def mock_genai_client_with_response_no_parts(monkeypatch: pytest.MonkeyPatch) -> MockGenaiClient:
    """Configure the mocked client to return a candidate with no content.parts."""
    response = GenaiResponse(candidates=[GenaiResponse.Candidate(content=GenaiResponse.Content(parts=[]))])
    return mock_genai_client_with_response(monkeypatch, response)


def mock_genai_client_with_response_no_text(monkeypatch: pytest.MonkeyPatch) -> MockGenaiClient:
    """Configure the mocked client to return a part whose text is None."""
    response = GenaiResponse(candidates=[GenaiResponse.Candidate(content=GenaiResponse.Content(parts=[GenaiResponse.Part(text=None)]))])
    return mock_genai_client_with_response(monkeypatch, response)
