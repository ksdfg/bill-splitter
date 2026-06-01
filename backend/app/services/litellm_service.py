"""
LiteLLM service for multi-provider LLM calls.

This service provides a unified interface to multiple LLM providers (OpenAI, Anthropic, Google, etc.)
using LiteLLM. It supports custom proxy endpoints via LITELLM_API_BASE.
"""

import base64

from litellm import completion

from app.core.settings import settings
from app.schemas.bill import OCRBill

BILL_OCR_PROMPT = """
You are an expert at extracting information from bills and receipts.
Your task is to analyze the provided image of a bill and extract the following information in JSON format:

Extract a Bill object with the following structure:
- items: A list of items, where each item contains:
  - name: The name of the item (string, non-empty)
  - price: The price of the item (float, must be positive)
  - quantity: The quantity ordered (integer, must be positive, at least 1)
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


def get_bill_details_from_image(image_bytes: bytes, mime_type: str) -> str:
    """
    Use LiteLLM to extract bill details from an image.

    Supports multiple LLM providers via a unified interface. Can be configured
    to use a custom proxy endpoint via LITELLM_API_BASE.

    :param image_bytes: The image bytes of the bill
    :param mime_type: The MIME type of the image (e.g., "image/jpeg")
    :return: Extracted bill details as a JSON string
    """
    # Encode image to base64 data URL
    base64_image = base64.b64encode(image_bytes).decode("utf-8")
    image_url = f"data:{mime_type};base64,{base64_image}"

    # Build message with vision content
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": BILL_OCR_PROMPT},
                {
                    "type": "image_url",
                    "image_url": {"url": image_url},
                },
            ],
        }
    ]

    # Build completion kwargs
    kwargs: dict = {
        "model": settings.LITELLM_MODEL,
        "messages": messages,
        "response_format": OCRBill,
        "api_base": settings.LITELLM_API_BASE,
        "api_key": settings.LITELLM_API_KEY,
    }

    response = completion(**kwargs)

    if not response.choices or len(response.choices) == 0:
        raise ValueError("No response from LiteLLM")

    content = response.choices[0].message.content
    if content is None:
        raise ValueError("No content in LiteLLM response")

    return content
