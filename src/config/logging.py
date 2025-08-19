"""로깅 설정"""

import logging
import sys
from typing import Dict, Any
import structlog
from pydantic import BaseModel


class LogConfig(BaseModel):
    """로그 설정 모델"""
    
    level: str = "INFO"
    format: str = "json"  # json 또는 text
    

def setup_logging(config: LogConfig) -> None:
    """구조화된 로깅 설정"""
    
    # 기본 로깅 레벨 설정
    logging.basicConfig(
        level=getattr(logging, config.level.upper()),
        stream=sys.stdout,
        format="%(message)s"
    )
    
    # structlog 프로세서 설정
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]
    
    # 출력 형식에 따른 렌더러 선택
    if config.format.lower() == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer(colors=True))
    
    # structlog 설정
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        context_class=dict,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = None) -> structlog.stdlib.BoundLogger:
    """구조화된 로거 인스턴스 반환"""
    return structlog.get_logger(name)


def log_request_response(
    method: str,
    url: str,
    status_code: int = None,
    response_time: float = None,
    error: str = None,
    **kwargs
) -> None:
    """HTTP 요청/응답 로깅"""
    logger = get_logger("http")
    
    log_data = {
        "method": method,
        "url": url,
        "status_code": status_code,
        "response_time_ms": response_time * 1000 if response_time else None,
        **kwargs
    }
    
    if error:
        log_data["error"] = error
        logger.error("HTTP request failed", **log_data)
    else:
        logger.info("HTTP request completed", **log_data)


def log_mcp_operation(
    service: str,
    operation: str,
    success: bool = True,
    duration: float = None,
    error: str = None,
    **kwargs
) -> None:
    """MCP 작업 로깅"""
    logger = get_logger("mcp")
    
    log_data = {
        "service": service,
        "operation": operation,
        "success": success,
        "duration_ms": duration * 1000 if duration else None,
        **kwargs
    }
    
    if error:
        log_data["error"] = error
        logger.error("MCP operation failed", **log_data)
    else:
        logger.info("MCP operation completed", **log_data)