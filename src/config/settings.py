"""환경별 설정 관리"""

import os
from typing import Dict, List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class BaseConfig(BaseSettings):
    """기본 설정 클래스"""
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"
    }


class AppSettings(BaseConfig):
    """애플리케이션 설정"""
    
    app_name: str = Field(default="AIDT MCP Server", description="애플리케이션 이름")
    debug: bool = Field(default=False, description="디버그 모드")
    version: str = Field(default="0.1.0", description="애플리케이션 버전")
    environment: str = Field(default="development", description="실행 환경")
    
    # 서버 설정
    host: str = Field(default="127.0.0.1", description="서버 호스트")
    port: int = Field(default=8000, description="서버 포트")
    workers: int = Field(default=1, description="워커 프로세스 수")
    
    # MCP 설정
    mcp_enabled_services: str = Field(
        default="calculator", 
        description="활성화된 MCP 서비스 목록 (콤마로 구분)"
    )
    mcp_mount_path: str = Field(default="/mcp", description="MCP 마운트 경로")
    
    # 로깅 설정
    log_level: str = Field(default="INFO", description="로그 레벨")
    log_format: str = Field(default="json", description="로그 포맷 (json/text)")
    
    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v):
        allowed = ["development", "staging", "production", "test"]
        if v.lower() not in allowed:
            raise ValueError(f"환경은 {allowed} 중 하나여야 합니다")
        return v.lower()
    
    def get_enabled_services(self) -> List[str]:
        """활성화된 서비스 목록을 리스트로 반환"""
        if isinstance(self.mcp_enabled_services, str):
            return [s.strip() for s in self.mcp_enabled_services.split(",") if s.strip()]
        return self.mcp_enabled_services or []


class SecuritySettings(BaseConfig):
    """보안 설정"""
    
    secret_key: str = Field(..., description="JWT 시크릿 키")
    algorithm: str = Field(default="HS256", description="JWT 알고리즘")
    access_token_expire_minutes: int = Field(default=30, description="액세스 토큰 만료 시간(분)")
    
    # CORS 설정
    cors_origins: List[str] = Field(default=["*"], description="CORS 허용 오리진")
    cors_methods: List[str] = Field(default=["*"], description="CORS 허용 메서드")
    cors_headers: List[str] = Field(default=["*"], description="CORS 허용 헤더")
    
    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [s.strip() for s in v.split(",") if s.strip()]
        return v or ["*"]


class ConfluenceSettings(BaseConfig):
    """Confluence 설정"""
    
    base_url: str = Field(..., env="CONFLUENCE_BASE_URL", description="Confluence 베이스 URL")
    email: str = Field(..., env="CONFLUENCE_EMAIL", description="Confluence 이메일")
    api_token: str = Field(..., env="CONFLUENCE_API_TOKEN", description="Confluence API 토큰")
    
    # 연결 설정
    timeout: float = Field(default=10.0, description="요청 타임아웃(초)")
    max_retries: int = Field(default=3, description="최대 재시도 횟수")
    retry_delay: float = Field(default=1.0, description="재시도 지연(초)")
    
    # 검색 설정
    max_results: int = Field(default=100, description="최대 검색 결과 수")
    default_expand: str = Field(default="body.storage,version", description="기본 확장 필드")
    
    @field_validator("base_url")
    @classmethod
    def validate_base_url(cls, v):
        return v.rstrip("/") if v else v


class JiraSettings(BaseConfig):
    """JIRA 설정"""
    
    base_url: str = Field(..., env="JIRA_BASE_URL", description="JIRA 베이스 URL")
    email: str = Field(..., env="JIRA_EMAIL", description="JIRA 이메일")
    api_token: str = Field(..., env="JIRA_API_TOKEN", description="JIRA API 토큰")
    
    timeout: float = Field(default=10.0, description="요청 타임아웃(초)")
    max_retries: int = Field(default=3, description="최대 재시도 횟수")
    
    @field_validator("base_url")
    @classmethod
    def validate_base_url(cls, v):
        return v.rstrip("/") if v else v


class SlackSettings(BaseConfig):
    """Slack 설정"""
    
    bot_token: str = Field(..., env="SLACK_BOT_TOKEN", description="Slack 봇 토큰")
    app_token: str = Field(..., env="SLACK_APP_TOKEN", description="Slack 앱 토큰")
    signing_secret: str = Field(..., env="SLACK_SIGNING_SECRET", description="Slack 서명 시크릿")
    
    timeout: float = Field(default=10.0, description="요청 타임아웃(초)")
    max_retries: int = Field(default=3, description="최대 재시도 횟수")


class DatabaseSettings(BaseConfig):
    """데이터베이스 설정 (필요시)"""
    
    redis_url: Optional[str] = Field(None, env="REDIS_URL", description="Redis URL")
    redis_password: Optional[str] = Field(None, env="REDIS_PASSWORD", description="Redis 비밀번호")
    redis_db: int = Field(default=0, description="Redis DB 번호")


class Settings:
    """통합 설정 클래스"""
    
    def __init__(self):
        self.app = AppSettings()
        self.security = SecuritySettings()
        self.confluence = ConfluenceSettings() if self._is_service_enabled("confluence") else None
        self.jira = JiraSettings() if self._is_service_enabled("jira") else None
        self.slack = SlackSettings() if self._is_service_enabled("slack") else None
        # Calculator는 외부 설정이 필요없으므로 항상 활성화 가능
        self.calculator = True if self._is_service_enabled("calculator") else False
        self.database = DatabaseSettings()
    
    def _is_service_enabled(self, service: str) -> bool:
        """서비스가 활성화되어 있는지 확인"""
        return service in self.app.get_enabled_services()
    
    def get_service_configs(self) -> Dict[str, BaseConfig]:
        """활성화된 서비스 설정들을 반환"""
        configs = {}
        if self.confluence:
            configs["confluence"] = self.confluence
        if self.jira:
            configs["jira"] = self.jira
        if self.slack:
            configs["slack"] = self.slack
        return configs


# 전역 설정 인스턴스
settings = Settings()