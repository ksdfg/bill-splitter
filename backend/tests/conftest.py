import os

os.environ.setdefault("LITELLM_MODEL", "gemini/gemini-2.5-flash")
os.environ.setdefault("LITELLM_API_BASE", "https://proxy.clanker.ai")
os.environ.setdefault("LITELLM_API_KEY", "clanker123")


def pytest_configure(config):
    config.addinivalue_line("markers", "mock_llm_response(response): Set the mock LLM response for the test.")
