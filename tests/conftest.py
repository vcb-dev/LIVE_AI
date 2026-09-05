import os

import pytest

os.environ.setdefault("DEEPSEEK_API_KEY", "test-deepseek-key")
os.environ.setdefault("AI_SERVICE_API_KEY", "test-service-key")

@pytest.fixture
def api_key() -> str:
    return "test-service-key"
