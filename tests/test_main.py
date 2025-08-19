"""메인 애플리케이션 테스트"""

import pytest
from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient):
    """루트 엔드포인트 테스트"""
    response = client.get("/")
    assert response.status_code == 200
    
    data = response.json()
    assert "service" in data
    assert "version" in data
    assert "environment" in data
    assert "enabled_services" in data
    assert "mcp_endpoint" in data


def test_health_endpoint(client: TestClient):
    """헬스체크 엔드포인트 테스트"""
    response = client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    assert "status" in data
    assert "version" in data
    assert "environment" in data
    assert "services" in data


@pytest.mark.asyncio
async def test_async_client(async_client):
    """비동기 클라이언트 테스트"""
    response = await async_client.get("/")
    assert response.status_code == 200
    
    data = response.json()
    assert "service" in data