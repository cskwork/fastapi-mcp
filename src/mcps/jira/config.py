"""JIRA MCP 설정"""

from typing import Dict, Any
from ...config.settings import settings


class JiraConfig:
    """JIRA 설정 관리자"""
    
    def __init__(self):
        if not settings.jira:
            raise ValueError("JIRA 설정이 활성화되지 않았습니다")
        
        self.base_url = settings.jira.base_url
        self.email = settings.jira.email
        self.api_token = settings.jira.api_token
        self.timeout = settings.jira.timeout
        self.max_retries = settings.jira.max_retries
    
    @property
    def auth_tuple(self) -> tuple:
        """인증 튜플 (email, api_token)"""
        return (self.email, self.api_token)
    
    @property
    def api_base_url(self) -> str:
        """API 베이스 URL"""
        return f"{self.base_url}/rest/api/3"
    
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
    
    def get_issue_url(self, issue_key: str = None) -> str:
        """이슈 API URL"""
        if issue_key:
            return f"{self.api_base_url}/issue/{issue_key}"
        return f"{self.api_base_url}/issue"
    
    def get_project_url(self, project_key: str = None) -> str:
        """프로젝트 API URL"""
        if project_key:
            return f"{self.api_base_url}/project/{project_key}"
        return f"{self.api_base_url}/project"
    
    def get_user_url(self, account_id: str = None) -> str:
        """사용자 API URL"""
        if account_id:
            return f"{self.api_base_url}/user?accountId={account_id}"
        return f"{self.api_base_url}/user/search"
    
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
            "api_base_url": self.api_base_url
        }


# 전역 설정 인스턴스
try:
    jira_config = JiraConfig()
except ValueError:
    jira_config = None