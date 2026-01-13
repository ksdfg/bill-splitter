from dataclasses import dataclass, field
from typing import Any, Optional

import pytest

from app.services.gemini import get_bill_details_from_image
from tests import examples


@dataclass
class GeminiResponse:
    """
    Top-level response dataclass. Subtypes are nested dataclasses to keep the
    structure grouped and readable (use as `GeminiResponse.Part`, `GeminiResponse.Content`, etc.).
    """

    candidates: Optional[list["GeminiResponse.Candidate"]] = None

    @dataclass
    class Part:
        text: Optional[str] = None

    @dataclass
    class Content:
        parts: list["GeminiResponse.Part"] = field(default_factory=list)

    @dataclass
    class Candidate:
        content: Optional["GeminiResponse.Content"] = None


class MockGeminiClient:
    """
    Mock of genai.Client with only the parts needed for testing.
    """

    class MockModels:
        def __init__(self, response: Optional[GeminiResponse]) -> None:
            self._response: Optional[GeminiResponse] = response
            self.last_call: Optional[dict[str, Any]] = None

        def generate_content(self, model: str, contents: Any, config: Any) -> Optional[GeminiResponse]:
            # Record the call so tests can assert on the model/args used
            self.last_call = {"model": model, "contents": contents, "config": config}
            return self._response

    def __init__(self, response: Optional[GeminiResponse]) -> None:
        self.models = self.MockModels(response)


def mock_gemini_client(monkeypatch: pytest.MonkeyPatch, response: Optional[GeminiResponse] = None) -> MockGeminiClient:
    """
    Create a MockClient with `response`, patch `gemini_module.genai.Client` to
    return that instance, and return the instance for optional inspection.
    """
    client_instance = MockGeminiClient(response)
    monkeypatch.setattr("app.services.gemini.Client", lambda api_key, inst=client_instance: inst)
    return client_instance


class TestGetBillDetailsFromImage:
    def test_success(self, monkeypatch: pytest.MonkeyPatch):
        llm_success_response_text = examples.simple_bill.OCR_BILL.model_dump_json()

        # Mock the Gemini client
        mock_response = GeminiResponse(
            candidates=[
                GeminiResponse.Candidate(
                    content=GeminiResponse.Content(parts=[GeminiResponse.Part(text=llm_success_response_text)])
                )
            ]
        )
        mock_client = mock_gemini_client(monkeypatch, mock_response)

        ocr_bill = get_bill_details_from_image(image_bytes=b"fake-image-bytes", mime_type="image/png")

        # Verify the model used is the expected model
        last_call = mock_client.models.last_call
        assert last_call is not None, "expected generate_content to be called"
        assert last_call["model"] == "gemini-2.5-flash"

        assert ocr_bill == llm_success_response_text

    @pytest.mark.parametrize(
        "mock_response, error_message",
        [
            (GeminiResponse(candidates=[]), "No response from Gemini API"),
            (
                GeminiResponse(candidates=[GeminiResponse.Candidate(content=GeminiResponse.Content(parts=[]))]),
                "No content parts in Gemini API response",
            ),
            (
                GeminiResponse(
                    candidates=[
                        GeminiResponse.Candidate(content=GeminiResponse.Content(parts=[GeminiResponse.Part(text=None)]))
                    ]
                ),
                "No text content in Gemini API response",
            ),
        ],
    )
    def test_errors_in_gemini_response(
        self, monkeypatch: pytest.MonkeyPatch, mock_response: GeminiResponse, error_message: str
    ):
        # Mock the Gemini client to return an error response
        mock_client = mock_gemini_client(monkeypatch, mock_response)

        with pytest.raises(ValueError) as exc:
            get_bill_details_from_image(image_bytes=b"fake", mime_type="image/png")

        assert str(exc.value) == error_message

        # Verify the model used is the expected model
        last_call = mock_client.models.last_call
        assert last_call is not None, "expected generate_content to be called"
        assert last_call["model"] == "gemini-2.5-flash"
