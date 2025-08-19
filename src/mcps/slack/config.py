"""Slack MCP 설정"""

from typing import Dict, Any
from ...config.settings import settings


class SlackConfig:
    """Slack 설정 관리자"""
    
    def __init__(self):
        if not settings.slack:
            raise ValueError("Slack 설정이 활성화되지 않았습니다")
        
        self.bot_token = settings.slack.bot_token
        self.app_token = settings.slack.app_token
        self.signing_secret = settings.slack.signing_secret
        self.timeout = settings.slack.timeout
        self.max_retries = settings.slack.max_retries
    
    @property
    def auth_headers(self) -> Dict[str, str]:
        """인증 헤더"""
        return {
            "Authorization": f"Bearer {self.bot_token}",
            "Content-Type": "application/json"
        }
    
    @property
    def api_base_url(self) -> str:
        """Slack API 베이스 URL"""
        return "https://slack.com/api"
    
    def get_conversations_info_url(self) -> str:
        """채널 정보 조회 API URL"""
        return f"{self.api_base_url}/conversations.info"
    
    def get_conversations_history_url(self) -> str:
        """채널 히스토리 조회 API URL"""
        return f"{self.api_base_url}/conversations.history"
    
    def get_chat_post_message_url(self) -> str:
        """메시지 전송 API URL"""
        return f"{self.api_base_url}/chat.postMessage"
    
    def get_users_info_url(self) -> str:
        """사용자 정보 조회 API URL"""
        return f"{self.api_base_url}/users.info"
    
    def get_users_list_url(self) -> str:
        """사용자 목록 조회 API URL"""
        return f"{self.api_base_url}/users.list"
    
    def get_conversations_list_url(self) -> str:
        """채널 목록 조회 API URL"""
        return f"{self.api_base_url}/conversations.list"
    
    def get_auth_test_url(self) -> str:
        """인증 테스트 API URL"""
        return f"{self.api_base_url}/auth.test"
    
    def validate_config(self) -> bool:
        """설정 유효성 검증"""
        required_fields = [
            self.bot_token,
            self.signing_secret
        ]
        
        if not all(required_fields):
            return False
        
        # 토큰 형식 기본 검증
        if not self.bot_token.startswith("xoxb-"):
            return False
        
        if self.app_token and not self.app_token.startswith("xapp-"):
            return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """설정을 딕셔너리로 변환 (민감한 정보 제외)"""
        return {
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "api_base_url": self.api_base_url,
            "bot_token_prefix": self.bot_token[:10] + "..." if self.bot_token else None,
            "app_token_configured": bool(self.app_token),
            "signing_secret_configured": bool(self.signing_secret)
        }


# 전역 설정 인스턴스
try:
    slack_config = SlackConfig()
except ValueError:
    slack_config = None