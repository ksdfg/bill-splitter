"""
LiteLLM service for multi-provider LLM calls.

This service provides a unified interface to multiple LLM providers (OpenAI, Anthropic, xAI, etc.)
using LiteLLM. It supports custom proxy endpoints via LITELLM_API_BASE.
"""

import base64

from litellm import completion

from app.core.settings import settings

# JSON schema for bill OCR response
BILL_OCR_JSON_SCHEMA = {
    "type": "json_schema",
    "json_schema": {
        "name": "bill_ocr",
        "schema": {
            "type": "object",
            "properties": {
                "tax_rate": {"type": "number"},
                "service_charge": {"type": "number"},
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "price": {"type": "number"},
                            "quantity": {"type": "number"},
                        },
                        "required": ["name", "price", "quantity"],
                    },
                },
            },
            "required": ["tax_rate", "service_charge", "items"],
        },
    },
}


def generate_content_from_image(prompt: str, image_bytes: bytes, mime_type: str) -> str:
    """
    Use LiteLLM to extract bill details from an image.

    Supports multiple LLM providers via a unified interface. Can be configured
    to use a custom proxy endpoint via LITELLM_API_BASE.

    :param prompt: The prompt describing what to extract
    :param image_bytes: The image bytes of the bill
    :param mime_type: The MIME type of the image (e.g., "image/jpeg")
    :return: Extracted bill details as a JSON string
    """
    if not settings.LITELLM_MODEL:
        raise ValueError("LITELLM_MODEL is not set in settings")

    # Encode image to base64 data URL
    base64_image = base64.b64encode(image_bytes).decode("utf-8")
    image_url = f"data:{mime_type};base64,{base64_image}"

    # Build message with vision content
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": image_url, "format": mime_type},
                },
            ],
        }
    ]

    # Build completion kwargs
    kwargs = {
        "model": settings.LITELLM_MODEL,
        "messages": messages,
        "response_format": BILL_OCR_JSON_SCHEMA,
    }

    # Add optional proxy configuration
    if settings.LITELLM_API_BASE:
        kwargs["api_base"] = settings.LITELLM_API_BASE
    if settings.LITELLM_API_KEY:
        kwargs["api_key"] = settings.LITELLM_API_KEY

    response = completion(**kwargs)

    if not response.choices or len(response.choices) == 0:
        raise ValueError("No response from LiteLLM")

    content = response.choices[0].message.content
    if content is None:
        raise ValueError("No content in LiteLLM response")

    return content
