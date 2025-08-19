"""AIDT MCP FastAPI 메인 애플리케이션"""

import asyncio
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi_mcp import FastApiMCP
import structlog

from .config.settings import settings
from .config.logging import setup_logging, LogConfig
from .shared.middleware import (
    RequestLoggingMiddleware,
    ErrorHandlingMiddleware,
    SecurityHeadersMiddleware,
    RateLimitMiddleware
)
from .shared.models import HealthCheckResponse, ServiceStatus
from .shared.exceptions import MCPBaseException

# 로깅 설정
setup_logging(LogConfig(
    level=settings.app.log_level,
    format=settings.app.log_format
))

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    logger.info("AIDT MCP Server starting up", version=settings.app.version)
    
    # 서비스별 HTTP 클라이언트 초기화
    await _initialize_services()
    
    yield
    
    logger.info("AIDT MCP Server shutting down")
    
    # 서비스별 리소스 정리
    await _cleanup_services()


async def _initialize_services():
    """서비스별 초기화"""
    enabled_services = settings.app.get_enabled_services()
    logger.info("Initializing services", enabled_services=enabled_services)
    
    # 활성화된 서비스별 클라이언트 초기화
    for service_name in enabled_services:
        try:
            if service_name == "confluence" and settings.confluence:
                from .mcps.confluence.client import get_confluence_client
                client = await get_confluence_client()
                app.state.confluence_client = client
                logger.info("Confluence client initialized")
                
            elif service_name == "jira" and settings.jira:
                from .mcps.jira.client import get_jira_client
                client = await get_jira_client()
                app.state.jira_client = client
                logger.info("JIRA client initialized")
                
            elif service_name == "slack" and settings.slack:
                from .mcps.slack.client import get_slack_client
                client = await get_slack_client()
                app.state.slack_client = client
                logger.info("Slack client initialized")
                
            elif service_name == "calculator":
                from .mcps.calculator.client import initialize_calculator_client
                client = await initialize_calculator_client()
                app.state.calculator_client = client
                logger.info("Calculator client initialized")
                
        except Exception as e:
            logger.error(f"Failed to initialize {service_name} service", error=str(e))
            # 개별 서비스 초기화 실패는 전체 시스템을 중단시키지 않음


async def _cleanup_services():
    """서비스별 정리"""
    logger.info("Cleaning up services")
    
    # HTTP 클라이언트 정리
    if hasattr(app.state, "confluence_client"):
        await app.state.confluence_client.aclose()
        logger.info("Confluence client closed")
    
    if hasattr(app.state, "jira_client"):
        await app.state.jira_client.aclose()
        logger.info("JIRA client closed")
    
    if hasattr(app.state, "slack_client"):
        await app.state.slack_client.aclose()
        logger.info("Slack client closed")
    
    # Calculator는 HTTP 클라이언트가 아니므로 별도 정리 불필요
    if hasattr(app.state, "calculator_client"):
        logger.info("Calculator client cleaned up")


# FastAPI 애플리케이션 생성
app = FastAPI(
    title=settings.app.app_name,
    version=settings.app.version,
    description="AIDT MCP FastAPI 멀티서버 플랫폼",
    debug=settings.app.debug,
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.security.cors_origins,
    allow_credentials=True,
    allow_methods=settings.security.cors_methods,
    allow_headers=settings.security.cors_headers,
)

# 미들웨어 추가 (순서 중요!)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(ErrorHandlingMiddleware)

# 레이트 리미팅 (개발환경에서는 제한적으로 적용)
if settings.app.environment != "development":
    app.add_middleware(RateLimitMiddleware, max_requests=100, window_seconds=60)


# 전역 예외 처리기
@app.exception_handler(MCPBaseException)
async def mcp_exception_handler(request, exc: MCPBaseException):
    """MCP 커스텀 예외 처리"""
    logger.error(
        "MCP exception occurred",
        service=exc.service,
        operation=exc.operation,
        error=exc.message,
        details=exc.details
    )
    
    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "message": exc.message,
            "service": exc.service,
            "operation": exc.operation,
            "details": exc.details
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """HTTP 예외 처리"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )


# 기본 라우터
@app.get("/", response_model=Dict[str, Any])
async def root():
    """루트 엔드포인트"""
    return {
        "service": settings.app.app_name,
        "version": settings.app.version,
        "environment": settings.app.environment,
        "enabled_services": settings.app.get_enabled_services(),
        "mcp_endpoint": f"{settings.app.mcp_mount_path}"
    }


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """헬스체크 엔드포인트"""
    service_statuses = {}
    
    # 활성화된 서비스별 상태 확인
    for service_name in settings.app.get_enabled_services():
        try:
            if service_name == "confluence" and hasattr(app.state, "confluence_client"):
                status = await _check_confluence_health()
            elif service_name == "jira" and hasattr(app.state, "jira_client"):
                status = await _check_jira_health()
            elif service_name == "slack" and hasattr(app.state, "slack_client"):
                status = await _check_slack_health()
            elif service_name == "calculator" and hasattr(app.state, "calculator_client"):
                status = await _check_calculator_health()
            else:
                status = ServiceStatus(
                    name=service_name,
                    status="unconfigured",
                    error="Service not configured or initialized"
                )
            
            service_statuses[service_name] = status.dict()
            
        except Exception as e:
            service_statuses[service_name] = ServiceStatus(
                name=service_name,
                status="unhealthy",
                error=str(e)
            ).dict()
    
    # 전체 상태 결정
    overall_status = "healthy"
    if any(status["status"] == "unhealthy" for status in service_statuses.values()):
        overall_status = "degraded"
    elif all(status["status"] == "unconfigured" for status in service_statuses.values()):
        overall_status = "unhealthy"
    
    return HealthCheckResponse(
        status=overall_status,
        version=settings.app.version,
        environment=settings.app.environment,
        services=service_statuses
    )


async def _check_confluence_health() -> ServiceStatus:
    """Confluence 서비스 헬스체크"""
    # 실제 구현에서는 간단한 API 호출로 상태 확인
    return ServiceStatus(name="confluence", status="healthy")


async def _check_jira_health() -> ServiceStatus:
    """JIRA 서비스 헬스체크"""
    return ServiceStatus(name="jira", status="healthy")


async def _check_slack_health() -> ServiceStatus:
    """Slack 서비스 헬스체크"""
    return ServiceStatus(name="slack", status="healthy")


async def _check_calculator_health() -> ServiceStatus:
    """Calculator 서비스 헬스체크"""
    try:
        client = app.state.calculator_client
        health = await client.health_check()
        if health["status"] == "healthy":
            return ServiceStatus(name="calculator", status="healthy")
        else:
            return ServiceStatus(name="calculator", status="unhealthy", error="Health check failed")
    except Exception as e:
        return ServiceStatus(name="calculator", status="unhealthy", error=str(e))


# 활성화된 서비스별 라우터 등록
def register_service_routers():
    """서비스 라우터 등록 (일반 FastAPI 엔드포인트)"""
    enabled_services = settings.app.get_enabled_services()
    logger.info("Registering service routers", enabled_services=enabled_services)
    
    for service_name in enabled_services:
        try:
            if service_name == "confluence" and settings.confluence:
                from .mcps.confluence.router import router as confluence_router
                app.include_router(
                    confluence_router,
                    prefix=f"/confluence"
                )
                logger.info("Confluence router registered")
                
            elif service_name == "jira" and settings.jira:
                from .mcps.jira.router import router as jira_router
                app.include_router(
                    jira_router,
                    prefix=f"/jira"
                )
                logger.info("JIRA router registered")
                
            elif service_name == "slack" and settings.slack:
                from .mcps.slack.router import router as slack_router
                app.include_router(
                    slack_router,
                    prefix=f"/slack"
                )
                logger.info("Slack router registered")
                
            elif service_name == "calculator":
                from .mcps.calculator.router import router as calculator_router
                app.include_router(
                    calculator_router,
                    prefix=f"/calculator"
                )
                logger.info("Calculator router registered")
                
        except ImportError as e:
            logger.warning(f"Could not import {service_name} router", error=str(e))
        except Exception as e:
            logger.error(f"Failed to register {service_name} router", error=str(e))


# 서비스 라우터 등록
register_service_routers()

# FastAPI MCP 서버 설정 및 마운트
mcp = FastApiMCP(
    app,
    name="AIDT MCP Server",
    description="AIDT 교육 플랫폼을 위한 멀티서비스 MCP 서버",
    include_tags=settings.app.get_enabled_services(),
    describe_all_responses=True,
    describe_full_response_schema=True
)

# MCP 서버를 지정된 경로에 마운트
mcp.mount_http()

logger.info(
    "AIDT MCP Server configured",
    version=settings.app.version,
    environment=settings.app.environment,
    enabled_services=settings.app.get_enabled_services(),
    mcp_mount_path=settings.app.mcp_mount_path
)