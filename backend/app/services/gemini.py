from google import genai
from google.genai import types
from pydantic import BaseModel, Field

from app.core.settings import settings

GENERATE_CONTENT_CONFIG = types.GenerateContentConfig(
    response_mime_type="application/json",
    response_schema=genai.types.Schema(
        type=genai.types.Type.OBJECT,
        properties={
            "tax_rate": genai.types.Schema(
                type=genai.types.Type.NUMBER,
            ),
            "service_charge": genai.types.Schema(
                type=genai.types.Type.NUMBER,
            ),
            "items": genai.types.Schema(
                type=genai.types.Type.ARRAY,
                items=genai.types.Schema(
                    type=genai.types.Type.OBJECT,
                    properties={
                        "name": genai.types.Schema(
                            type=genai.types.Type.STRING,
                        ),
                        "price": genai.types.Schema(
                            type=genai.types.Type.NUMBER,
                        ),
                        "quantity": genai.types.Schema(
                            type=genai.types.Type.NUMBER,
                        ),
                    },
                ),
            ),
        },
    ),
)


def generate_content_from_image(prompt: str, image_bytes: bytes, mime_type: str) -> str:
    """
    Use Gemini API to extract bill details from an image.

    :param image_bytes: The image bytes of the bill
    :return: Extracted bill details as an OCRBill object
    """
    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    model = "gemini-2.5-flash"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=prompt),
                types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
            ],
        ),
    ]

    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=GENERATE_CONTENT_CONFIG,
    )

    if response.candidates is None or len(response.candidates) == 0:
        raise ValueError("No response from Gemini API")

    candidate = response.candidates[0]
    if candidate.content is None or candidate.content.parts is None or len(candidate.content.parts) == 0:
        raise ValueError("No content parts in Gemini API response")

    bill_data = candidate.content.parts[0].text
    if bill_data is None:
        raise ValueError("No text content in Gemini API response")

    return bill_data
