from google.genai import Client, types

from app.core.settings import settings

BILL_OCR_PROMPT = """
You are an expert at extracting information from bills and receipts.
Your task is to analyze the provided image of a bill and extract the following information in JSON format:

Extract a Bill object with the following structure:
- items: A list of items, where each item contains:
  - name: The name of the item (string, non-empty)
  - price: The price of the item (float, must be positive)
  - quantity: The quantity ordered (integer, must be positive)
- tax_rate: The tax rate applied to the bill as a decimal (float, between 0.0 and 1.0, default is 0.0 if not found)
- service_charge: The service charge as a decimal (float, between 0.0 and 1.0, default is 0.0 if not found)
- amount_paid: The final total amount that must be paid, after applying all tax, service charges and discounts (float, must be positive)

Important notes:
- Extract only the items that appear on the bill
- Calculate tax_rate and service_charge from the bill if visible, otherwise use defaults
- Ensure all extracted values match the specified types and constraints
- Return the response as valid JSON that matches the Bill schema

Please analyze the bill image and extract the information now.
"""

GENERATE_CONTENT_CONFIG = types.GenerateContentConfig(
    response_mime_type="application/json",
    response_schema=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "tax_rate": types.Schema(
                type=types.Type.NUMBER,
            ),
            "service_charge": types.Schema(
                type=types.Type.NUMBER,
            ),
            "amount_paid": types.Schema(
                type=types.Type.NUMBER,
            ),
            "items": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "name": types.Schema(
                            type=types.Type.STRING,
                        ),
                        "price": types.Schema(
                            type=types.Type.NUMBER,
                        ),
                        "quantity": types.Schema(
                            type=types.Type.NUMBER,
                        ),
                    },
                    required=[
                        "name",
                        "price",
                        "quantity",
                    ],
                ),
            ),
        },
        required=[
            "items",
            "amount_paid",
            "tax_rate",
            "service_charge",
        ],
    ),
)


def get_bill_details_from_image(image_bytes: bytes, mime_type: str) -> str:
    """
    Use Gemini API to extract bill details from an image.

    :param image_bytes: The image bytes of the bill
    :return: Extracted bill details as an OCRBill object
    """
    client = Client(api_key=settings.GEMINI_API_KEY)

    model = "gemini-2.5-flash"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=BILL_OCR_PROMPT),
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
