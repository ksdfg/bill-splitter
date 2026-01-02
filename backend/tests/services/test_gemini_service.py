from __future__ import annotations

import pytest

from app.services.gemini import generate_content_from_image
from tests.conftest import mock_genai_client_with_response_no_candidates, mock_genai_client_with_response_no_parts, mock_genai_client_with_response_no_text, mock_genai_client_with_response_success


def test_generate_content_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Success path: the Gemini mock returns a candidate with a part.text string.
    Assert the function returns that text and that the model used was correct.
    """
    expected_text = (
        '{"items":[{"name":"Coffee","price":3.5,"quantity":1}],"amount_paid":3.5,"tax_rate":0.0,"service_charge":0.0}'
    )

    # Arrange: configure genai client to return a mock with desired response
    client_instance = mock_genai_client_with_response_success(monkeypatch, expected_text)

    result = generate_content_from_image(prompt="parse this", image_bytes=b"fake-image-bytes", mime_type="image/png")

    assert result == expected_text

    # Verify the model used is the expected model
    last_call = client_instance.models.last_call
    assert last_call is not None, "expected generate_content to be called"
    assert last_call["model"] == "gemini-2.5-flash"


def test_generate_content_no_candidates_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    If Gemini returns an empty candidates list, the function should raise ValueError.
    """
    mock_genai_client_with_response_no_candidates(monkeypatch)

    with pytest.raises(ValueError) as exc:
        generate_content_from_image(prompt="parse", image_bytes=b"fake", mime_type="image/png")
    assert "No response from Gemini API" in str(exc.value)


def test_generate_content_no_content_parts_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    If the candidate has no content.parts, raise ValueError.
    """
    mock_genai_client_with_response_no_parts(monkeypatch)

    with pytest.raises(ValueError) as exc:
        generate_content_from_image(prompt="parse", image_bytes=b"fake", mime_type="image/png")

    assert "No content parts in Gemini API response" in str(exc.value)


def test_generate_content_no_text_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    If the first part exists but its .text is None, raise ValueError.
    """
    mock_genai_client_with_response_no_text(monkeypatch)

    with pytest.raises(ValueError) as exc:
        generate_content_from_image(prompt="parse", image_bytes=b"fake", mime_type="image/png")

    assert "No text content in Gemini API response" in str(exc.value)
