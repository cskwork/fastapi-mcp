"""Slack MCP 라우터"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Body
import structlog

from ...shared.utils import format_error_response, create_success_response
from ...shared.exceptions import MCPBaseException
from ...shared.auth import get_optional_user
from .client import get_slack_client, SlackClient
from .models import (
    SlackChannelRequest,
    SlackMessageRequest,
    SlackHistoryRequest,
    SlackChannelResponse,
    SlackMessageResponse,
    SlackHistoryResponse,
    SlackUserResponse
)

logger = structlog.get_logger(__name__)

router = APIRouter(tags=["slack"])


@router.get("/channel/info",
           response_model=SlackChannelResponse,
           operation_id="slack_get_channel_info",
           summary="Slack 채널 정보 조회",
           description="채널 ID 또는 이름을 사용하여 Slack 채널 정보를 조회합니다")
async def get_slack_channel_info(
    channel: str = Query(..., description="채널 ID 또는 이름 (예: #general, C1234567890)"),
    client: SlackClient = Depends(get_slack_client),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Slack 채널 정보 조회"""
    
    try:
        logger.info(
            "Slack channel info requested",
            channel=channel,
            user_id=user.get("sub") if user else None
        )
        
        channel_info = await client.get_channel_info(channel=channel)
        
        logger.info(
            "Slack channel info retrieved",
            channel=channel,
            name=channel_info.channel.name
        )
        
        return SlackChannelResponse(
            success=True,
            message="Slack 채널 정보 조회가 성공적으로 완료되었습니다",
            data=channel_info
        )
        
    except MCPBaseException as e:
        logger.error("Slack channel info retrieval failed", error=str(e), channel=channel)
        raise HTTPException(
            status_code=400 if e.__class__.__name__ != "AuthenticationError" else 401,
            detail=format_error_response(e, service="slack", operation="get_channel_info")
        )
    except Exception as e:
        logger.error("Unexpected error in Slack channel info retrieval", error=str(e), channel=channel)
        raise HTTPException(
            status_code=500,
            detail=format_error_response(e, service="slack", operation="get_channel_info")
        )


@router.get("/channel/history",
           response_model=SlackHistoryResponse,
           operation_id="slack_get_channel_history",
           summary="Slack 채널 메시지 히스토리 조회",
           description="채널의 메시지 히스토리를 조회합니다")
async def get_slack_channel_history(
    channel: str = Query(..., description="채널 ID 또는 이름"),
    limit: int = Query(100, description="가져올 메시지 수", ge=1, le=1000),
    oldest: Optional[str] = Query(None, description="시작 타임스탬프"),
    latest: Optional[str] = Query(None, description="종료 타임스탬프"),
    client: SlackClient = Depends(get_slack_client),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Slack 채널 메시지 히스토리 조회"""
    
    try:
        logger.info(
            "Slack channel history requested",
            channel=channel,
            limit=limit,
            user_id=user.get("sub") if user else None
        )
        
        history = await client.get_conversation_history(
            channel=channel,
            limit=limit,
            oldest=oldest,
            latest=latest
        )
        
        logger.info(
            "Slack channel history retrieved",
            channel=channel,
            message_count=len(history.messages)
        )
        
        return SlackHistoryResponse(
            success=True,
            message="Slack 채널 히스토리 조회가 성공적으로 완료되었습니다",
            data=history
        )
        
    except MCPBaseException as e:
        logger.error("Slack channel history retrieval failed", error=str(e), channel=channel)
        raise HTTPException(
            status_code=400 if e.__class__.__name__ != "AuthenticationError" else 401,
            detail=format_error_response(e, service="slack", operation="get_channel_history")
        )
    except Exception as e:
        logger.error("Unexpected error in Slack channel history retrieval", error=str(e), channel=channel)
        raise HTTPException(
            status_code=500,
            detail=format_error_response(e, service="slack", operation="get_channel_history")
        )


@router.post("/message/send",
            response_model=SlackMessageResponse,
            operation_id="slack_send_message",
            summary="Slack 메시지 전송",
            description="지정된 채널에 메시지를 전송합니다")
async def send_slack_message(
    request: SlackMessageRequest = Body(..., description="메시지 전송 요청"),
    client: SlackClient = Depends(get_slack_client),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Slack 메시지 전송"""
    
    try:
        logger.info(
            "Slack message send requested",
            channel=request.channel,
            text_length=len(request.text),
            has_thread=bool(request.thread_ts),
            user_id=user.get("sub") if user else None
        )
        
        response = await client.post_message(
            channel=request.channel,
            text=request.text,
            thread_ts=request.thread_ts
        )
        
        logger.info(
            "Slack message sent",
            channel=request.channel,
            ts=response.ts
        )
        
        return SlackMessageResponse(
            success=True,
            message="Slack 메시지 전송이 성공적으로 완료되었습니다",
            data=response
        )
        
    except MCPBaseException as e:
        logger.error("Slack message send failed", error=str(e), channel=request.channel)
        raise HTTPException(
            status_code=400 if e.__class__.__name__ != "AuthenticationError" else 401,
            detail=format_error_response(e, service="slack", operation="send_message")
        )
    except Exception as e:
        logger.error("Unexpected error in Slack message send", error=str(e), channel=request.channel)
        raise HTTPException(
            status_code=500,
            detail=format_error_response(e, service="slack", operation="send_message")
        )


@router.get("/user/info",
           response_model=SlackUserResponse,
           operation_id="slack_get_user_info",
           summary="Slack 사용자 정보 조회",
           description="사용자 ID를 사용하여 Slack 사용자 정보를 조회합니다")
async def get_slack_user_info(
    user_id: str = Query(..., description="사용자 ID (예: U1234567890)"),
    client: SlackClient = Depends(get_slack_client),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Slack 사용자 정보 조회"""
    
    try:
        logger.info(
            "Slack user info requested",
            target_user_id=user_id,
            user_id=user.get("sub") if user else None
        )
        
        user_info = await client.get_user_info(user_id=user_id)
        
        logger.info(
            "Slack user info retrieved",
            target_user_id=user_id,
            name=user_info.user.name
        )
        
        return SlackUserResponse(
            success=True,
            message="Slack 사용자 정보 조회가 성공적으로 완료되었습니다",
            data=user_info
        )
        
    except MCPBaseException as e:
        logger.error("Slack user info retrieval failed", error=str(e), user_id=user_id)
        raise HTTPException(
            status_code=400 if e.__class__.__name__ != "AuthenticationError" else 401,
            detail=format_error_response(e, service="slack", operation="get_user_info")
        )
    except Exception as e:
        logger.error("Unexpected error in Slack user info retrieval", error=str(e), user_id=user_id)
        raise HTTPException(
            status_code=500,
            detail=format_error_response(e, service="slack", operation="get_user_info")
        )


@router.get("/health",
           operation_id="slack_health_check",
           summary="Slack 서비스 상태 확인",
           description="Slack 서비스의 연결 상태와 통계 정보를 확인합니다")
async def slack_health(
    client: SlackClient = Depends(get_slack_client)
):
    """Slack 서비스 헬스체크"""
    
    try:
        health_info = await client.health_check()
        
        logger.info("Slack health check completed", status=health_info["status"])
        
        return create_success_response(
            data=health_info,
            message="Slack 서비스 상태 확인 완료"
        )
        
    except Exception as e:
        logger.error("Slack health check failed", error=str(e))
        return create_success_response(
            data={
                "status": "unhealthy",
                "error": str(e)
            },
            message="Slack 서비스 상태 확인 실패"
        )


@router.get("/stats",
           operation_id="slack_get_stats",
           summary="Slack 통계 정보",
           description="Slack 클라이언트의 통계 정보를 반환합니다")
async def slack_stats(
    client: SlackClient = Depends(get_slack_client)
):
    """Slack 통계 정보"""
    
    try:
        stats = client.get_stats()
        
        logger.info("Slack stats retrieved")
        
        return create_success_response(
            data=stats.dict(),
            message="Slack 통계 정보 조회 완료"
        )
        
    except Exception as e:
        logger.error("Failed to get Slack stats", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=format_error_response(e, service="slack", operation="get_stats")
        )


@router.get("/config",
           operation_id="slack_get_config",
           summary="Slack 설정 정보",
           description="Slack 서비스의 설정 정보를 반환합니다 (민감한 정보 제외)")
async def slack_config():
    """Slack 설정 정보 (민감한 정보 제외)"""
    
    try:
        from .config import slack_config
        
        if not slack_config:
            raise HTTPException(
                status_code=503,
                detail="Slack 서비스가 구성되지 않았습니다"
            )
        
        config_info = slack_config.to_dict()
        
        logger.info("Slack config retrieved")
        
        return create_success_response(
            data=config_info,
            message="Slack 설정 정보 조회 완료"
        )
        
    except Exception as e:
        logger.error("Failed to get Slack config", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=format_error_response(e, service="slack", operation="get_config")
        )