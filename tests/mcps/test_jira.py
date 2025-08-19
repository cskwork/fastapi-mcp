"""JIRA MCP 테스트"""

import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient


@pytest.fixture
def mock_jira_client():
    """JIRA 클라이언트 모킹"""
    with patch("src.mcps.jira.router.get_jira_client") as mock:
        client = AsyncMock()
        mock.return_value = client
        yield client


def test_jira_search_endpoint(client: TestClient, mock_jira_client):
    """JIRA 검색 엔드포인트 테스트"""
    # Mock 응답 설정
    from src.mcps.jira.models import JiraSearchResult, JiraIssue, JiraIssueFields, JiraIssueType, JiraStatus, JiraProject
    
    mock_jira_client.search_issues.return_value = JiraSearchResult(
        expand="",
        start_at=0,
        max_results=50,
        total=1,
        issues=[
            JiraIssue(
                id="123",
                key="TEST-123",
                self="https://test.atlassian.net/rest/api/3/issue/123",
                fields=JiraIssueFields(
                    summary="Test Issue",
                    issue_type=JiraIssueType(
                        id="1",
                        name="Task",
                        subtask=False
                    ),
                    status=JiraStatus(
                        id="1",
                        name="Open"
                    ),
                    project=JiraProject(
                        id="1",
                        key="TEST",
                        name="Test Project",
                        project_type_key="software"
                    )
                )
            )
        ]
    )
    
    # 요청 실행
    response = client.get("/jira/search?jql=project=TEST")
    
    # 검증
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert len(data["data"]["issues"]) == 1


def test_jira_issue_endpoint(client: TestClient, mock_jira_client):
    """JIRA 이슈 엔드포인트 테스트"""
    # Mock 응답 설정
    from src.mcps.jira.models import JiraIssue, JiraIssueFields, JiraIssueType, JiraStatus, JiraProject
    
    mock_jira_client.get_issue.return_value = JiraIssue(
        id="123",
        key="TEST-123",
        self="https://test.atlassian.net/rest/api/3/issue/123",
        fields=JiraIssueFields(
            summary="Test Issue",
            issue_type=JiraIssueType(
                id="1",
                name="Task",
                subtask=False
            ),
            status=JiraStatus(
                id="1",
                name="Open"
            ),
            project=JiraProject(
                id="1",
                key="TEST",
                name="Test Project",
                project_type_key="software"
            )
        )
    )
    
    # 요청 실행
    response = client.get("/jira/issue?issue_key=TEST-123")
    
    # 검증
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["key"] == "TEST-123"


def test_jira_health_endpoint(client: TestClient, mock_jira_client):
    """JIRA 헬스체크 엔드포인트 테스트"""
    # Mock 응답 설정
    mock_jira_client.health_check.return_value = {
        "status": "healthy",
        "response_time_ms": 150.0,
        "stats": {
            "total_requests": 5,
            "successful_requests": 5,
            "failed_requests": 0
        }
    }
    
    # 요청 실행
    response = client.get("/jira/health")
    
    # 검증
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["status"] == "healthy"


def test_jira_invalid_jql(client: TestClient, mock_jira_client):
    """잘못된 JQL 쿼리 테스트"""
    # 요청 실행 (위험한 패턴 포함)
    response = client.get("/jira/search?jql=delete+from+issues")
    
    # 검증 (400 오류 예상)
    assert response.status_code == 400