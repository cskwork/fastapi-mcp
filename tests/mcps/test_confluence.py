"""Confluence MCP 테스트"""

import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient


@pytest.fixture
def mock_confluence_client():
    """Confluence 클라이언트 모킹"""
    with patch("src.mcps.confluence.router.get_confluence_client") as mock:
        client = AsyncMock()
        mock.return_value = client
        yield client


def test_confluence_search_endpoint(client: TestClient, mock_confluence_client):
    """Confluence 검색 엔드포인트 테스트"""
    # Mock 응답 설정
    from src.mcps.confluence.models import ConfluenceSearchResult, ConfluenceContent
    
    mock_confluence_client.search.return_value = ConfluenceSearchResult(
        results=[
            ConfluenceContent(
                id="123",
                title="Test Page",
                type="page",
                status="current"
            )
        ],
        start=0,
        limit=25,
        size=1
    )
    
    # 요청 실행
    response = client.get("/confluence/search?q=type=page")
    
    # 검증
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert len(data["data"]["results"]) == 1


def test_confluence_page_endpoint(client: TestClient, mock_confluence_client):
    """Confluence 페이지 엔드포인트 테스트"""
    # Mock 응답 설정
    from src.mcps.confluence.models import ConfluenceContent
    
    mock_confluence_client.get_page.return_value = ConfluenceContent(
        id="123",
        title="Test Page",
        type="page",
        status="current"
    )
    
    # 요청 실행
    response = client.get("/confluence/page?page_id=123")
    
    # 검증
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["title"] == "Test Page"


def test_confluence_health_endpoint(client: TestClient, mock_confluence_client):
    """Confluence 헬스체크 엔드포인트 테스트"""
    # Mock 응답 설정
    mock_confluence_client.health_check.return_value = {
        "status": "healthy",
        "response_time_ms": 100.0,
        "stats": {
            "total_requests": 10,
            "successful_requests": 9,
            "failed_requests": 1
        }
    }
    
    # 요청 실행
    response = client.get("/confluence/health")
    
    # 검증
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["status"] == "healthy"


def test_confluence_invalid_cql(client: TestClient, mock_confluence_client):
    """잘못된 CQL 쿼리 테스트"""
    # 요청 실행 (위험한 패턴 포함)
    response = client.get("/confluence/search?q=user.accountid")
    
    # 검증 (400 오류 예상)
    assert response.status_code == 400