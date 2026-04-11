from dataclasses import dataclass, field
from typing import Any, Optional
from unittest.mock import MagicMock

import pytest

from app.core.settings import settings
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

        response = MockLiteLLMResponse(
            choices=[MockChoice(message=MagicMock(content=llm_success_response_text))]
        )
        mock_fn = mock_litellm_completion(monkeypatch, response)
        monkeypatch.setattr("app.services.litellm_service.settings.LITELLM_MODEL", "gemini/gemini-2.5-flash")

        result = get_bill_details_from_image(image_bytes=b"fake-image-bytes", mime_type="image/png")

        assert result == llm_success_response_text
        mock_fn.assert_called_once()
        call_kwargs = mock_fn.call_args[1]
        assert call_kwargs["model"] == "gemini/gemini-2.5-flash"

    def test_no_model_set(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr("app.services.litellm_service.settings.LITELLM_MODEL", None)

        with pytest.raises(ValueError, match="LITELLM_MODEL is not set"):
            get_bill_details_from_image(image_bytes=b"fake", mime_type="image/png")

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
        monkeypatch.setattr("app.services.litellm_service.settings.LITELLM_MODEL", "gemini/gemini-2.5-flash")

        with pytest.raises(ValueError, match=error_message):
            get_bill_details_from_image(image_bytes=b"fake", mime_type="image/png")


class TestLiteLLMConfiguration:
    """Tests for LiteLLM API base URL and model configuration."""

    success_response = MockLiteLLMResponse(
        choices=[MockChoice(message=MagicMock(content='{"items": [], "amount_paid": 0, "tax_rate": 0, "service_charge": 0}'))]
    )

    @pytest.mark.parametrize(
        "api_base, api_key",
        [
            ("https://custom-proxy.example.com", None),
            (None, "custom-api-key"),
            ("https://custom-proxy.example.com", "custom-api-key"),
        ],
    )
    def test_custom_configuration(
        self, monkeypatch: pytest.MonkeyPatch, api_base: Optional[str], api_key: Optional[str]
    ):
        monkeypatch.setattr("app.services.litellm_service.settings.LITELLM_MODEL", "openai/gpt-4o")
        monkeypatch.setattr("app.services.litellm_service.settings.LITELLM_API_BASE", api_base)
        monkeypatch.setattr("app.services.litellm_service.settings.LITELLM_API_KEY", api_key)

        mock_fn = mock_litellm_completion(monkeypatch, self.success_response)

        get_bill_details_from_image(image_bytes=b"fake", mime_type="image/png")

        mock_fn.assert_called_once()
        call_kwargs = mock_fn.call_args[1]

        assert call_kwargs["model"] == "openai/gpt-4o"
        if api_base:
            assert call_kwargs["api_base"] == api_base
        else:
            assert "api_base" not in call_kwargs
        if api_key:
            assert call_kwargs["api_key"] == api_key
        else:
            assert "api_key" not in call_kwargs
