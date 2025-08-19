"""공통 미들웨어"""

import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

from .models import LogEntry

logger = structlog.get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """요청/응답 로깅 미들웨어"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 요청 시작 시간 및 고유 ID 생성
        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        # 요청 정보 로깅
        logger.info(
            "Request started",
            request_id=request_id,
            method=request.method,
            url=str(request.url),
            user_agent=request.headers.get("user-agent"),
            client_ip=self._get_client_ip(request)
        )
        
        # 요청 처리
        try:
            response = await call_next(request)
            duration = time.time() - start_time
            
            # 성공 응답 로깅
            logger.info(
                "Request completed",
                request_id=request_id,
                method=request.method,
                url=str(request.url),
                status_code=response.status_code,
                duration_ms=duration * 1000
            )
            
            # 응답 헤더에 요청 ID 추가
            response.headers["X-Request-ID"] = request_id
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            
            # 오류 응답 로깅
            logger.error(
                "Request failed",
                request_id=request_id,
                method=request.method,
                url=str(request.url),
                error=str(e),
                duration_ms=duration * 1000
            )
            raise
    
    def _get_client_ip(self, request: Request) -> str:
        """클라이언트 IP 주소 추출"""
        # X-Forwarded-For 헤더 확인 (프록시/로드밸런서 환경)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        # X-Real-IP 헤더 확인
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # 직접 연결된 클라이언트 IP
        return request.client.host if request.client else "unknown"


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """전역 오류 처리 미들웨어"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)
        except Exception as e:
            logger.error(
                "Unhandled exception",
                method=request.method,
                url=str(request.url),
                error=str(e),
                error_type=type(e).__name__
            )
            
            # 프로덕션에서는 상세 오류 정보 숨김
            from ..config.settings import settings
            
            if settings.app.debug:
                error_detail = str(e)
            else:
                error_detail = "Internal server error"
            
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": error_detail,
                    "error_type": type(e).__name__
                }
            )


class RateLimitMiddleware(BaseHTTPMiddleware):
    """레이트 리미팅 미들웨어 (간단한 구현)"""
    
    def __init__(self, app, max_requests: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}  # 실제 환경에서는 Redis 사용 권장
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        client_ip = self._get_client_ip(request)
        current_time = time.time()
        
        # 클라이언트별 요청 기록 정리 (만료된 기록 제거)
        if client_ip in self.requests:
            self.requests[client_ip] = [
                req_time for req_time in self.requests[client_ip]
                if current_time - req_time < self.window_seconds
            ]
        else:
            self.requests[client_ip] = []
        
        # 레이트 리미트 체크
        if len(self.requests[client_ip]) >= self.max_requests:
            logger.warning(
                "Rate limit exceeded",
                client_ip=client_ip,
                requests_count=len(self.requests[client_ip]),
                max_requests=self.max_requests
            )
            
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "message": "Rate limit exceeded",
                    "retry_after": self.window_seconds
                },
                headers={"Retry-After": str(self.window_seconds)}
            )
        
        # 현재 요청 기록
        self.requests[client_ip].append(current_time)
        
        return await call_next(request)
    
    def _get_client_ip(self, request: Request) -> str:
        """클라이언트 IP 주소 추출"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """보안 헤더 추가 미들웨어"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # 보안 헤더 추가
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # HSTS (HTTPS 환경에서만)
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response