"""테스트 설정 및 픽스처"""

import pytest
import asyncio
from typing import Generator, AsyncGenerator
from fastapi.testclient import TestClient
from httpx import AsyncClient

from src.main import app


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """테스트 세션용 이벤트 루프"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """FastAPI 테스트 클라이언트"""
    with TestClient(app) as c:
        yield c


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """비동기 HTTP 클라이언트"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    """환경변수 모킹 - 모든 테스트에 자동 적용"""
    env_vars = {
        "SECRET_KEY": "test-secret-key",
        "MCP_ENABLED_SERVICES": "confluence,jira,slack",
        "CONFLUENCE_BASE_URL": "https://test.atlassian.net",
        "CONFLUENCE_EMAIL": "test@example.com",
        "CONFLUENCE_API_TOKEN": "test-token",
        "JIRA_BASE_URL": "https://test.atlassian.net",
        "JIRA_EMAIL": "test@example.com",
        "JIRA_API_TOKEN": "test-token",
        "SLACK_BOT_TOKEN": "xoxb-test-token",
        "SLACK_SIGNING_SECRET": "test-secret",
    }
    
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)
    
    return env_vars