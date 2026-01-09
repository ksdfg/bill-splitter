def pytest_configure(config):
    config.addinivalue_line("markers", "mock_llm_response(response): Set the mock Gemini LLM response for the test.")
