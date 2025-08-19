"""Confluence MCP 라우터"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
import structlog

from ...shared.utils import validate_cql_query, format_error_response, create_success_response
from ...shared.exceptions import MCPBaseException
from ...shared.auth import get_optional_user
from .client import get_confluence_client, ConfluenceClient
from .models import (
    ConfluenceSearchRequest,
    ConfluencePageRequest, 
    ConfluenceSpaceRequest,
    ConfluenceSearchResponse,
    ConfluencePageResponse,
    ConfluenceSpaceResponse
)

logger = structlog.get_logger(__name__)

router = APIRouter(tags=["confluence"])


@router.get("/search", 
           response_model=ConfluenceSearchResponse,
           operation_id="confluence_search",
           summary="Confluence 콘텐츠 검색",
           description="CQL을 사용하여 Confluence 콘텐츠를 검색합니다")
async def search_confluence(
    q: str = Query(..., description="CQL 검색 쿼리", min_length=1, max_length=1000),
    limit: int = Query(25, description="결과 제한 수", ge=1, le=100),
    cursor: Optional[str] = Query(None, description="페이지네이션 커서"),
    expand: Optional[str] = Query(None, description="확장할 필드들"),
    client: ConfluenceClient = Depends(get_confluence_client),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Confluence 콘텐츠 검색"""
    
    try:
        # CQL 쿼리 검증
        validated_cql = validate_cql_query(q)
        
        logger.info(
            "Confluence search requested",
            cql=validated_cql,
            limit=limit,
            user_id=user.get("sub") if user else None
        )
        
        # 검색 실행
        result = await client.search(
            cql=validated_cql,
            limit=limit,
            cursor=cursor,
            expand=expand
        )
        
        logger.info(
            "Confluence search completed",
            results_count=result.size,
            total_size=result.total_size
        )
        
        return ConfluenceSearchResponse(
            success=True,
            message="검색이 성공적으로 완료되었습니다",
            data=result
        )
        
    except MCPBaseException as e:
        logger.error("Confluence search failed", error=str(e), cql=q)
        raise HTTPException(
            status_code=400,
            detail=format_error_response(e, service="confluence", operation="search")
        )
    except Exception as e:
        logger.error("Unexpected error in confluence search", error=str(e), cql=q)
        raise HTTPException(
            status_code=500,
            detail=format_error_response(e, service="confluence", operation="search")
        )


@router.get("/page",
           response_model=ConfluencePageResponse,
           operation_id="confluence_get_page",
           summary="Confluence 페이지 조회",
           description="페이지 ID를 사용하여 Confluence 페이지 상세 정보를 조회합니다")
async def get_confluence_page(
    page_id: str = Query(..., description="페이지 ID"),
    expand: str = Query("body.storage,version", description="확장할 필드들"),
    client: ConfluenceClient = Depends(get_confluence_client),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Confluence 페이지 조회"""
    
    try:
        logger.info(
            "Confluence page requested",
            page_id=page_id,
            expand=expand,
            user_id=user.get("sub") if user else None
        )
        
        # 페이지 조회
        page = await client.get_page(page_id=page_id, expand=expand)
        
        logger.info(
            "Confluence page retrieved",
            page_id=page_id,
            title=page.title
        )
        
        return ConfluencePageResponse(
            success=True,
            message="페이지 조회가 성공적으로 완료되었습니다",
            data=page
        )
        
    except MCPBaseException as e:
        logger.error("Confluence page retrieval failed", error=str(e), page_id=page_id)
        raise HTTPException(
            status_code=400 if e.__class__.__name__ != "AuthenticationError" else 401,
            detail=format_error_response(e, service="confluence", operation="get_page")
        )
    except Exception as e:
        logger.error("Unexpected error in confluence page retrieval", error=str(e), page_id=page_id)
        raise HTTPException(
            status_code=500,
            detail=format_error_response(e, service="confluence", operation="get_page")
        )


@router.get("/space",
           response_model=ConfluenceSpaceResponse,
           operation_id="confluence_get_space",
           summary="Confluence 스페이스 조회",
           description="스페이스 키를 사용하여 Confluence 스페이스 정보를 조회합니다")
async def get_confluence_space(
    space_key: str = Query(..., description="스페이스 키"),
    expand: Optional[str] = Query(None, description="확장할 필드들"),
    client: ConfluenceClient = Depends(get_confluence_client),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Confluence 스페이스 조회"""
    
    try:
        logger.info(
            "Confluence space requested",
            space_key=space_key,
            expand=expand,
            user_id=user.get("sub") if user else None
        )
        
        # 스페이스 조회
        space = await client.get_space(space_key=space_key, expand=expand)
        
        logger.info(
            "Confluence space retrieved",
            space_key=space_key,
            name=space.name
        )
        
        return ConfluenceSpaceResponse(
            success=True,
            message="스페이스 조회가 성공적으로 완료되었습니다",
            data=space
        )
        
    except MCPBaseException as e:
        logger.error("Confluence space retrieval failed", error=str(e), space_key=space_key)
        raise HTTPException(
            status_code=400 if e.__class__.__name__ != "AuthenticationError" else 401,
            detail=format_error_response(e, service="confluence", operation="get_space")
        )
    except Exception as e:
        logger.error("Unexpected error in confluence space retrieval", error=str(e), space_key=space_key)
        raise HTTPException(
            status_code=500,
            detail=format_error_response(e, service="confluence", operation="get_space")
        )


@router.get("/health",
           summary="Confluence 서비스 상태 확인",
           description="Confluence 서비스의 연결 상태와 통계 정보를 확인합니다")
async def confluence_health(
    client: ConfluenceClient = Depends(get_confluence_client)
):
    """Confluence 서비스 헬스체크"""
    
    try:
        health_info = await client.health_check()
        
        logger.info("Confluence health check completed", status=health_info["status"])
        
        return create_success_response(
            data=health_info,
            message="Confluence 서비스 상태 확인 완료"
        )
        
    except Exception as e:
        logger.error("Confluence health check failed", error=str(e))
        return create_success_response(
            data={
                "status": "unhealthy",
                "error": str(e)
            },
            message="Confluence 서비스 상태 확인 실패"
        )


@router.get("/stats",
           summary="Confluence 통계 정보",
           description="Confluence 클라이언트의 통계 정보를 반환합니다")
async def confluence_stats(
    client: ConfluenceClient = Depends(get_confluence_client)
):
    """Confluence 통계 정보"""
    
    try:
        stats = client.get_stats()
        
        logger.info("Confluence stats retrieved")
        
        return create_success_response(
            data=stats.dict(),
            message="Confluence 통계 정보 조회 완료"
        )
        
    except Exception as e:
        logger.error("Failed to get confluence stats", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=format_error_response(e, service="confluence", operation="get_stats")
        )


@router.get("/config",
           summary="Confluence 설정 정보",
           description="Confluence 서비스의 설정 정보를 반환합니다 (민감한 정보 제외)")
async def confluence_config():
    """Confluence 설정 정보 (민감한 정보 제외)"""
    
    try:
        from .config import confluence_config
        
        if not confluence_config:
            raise HTTPException(
                status_code=503,
                detail="Confluence 서비스가 구성되지 않았습니다"
            )
        
        config_info = confluence_config.to_dict()
        # 민감한 정보 제거
        config_info.pop("api_token", None)
        
        logger.info("Confluence config retrieved")
        
        return create_success_response(
            data=config_info,
            message="Confluence 설정 정보 조회 완료"
        )
        
    except Exception as e:
        logger.error("Failed to get confluence config", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=format_error_response(e, service="confluence", operation="get_config")
        )