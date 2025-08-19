"""JIRA MCP 라우터"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
import structlog

from ...shared.utils import format_error_response, create_success_response
from ...shared.exceptions import MCPBaseException
from ...shared.auth import get_optional_user
from .client import get_jira_client, JiraClient
from .models import (
    JiraIssueRequest,
    JiraSearchRequest,
    JiraProjectRequest,
    JiraIssueResponse,
    JiraSearchResponse,
    JiraProjectResponse
)

logger = structlog.get_logger(__name__)

router = APIRouter(tags=["jira"])


@router.get("/search",
           response_model=JiraSearchResponse,
           operation_id="jira_search_issues",
           summary="JIRA 이슈 검색",
           description="JQL을 사용하여 JIRA 이슈를 검색합니다")
async def search_jira_issues(
    jql: str = Query(..., description="JQL 검색 쿼리", min_length=1, max_length=2000),
    start_at: int = Query(0, description="시작 인덱스", ge=0),
    max_results: int = Query(50, description="최대 결과 수", ge=1, le=100),
    expand: Optional[str] = Query(None, description="확장할 필드들"),
    client: JiraClient = Depends(get_jira_client),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """JIRA 이슈 검색"""
    
    try:
        logger.info(
            "JIRA search requested",
            jql=jql,
            max_results=max_results,
            user_id=user.get("sub") if user else None
        )
        
        # JQL 쿼리 검증은 클라이언트에서 수행
        result = await client.search_issues(
            jql=jql,
            start_at=start_at,
            max_results=max_results,
            expand=expand
        )
        
        logger.info(
            "JIRA search completed",
            total_results=result.total,
            returned_results=len(result.issues)
        )
        
        return JiraSearchResponse(
            success=True,
            message="JIRA 이슈 검색이 성공적으로 완료되었습니다",
            data=result
        )
        
    except MCPBaseException as e:
        logger.error("JIRA search failed", error=str(e), jql=jql)
        raise HTTPException(
            status_code=400 if e.__class__.__name__ != "AuthenticationError" else 401,
            detail=format_error_response(e, service="jira", operation="search")
        )
    except Exception as e:
        logger.error("Unexpected error in JIRA search", error=str(e), jql=jql)
        raise HTTPException(
            status_code=500,
            detail=format_error_response(e, service="jira", operation="search")
        )


@router.get("/issue",
           response_model=JiraIssueResponse,
           operation_id="jira_get_issue",
           summary="JIRA 이슈 조회",
           description="이슈 키를 사용하여 JIRA 이슈 상세 정보를 조회합니다")
async def get_jira_issue(
    issue_key: str = Query(..., description="이슈 키 (예: ABC-123)"),
    expand: Optional[str] = Query(None, description="확장할 필드들"),
    client: JiraClient = Depends(get_jira_client),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """JIRA 이슈 조회"""
    
    try:
        logger.info(
            "JIRA issue requested",
            issue_key=issue_key,
            expand=expand,
            user_id=user.get("sub") if user else None
        )
        
        issue = await client.get_issue(issue_key=issue_key, expand=expand)
        
        logger.info(
            "JIRA issue retrieved",
            issue_key=issue_key,
            summary=issue.fields.summary
        )
        
        return JiraIssueResponse(
            success=True,
            message="JIRA 이슈 조회가 성공적으로 완료되었습니다",
            data=issue
        )
        
    except MCPBaseException as e:
        logger.error("JIRA issue retrieval failed", error=str(e), issue_key=issue_key)
        raise HTTPException(
            status_code=400 if e.__class__.__name__ != "AuthenticationError" else 401,
            detail=format_error_response(e, service="jira", operation="get_issue")
        )
    except Exception as e:
        logger.error("Unexpected error in JIRA issue retrieval", error=str(e), issue_key=issue_key)
        raise HTTPException(
            status_code=500,
            detail=format_error_response(e, service="jira", operation="get_issue")
        )


@router.get("/project",
           response_model=JiraProjectResponse,
           operation_id="jira_get_project",
           summary="JIRA 프로젝트 조회",
           description="프로젝트 키를 사용하여 JIRA 프로젝트 정보를 조회합니다")
async def get_jira_project(
    project_key: str = Query(..., description="프로젝트 키"),
    expand: Optional[str] = Query(None, description="확장할 필드들"),
    client: JiraClient = Depends(get_jira_client),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """JIRA 프로젝트 조회"""
    
    try:
        logger.info(
            "JIRA project requested",
            project_key=project_key,
            expand=expand,
            user_id=user.get("sub") if user else None
        )
        
        project = await client.get_project(project_key=project_key, expand=expand)
        
        logger.info(
            "JIRA project retrieved",
            project_key=project_key,
            name=project.name
        )
        
        return JiraProjectResponse(
            success=True,
            message="JIRA 프로젝트 조회가 성공적으로 완료되었습니다",
            data=project
        )
        
    except MCPBaseException as e:
        logger.error("JIRA project retrieval failed", error=str(e), project_key=project_key)
        raise HTTPException(
            status_code=400 if e.__class__.__name__ != "AuthenticationError" else 401,
            detail=format_error_response(e, service="jira", operation="get_project")
        )
    except Exception as e:
        logger.error("Unexpected error in JIRA project retrieval", error=str(e), project_key=project_key)
        raise HTTPException(
            status_code=500,
            detail=format_error_response(e, service="jira", operation="get_project")
        )


@router.get("/health",
           operation_id="jira_health_check",
           summary="JIRA 서비스 상태 확인",
           description="JIRA 서비스의 연결 상태와 통계 정보를 확인합니다")
async def jira_health(
    client: JiraClient = Depends(get_jira_client)
):
    """JIRA 서비스 헬스체크"""
    
    try:
        health_info = await client.health_check()
        
        logger.info("JIRA health check completed", status=health_info["status"])
        
        return create_success_response(
            data=health_info,
            message="JIRA 서비스 상태 확인 완료"
        )
        
    except Exception as e:
        logger.error("JIRA health check failed", error=str(e))
        return create_success_response(
            data={
                "status": "unhealthy",
                "error": str(e)
            },
            message="JIRA 서비스 상태 확인 실패"
        )


@router.get("/stats",
           operation_id="jira_get_stats",
           summary="JIRA 통계 정보",
           description="JIRA 클라이언트의 통계 정보를 반환합니다")
async def jira_stats(
    client: JiraClient = Depends(get_jira_client)
):
    """JIRA 통계 정보"""
    
    try:
        stats = client.get_stats()
        
        logger.info("JIRA stats retrieved")
        
        return create_success_response(
            data=stats.dict(),
            message="JIRA 통계 정보 조회 완료"
        )
        
    except Exception as e:
        logger.error("Failed to get JIRA stats", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=format_error_response(e, service="jira", operation="get_stats")
        )


@router.get("/config",
           operation_id="jira_get_config",
           summary="JIRA 설정 정보",
           description="JIRA 서비스의 설정 정보를 반환합니다 (민감한 정보 제외)")
async def jira_config():
    """JIRA 설정 정보 (민감한 정보 제외)"""
    
    try:
        from .config import jira_config
        
        if not jira_config:
            raise HTTPException(
                status_code=503,
                detail="JIRA 서비스가 구성되지 않았습니다"
            )
        
        config_info = jira_config.to_dict()
        # 민감한 정보 제거
        config_info.pop("api_token", None)
        
        logger.info("JIRA config retrieved")
        
        return create_success_response(
            data=config_info,
            message="JIRA 설정 정보 조회 완료"
        )
        
    except Exception as e:
        logger.error("Failed to get JIRA config", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=format_error_response(e, service="jira", operation="get_config")
        )