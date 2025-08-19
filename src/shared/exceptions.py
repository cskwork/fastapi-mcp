"""커스텀 예외 클래스들"""

from typing import Optional, Dict, Any
from fastapi import HTTPException


class MCPBaseException(Exception):
    """MCP 기본 예외 클래스"""
    
    def __init__(
        self,
        message: str,
        service: str = None,
        operation: str = None,
        details: Dict[str, Any] = None
    ):
        self.message = message
        self.service = service
        self.operation = operation
        self.details = details or {}
        super().__init__(self.message)


class ServiceUnavailableError(MCPBaseException):
    """서비스 사용 불가 오류"""
    pass


class AuthenticationError(MCPBaseException):
    """인증 오류"""
    pass


class AuthorizationError(MCPBaseException):
    """인가 오류"""
    pass


class RateLimitError(MCPBaseException):
    """레이트 리미트 오류"""
    pass


class ValidationError(MCPBaseException):
    """입력 검증 오류"""
    pass


class ExternalAPIError(MCPBaseException):
    """외부 API 오류"""
    
    def __init__(
        self,
        message: str,
        status_code: int = None,
        response_data: Dict[str, Any] = None,
        **kwargs
    ):
        self.status_code = status_code
        self.response_data = response_data or {}
        super().__init__(message, **kwargs)


class ConfigurationError(MCPBaseException):
    """설정 오류"""
    pass


def create_http_exception(
    status_code: int,
    message: str,
    details: Dict[str, Any] = None
) -> HTTPException:
    """HTTP 예외 생성 헬퍼"""
    return HTTPException(
        status_code=status_code,
        detail={
            "message": message,
            "details": details or {}
        }
    )