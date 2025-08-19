"""Confluence MCP 설정"""

from typing import Dict, Any
from ...config.settings import settings


class ConfluenceConfig:
    """Confluence 설정 관리자"""
    
    def __init__(self):
        if not settings.confluence:
            raise ValueError("Confluence 설정이 활성화되지 않았습니다")
        
        self.base_url = settings.confluence.base_url
        self.email = settings.confluence.email
        self.api_token = settings.confluence.api_token
        self.timeout = settings.confluence.timeout
        self.max_retries = settings.confluence.max_retries
        self.retry_delay = settings.confluence.retry_delay
        self.max_results = settings.confluence.max_results
        self.default_expand = settings.confluence.default_expand
    
    @property
    def auth_tuple(self) -> tuple:
        """인증 튜플 (email, api_token)"""
        return (self.email, self.api_token)
    
    @property
    def api_base_url(self) -> str:
        """API 베이스 URL"""
        return f"{self.base_url}/wiki/rest/api"
    
    @property
    def headers(self) -> Dict[str, str]:
        """기본 HTTP 헤더"""
        return {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    
    def get_search_url(self) -> str:
        """검색 API URL"""
        return f"{self.api_base_url}/search"
    
    def get_content_url(self, content_id: str = None) -> str:
        """콘텐츠 API URL"""
        if content_id:
            return f"{self.api_base_url}/content/{content_id}"
        return f"{self.api_base_url}/content"
    
    def get_space_url(self, space_key: str = None) -> str:
        """스페이스 API URL"""
        if space_key:
            return f"{self.api_base_url}/space/{space_key}"
        return f"{self.api_base_url}/space"
    
    def get_user_url(self, account_id: str = None) -> str:
        """사용자 API URL"""
        if account_id:
            return f"{self.api_base_url}/user?accountId={account_id}"
        return f"{self.api_base_url}/user"
    
    def validate_config(self) -> bool:
        """설정 유효성 검증"""
        required_fields = [
            self.base_url,
            self.email, 
            self.api_token
        ]
        
        if not all(required_fields):
            return False
        
        if not self.base_url.startswith(("http://", "https://")):
            return False
        
        if "@" not in self.email:
            return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """설정을 딕셔너리로 변환 (민감한 정보 제외)"""
        return {
            "base_url": self.base_url,
            "email": self.email,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay,
            "max_results": self.max_results,
            "default_expand": self.default_expand,
            "api_base_url": self.api_base_url
        }


# 전역 설정 인스턴스
try:
    confluence_config = ConfluenceConfig()
except ValueError:
    confluence_config = None