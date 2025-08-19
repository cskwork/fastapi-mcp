"""공통 유틸리티 함수들"""

import asyncio
import time
from typing import Any, Callable, TypeVar, Dict, List
from functools import wraps
import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)
import structlog

from .exceptions import ExternalAPIError, RateLimitError

T = TypeVar("T")
logger = structlog.get_logger(__name__)


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """입력값 정리 및 검증"""
    if not isinstance(text, str):
        raise ValueError("입력값은 문자열이어야 합니다")
    
    # 기본 정리
    sanitized = text.strip()
    
    # 길이 제한
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    # 위험한 문자 제거 (기본적인 XSS 방지)
    dangerous_chars = ["<script", "</script", "javascript:", "on="]
    for char in dangerous_chars:
        if char.lower() in sanitized.lower():
            raise ValueError(f"위험한 문자가 포함되어 있습니다: {char}")
    
    return sanitized


def validate_cql_query(query: str) -> str:
    """CQL 쿼리 검증 (Confluence용)"""
    query = sanitize_input(query)
    
    # 허용된 키워드만 확인 (실제 환경에서는 더 정교한 파싱 필요)
    allowed_keywords = [
        "type", "title", "space", "creator", "lastmodified",
        "and", "or", "not", "=", "~", "<", ">", "(", ")", 
        "label", "ancestor", "parent", "content"
    ]
    
    # 금지된 패턴 검사
    forbidden_patterns = [
        "user.", "accountid", "script", ";", "--", "/*", "*/",
        "drop", "delete", "update", "insert", "create", "alter"
    ]
    
    query_lower = query.lower()
    for pattern in forbidden_patterns:
        if pattern in query_lower:
            raise ValueError(f"금지된 패턴이 포함되어 있습니다: {pattern}")
    
    return query


def create_retry_decorator(
    max_attempts: int = 3,
    wait_min: float = 1.0,
    wait_max: float = 10.0,
    retry_exceptions: tuple = (httpx.HTTPStatusError, httpx.RequestError)
):
    """재시도 데코레이터 생성"""
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=wait_min, max=wait_max),
        retry=retry_if_exception_type(retry_exceptions),
        before_sleep=before_sleep_log(logger, "WARNING"),
        reraise=True
    )


async def retry_with_backoff(
    client: httpx.AsyncClient,
    method: str,
    url: str,
    max_retries: int = 3,
    **kwargs
) -> httpx.Response:
    """HTTP 요청 재시도 with 지수 백오프"""
    
    for attempt in range(max_retries):
        try:
            response = await client.request(method, url, **kwargs)
            
            # 4xx 오류는 재시도하지 않음 (401, 403 등)
            if 400 <= response.status_code < 500 and response.status_code != 429:
                response.raise_for_status()
                return response
            
            # 5xx 또는 429는 재시도 대상
            if response.status_code in (429, 502, 503, 504) or response.status_code >= 500:
                if attempt == max_retries - 1:
                    response.raise_for_status()
                
                wait_time = (2 ** attempt) * 0.5
                logger.warning(
                    "HTTP request failed, retrying",
                    attempt=attempt + 1,
                    status_code=response.status_code,
                    wait_time=wait_time,
                    url=url
                )
                await asyncio.sleep(wait_time)
                continue
            
            response.raise_for_status()
            return response
            
        except httpx.RequestError as e:
            if attempt == max_retries - 1:
                logger.error("HTTP request failed after all retries", error=str(e), url=url)
                raise ExternalAPIError(f"요청 실패: {str(e)}", details={"url": url})
            
            wait_time = (2 ** attempt) * 0.5
            logger.warning(
                "HTTP request error, retrying",
                attempt=attempt + 1,
                error=str(e),
                wait_time=wait_time,
                url=url
            )
            await asyncio.sleep(wait_time)
    
    raise ExternalAPIError("최대 재시도 횟수 초과", details={"url": url, "max_retries": max_retries})


def measure_time(func: Callable[..., T]) -> Callable[..., T]:
    """함수 실행 시간 측정 데코레이터"""
    
    @wraps(func)
    async def async_wrapper(*args, **kwargs) -> T:
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start_time
            logger.info(
                "Function executed",
                function=func.__name__,
                duration_ms=duration * 1000,
                success=True
            )
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                "Function failed",
                function=func.__name__,
                duration_ms=duration * 1000,
                error=str(e),
                success=False
            )
            raise
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs) -> T:
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            logger.info(
                "Function executed",
                function=func.__name__,
                duration_ms=duration * 1000,
                success=True
            )
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                "Function failed",
                function=func.__name__,
                duration_ms=duration * 1000,
                error=str(e),
                success=False
            )
            raise
    
    return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper


def parse_comma_separated(value: str) -> List[str]:
    """콤마로 구분된 문자열을 리스트로 파싱"""
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def format_error_response(
    error: Exception,
    service: str = None,
    operation: str = None
) -> Dict[str, Any]:
    """오류 응답 포맷팅"""
    error_data = {
        "error": True,
        "message": str(error),
        "type": type(error).__name__
    }
    
    if service:
        error_data["service"] = service
    
    if operation:
        error_data["operation"] = operation
    
    if hasattr(error, "details"):
        error_data["details"] = error.details
    
    if hasattr(error, "status_code"):
        error_data["status_code"] = error.status_code
    
    return error_data


def create_success_response(
    data: Any = None,
    message: str = "성공",
    metadata: Dict[str, Any] = None
) -> Dict[str, Any]:
    """성공 응답 생성"""
    response = {
        "success": True,
        "message": message
    }
    
    if data is not None:
        response["data"] = data
    
    if metadata:
        response["metadata"] = metadata
    
    return response