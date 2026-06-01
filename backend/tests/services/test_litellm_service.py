from dataclasses import dataclass, field
from typing import Optional
from unittest.mock import MagicMock

import pytest

from app.services.litellm_service import get_bill_details_from_image
from tests import examples


@dataclass
class MockChoice:
    message: MagicMock = field(default_factory=lambda: MagicMock(content=None))


@dataclass
class MockLiteLLMResponse:
    choices: list[MockChoice] = field(default_factory=list)


def mock_litellm_completion(
    monkeypatch: pytest.MonkeyPatch, response: Optional[MockLiteLLMResponse] = None
) -> MagicMock:
    """Patch litellm.completion and return the mock for inspection."""
    mock_fn = MagicMock(return_value=response)
    monkeypatch.setattr("app.services.litellm_service.completion", mock_fn)
    return mock_fn


class TestGetBillDetailsFromImage:
    def test_success(self, monkeypatch: pytest.MonkeyPatch):
        llm_success_response_text = examples.simple_bill.OCR_BILL.model_dump_json()

        response = MockLiteLLMResponse(choices=[MockChoice(message=MagicMock(content=llm_success_response_text))])
        mock_fn = mock_litellm_completion(monkeypatch, response)

        result = get_bill_details_from_image(image_bytes=b"fake-image-bytes", mime_type="image/png")

        assert result == llm_success_response_text
        mock_fn.assert_called_once()
        call_kwargs = mock_fn.call_args[1]
        assert call_kwargs["model"] == "gemini/gemini-2.5-flash"
        assert call_kwargs["api_base"] == "https://proxy.clanker.ai"
        assert call_kwargs["api_key"] == "clanker123"

    @pytest.mark.parametrize(
        "mock_response, error_message",
        [
            (MockLiteLLMResponse(choices=[]), "No response from LiteLLM"),
            (
                MockLiteLLMResponse(choices=[MockChoice(message=MagicMock(content=None))]),
                "No content in LiteLLM response",
            ),
        ],
    )
    def test_errors_in_response(
        self, monkeypatch: pytest.MonkeyPatch, mock_response: MockLiteLLMResponse, error_message: str
    ):
        mock_litellm_completion(monkeypatch, mock_response)

        with pytest.raises(ValueError, match=error_message):
            get_bill_details_from_image(image_bytes=b"fake", mime_type="image/png")
