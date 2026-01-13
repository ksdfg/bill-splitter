from dataclasses import dataclass, field
from json import dumps
from typing import Any, Iterator, Optional

import pytest

from app.services.gemini import get_bill_details_from_image


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


@pytest.fixture
def mock_gemini_client(monkeypatch: pytest.MonkeyPatch, request: pytest.FixtureRequest) -> Iterator[MockGeminiClient]:
    """
    Create a MockClient with `response`, patch `gemini_module.genai.Client` to
    return that instance, and return the instance for optional inspection.
    """
    #
    marker = request.node.get_closest_marker("mock_llm_response")
    mock_llm_response = marker.args[0] if marker else GeminiResponse()

    client_instance = MockGeminiClient(mock_llm_response)
    # Patch the Client constructor used in the module under test to always return our instance
    monkeypatch.setattr("app.services.gemini.Client", lambda api_key, inst=client_instance: inst)
    yield client_instance


class TestGetBillDetailsFromImage:
    llm_success_response_text = dumps(
        {
            "tax_rate": 0.05,
            "service_charge": 0.1,
            "amount_paid": 1207.50,
            "items": [
                {
                    "name": "Pizza",
                    "price": 600.0,
                    "quantity": 1,
                },
                {
                    "name": "Coke",
                    "price": 150.0,
                    "quantity": 1,
                },
                {
                    "name": "Ice Cream",
                    "price": 300.0,
                    "quantity": 1,
                },
            ],
        },
        sort_keys=True,
    )

    @pytest.mark.mock_llm_response(
        GeminiResponse(
            candidates=[
                GeminiResponse.Candidate(
                    content=GeminiResponse.Content(parts=[GeminiResponse.Part(text=llm_success_response_text)])
                )
            ]
        )
    )
    def test_success(self, mock_gemini_client: MockGeminiClient):
        ocr_bill = get_bill_details_from_image(image_bytes=b"fake-image-bytes", mime_type="image/png")

        # Verify the model used is the expected model
        last_call = mock_gemini_client.models.last_call
        assert last_call is not None, "expected generate_content to be called"
        assert last_call["model"] == "gemini-2.5-flash"

        assert ocr_bill == self.llm_success_response_text

    @pytest.mark.mock_llm_response(GeminiResponse(candidates=[]))
    def test_no_candidates(self, mock_gemini_client: MockGeminiClient):
        with pytest.raises(ValueError) as exc:
            get_bill_details_from_image(image_bytes=b"fake", mime_type="image/png")

        assert "No response from Gemini API" in str(exc.value)

        # Verify the model used is the expected model
        last_call = mock_gemini_client.models.last_call
        assert last_call is not None, "expected generate_content to be called"
        assert last_call["model"] == "gemini-2.5-flash"

    @pytest.mark.mock_llm_response(
        GeminiResponse(candidates=[GeminiResponse.Candidate(content=GeminiResponse.Content(parts=[]))])
    )
    def test_no_parts(self, mock_gemini_client: MockGeminiClient):
        with pytest.raises(ValueError) as exc:
            get_bill_details_from_image(image_bytes=b"fake", mime_type="image/png")

        assert "No content parts in Gemini API response" in str(exc.value)

        # Verify the model used is the expected model
        last_call = mock_gemini_client.models.last_call
        assert last_call is not None, "expected generate_content to be called"
        assert last_call["model"] == "gemini-2.5-flash"

    @pytest.mark.mock_llm_response(
        GeminiResponse(
            candidates=[
                GeminiResponse.Candidate(content=GeminiResponse.Content(parts=[GeminiResponse.Part(text=None)]))
            ]
        )
    )
    def test_no_text(self, mock_gemini_client: MockGeminiClient):
        with pytest.raises(ValueError) as exc:
            get_bill_details_from_image(image_bytes=b"fake", mime_type="image/png")

        assert "No text content in Gemini API response" in str(exc.value)

        # Verify the model used is the expected model
        last_call = mock_gemini_client.models.last_call
        assert last_call is not None, "expected generate_content to be called"
        assert last_call["model"] == "gemini-2.5-flash"
