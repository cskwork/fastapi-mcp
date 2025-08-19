"""Slack MCP 테스트"""

import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient


@pytest.fixture
def mock_slack_client():
    """Slack 클라이언트 모킹"""
    with patch("src.mcps.slack.router.get_slack_client") as mock:
        client = AsyncMock()
        mock.return_value = client
        yield client


def test_slack_channel_info_endpoint(client: TestClient, mock_slack_client):
    """Slack 채널 정보 엔드포인트 테스트"""
    # Mock 응답 설정
    from src.mcps.slack.models import SlackChannelInfo, SlackChannel
    
    mock_slack_client.get_channel_info.return_value = SlackChannelInfo(
        ok=True,
        channel=SlackChannel(
            id="C1234567890",
            name="general",
            is_channel=True,
            is_group=False,
            is_im=False,
            is_private=False,
            is_archived=False,
            is_general=True
        )
    )
    
    # 요청 실행
    response = client.get("/slack/channel/info?channel=general")
    
    # 검증
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["channel"]["name"] == "general"


def test_slack_channel_history_endpoint(client: TestClient, mock_slack_client):
    """Slack 채널 히스토리 엔드포인트 테스트"""
    # Mock 응답 설정
    from src.mcps.slack.models import SlackConversationHistory, SlackMessage
    
    mock_slack_client.get_conversation_history.return_value = SlackConversationHistory(
        ok=True,
        messages=[
            SlackMessage(
                type="message",
                text="Hello world!",
                user="U1234567890",
                ts="1234567890.123456"
            )
        ],
        has_more=False
    )
    
    # 요청 실행
    response = client.get("/slack/channel/history?channel=general&limit=10")
    
    # 검증
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]["messages"]) == 1
    assert data["data"]["messages"][0]["text"] == "Hello world!"


def test_slack_send_message_endpoint(client: TestClient, mock_slack_client):
    """Slack 메시지 전송 엔드포인트 테스트"""
    # Mock 응답 설정
    from src.mcps.slack.models import SlackPostMessageResponse, SlackMessage
    
    mock_slack_client.post_message.return_value = SlackPostMessageResponse(
        ok=True,
        channel="C1234567890",
        ts="1234567890.123456",
        message=SlackMessage(
            type="message",
            text="Test message",
            user="U0987654321",
            ts="1234567890.123456"
        )
    )
    
    # 요청 실행
    response = client.post("/slack/message/send", json={
        "channel": "general",
        "text": "Test message"
    })
    
    # 검증
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["ok"] is True
    assert data["data"]["message"]["text"] == "Test message"


def test_slack_user_info_endpoint(client: TestClient, mock_slack_client):
    """Slack 사용자 정보 엔드포인트 테스트"""
    # Mock 응답 설정
    from src.mcps.slack.models import SlackUserInfo, SlackUser
    
    mock_slack_client.get_user_info.return_value = SlackUserInfo(
        ok=True,
        user=SlackUser(
            id="U1234567890",
            name="testuser",
            real_name="Test User",
            email="test@example.com",
            is_bot=False,
            is_admin=False,
            is_deleted=False
        )
    )
    
    # 요청 실행
    response = client.get("/slack/user/info?user_id=U1234567890")
    
    # 검증
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["user"]["name"] == "testuser"


def test_slack_health_endpoint(client: TestClient, mock_slack_client):
    """Slack 헬스체크 엔드포인트 테스트"""
    # Mock 응답 설정
    mock_slack_client.health_check.return_value = {
        "status": "healthy",
        "response_time_ms": 200.0,
        "team": "Test Team",
        "user": "testbot",
        "stats": {
            "total_requests": 15,
            "successful_requests": 14,
            "failed_requests": 1,
            "messages_sent": 5
        }
    }
    
    # 요청 실행
    response = client.get("/slack/health")
    
    # 검증
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["status"] == "healthy"


def test_slack_invalid_channel(client: TestClient, mock_slack_client):
    """잘못된 채널 정보 테스트"""
    # 요청 실행 (빈 채널)
    response = client.get("/slack/channel/info?channel=")
    
    # 검증 (422 Validation Error 예상)
    assert response.status_code == 422