"""Slack API 클라이언트"""

import asyncio
from typing import Dict, Any, Optional, List
import httpx
import structlog

from ...shared.utils import retry_with_backoff, measure_time
from ...shared.exceptions import ExternalAPIError, AuthenticationError, RateLimitError
from .config import slack_config
from .models import (
    SlackChannelInfo,
    SlackConversationHistory,
    SlackPostMessageResponse,
    SlackUserInfo,
    SlackStats,
    SlackError
)

logger = structlog.get_logger(__name__)


class SlackClient:
    """Slack API 클라이언트"""
    
    def __init__(self):
        if not slack_config:
            raise ValueError("Slack 설정이 초기화되지 않았습니다")
        
        self.config = slack_config
        self.client: Optional[httpx.AsyncClient] = None
        self.stats = SlackStats(
            total_requests=0,
            successful_requests=0,
            failed_requests=0,
            average_response_time=0.0
        )
    
    async def __aenter__(self):
        """비동기 컨텍스트 매니저 시작"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """비동기 컨텍스트 매니저 종료"""
        await self.close()
    
    async def connect(self):
        """HTTP 클라이언트 연결"""
        if self.client is None:
            self.client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.config.timeout),
                headers=self.config.auth_headers,
                limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
            )
            logger.info("Slack client connected")
    
    async def close(self):
        """HTTP 클라이언트 종료"""
        if self.client:
            await self.client.aclose()
            self.client = None
            logger.info("Slack client disconnected")
    
    def _handle_slack_error(self, response_data: Dict[str, Any], operation: str):
        """Slack API 오류 처리"""
        if not response_data.get("ok", False):
            error_code = response_data.get("error", "unknown")
            error_message = f"Slack API 오류: {error_code}"
            
            if error_code in ["invalid_auth", "account_inactive", "token_revoked"]:
                raise AuthenticationError(error_message, service="slack", operation=operation)
            elif error_code == "rate_limited":
                raise RateLimitError(error_message, service="slack", operation=operation)
            else:
                raise ExternalAPIError(error_message, service="slack", operation=operation)
    
    @measure_time
    async def get_channel_info(self, channel: str) -> SlackChannelInfo:
        """채널 정보 조회"""
        
        if not self.client:
            await self.connect()
        
        params = {"channel": channel}
        
        try:
            logger.info("Slack channel info requested", channel=channel)
            
            response = await retry_with_backoff(
                self.client,
                "GET",
                self.config.get_conversations_info_url(),
                params=params,
                max_retries=self.config.max_retries
            )
            
            self._update_stats(success=True, response_time=response.elapsed.total_seconds())
            
            data = response.json()
            self._handle_slack_error(data, "get_channel_info")
            
            logger.info("Slack channel info retrieved", channel=channel, name=data.get("channel", {}).get("name"))
            
            return SlackChannelInfo(**data)
            
        except httpx.HTTPStatusError as e:
            self._update_stats(success=False)
            logger.error("Slack channel info request failed", channel=channel, status_code=e.response.status_code)
            raise ExternalAPIError(
                f"채널 정보 조회 실패: {e.response.status_code}",
                status_code=e.response.status_code,
                service="slack",
                operation="get_channel_info"
            )
        
        except Exception as e:
            self._update_stats(success=False)
            logger.error("Slack channel info error", channel=channel, error=str(e))
            raise ExternalAPIError(f"채널 정보 조회 오류: {str(e)}", service="slack", operation="get_channel_info")
    
    @measure_time
    async def get_conversation_history(
        self,
        channel: str,
        limit: int = 100,
        oldest: Optional[str] = None,
        latest: Optional[str] = None
    ) -> SlackConversationHistory:
        """채널 대화 히스토리 조회"""
        
        if not self.client:
            await self.connect()
        
        params = {
            "channel": channel,
            "limit": min(limit, 1000)
        }
        
        if oldest:
            params["oldest"] = oldest
        if latest:
            params["latest"] = latest
        
        try:
            logger.info("Slack conversation history requested", channel=channel, limit=limit)
            
            response = await retry_with_backoff(
                self.client,
                "GET",
                self.config.get_conversations_history_url(),
                params=params,
                max_retries=self.config.max_retries
            )
            
            self._update_stats(success=True, response_time=response.elapsed.total_seconds())
            
            data = response.json()
            self._handle_slack_error(data, "get_conversation_history")
            
            message_count = len(data.get("messages", []))
            logger.info("Slack conversation history retrieved", channel=channel, message_count=message_count)
            
            return SlackConversationHistory(**data)
            
        except httpx.HTTPStatusError as e:
            self._update_stats(success=False)
            logger.error("Slack conversation history request failed", channel=channel, status_code=e.response.status_code)
            raise ExternalAPIError(
                f"대화 히스토리 조회 실패: {e.response.status_code}",
                status_code=e.response.status_code,
                service="slack",
                operation="get_conversation_history"
            )
        
        except Exception as e:
            self._update_stats(success=False)
            logger.error("Slack conversation history error", channel=channel, error=str(e))
            raise ExternalAPIError(f"대화 히스토리 조회 오류: {str(e)}", service="slack", operation="get_conversation_history")
    
    @measure_time
    async def post_message(
        self,
        channel: str,
        text: str,
        thread_ts: Optional[str] = None
    ) -> SlackPostMessageResponse:
        """메시지 전송"""
        
        if not self.client:
            await self.connect()
        
        payload = {
            "channel": channel,
            "text": text
        }
        
        if thread_ts:
            payload["thread_ts"] = thread_ts
        
        try:
            logger.info("Slack message post requested", channel=channel, has_thread=bool(thread_ts))
            
            response = await retry_with_backoff(
                self.client,
                "POST",
                self.config.get_chat_post_message_url(),
                json=payload,
                max_retries=self.config.max_retries
            )
            
            self._update_stats(success=True, response_time=response.elapsed.total_seconds())
            self.stats.messages_sent += 1
            
            data = response.json()
            self._handle_slack_error(data, "post_message")
            
            logger.info("Slack message posted", channel=channel, ts=data.get("ts"))
            
            return SlackPostMessageResponse(**data)
            
        except httpx.HTTPStatusError as e:
            self._update_stats(success=False)
            logger.error("Slack message post failed", channel=channel, status_code=e.response.status_code)
            raise ExternalAPIError(
                f"메시지 전송 실패: {e.response.status_code}",
                status_code=e.response.status_code,
                service="slack",
                operation="post_message"
            )
        
        except Exception as e:
            self._update_stats(success=False)
            logger.error("Slack message post error", channel=channel, error=str(e))
            raise ExternalAPIError(f"메시지 전송 오류: {str(e)}", service="slack", operation="post_message")
    
    @measure_time
    async def get_user_info(self, user_id: str) -> SlackUserInfo:
        """사용자 정보 조회"""
        
        if not self.client:
            await self.connect()
        
        params = {"user": user_id}
        
        try:
            logger.info("Slack user info requested", user_id=user_id)
            
            response = await retry_with_backoff(
                self.client,
                "GET",
                self.config.get_users_info_url(),
                params=params,
                max_retries=self.config.max_retries
            )
            
            self._update_stats(success=True, response_time=response.elapsed.total_seconds())
            
            data = response.json()
            self._handle_slack_error(data, "get_user_info")
            
            logger.info("Slack user info retrieved", user_id=user_id, name=data.get("user", {}).get("name"))
            
            return SlackUserInfo(**data)
            
        except httpx.HTTPStatusError as e:
            self._update_stats(success=False)
            logger.error("Slack user info request failed", user_id=user_id, status_code=e.response.status_code)
            raise ExternalAPIError(
                f"사용자 정보 조회 실패: {e.response.status_code}",
                status_code=e.response.status_code,
                service="slack",
                operation="get_user_info"
            )
        
        except Exception as e:
            self._update_stats(success=False)
            logger.error("Slack user info error", user_id=user_id, error=str(e))
            raise ExternalAPIError(f"사용자 정보 조회 오류: {str(e)}", service="slack", operation="get_user_info")
    
    async def health_check(self) -> Dict[str, Any]:
        """Slack 연결 상태 확인"""
        
        if not self.client:
            await self.connect()
        
        try:
            # auth.test API로 연결 상태 확인
            response = await self.client.post(self.config.get_auth_test_url())
            response.raise_for_status()
            
            data = response.json()
            if data.get("ok"):
                return {
                    "status": "healthy",
                    "response_time_ms": response.elapsed.total_seconds() * 1000,
                    "team": data.get("team"),
                    "user": data.get("user"),
                    "stats": self.stats.dict()
                }
            else:
                return {
                    "status": "unhealthy",
                    "error": data.get("error", "unknown"),
                    "stats": self.stats.dict()
                }
            
        except Exception as e:
            logger.error("Slack health check failed", error=str(e))
            return {
                "status": "unhealthy",
                "error": str(e),
                "stats": self.stats.dict()
            }
    
    def _update_stats(self, success: bool, response_time: float = None):
        """통계 정보 업데이트"""
        self.stats.total_requests += 1
        
        if success:
            self.stats.successful_requests += 1
            if response_time:
                # 이동 평균 계산
                if self.stats.average_response_time == 0:
                    self.stats.average_response_time = response_time * 1000
                else:
                    self.stats.average_response_time = (
                        self.stats.average_response_time * 0.9 + 
                        response_time * 1000 * 0.1
                    )
        else:
            self.stats.failed_requests += 1
    
    def get_stats(self) -> SlackStats:
        """통계 정보 반환"""
        return self.stats


# 전역 클라이언트 인스턴스 관리
_slack_client: Optional[SlackClient] = None


async def get_slack_client() -> SlackClient:
    """Slack 클라이언트 인스턴스 반환"""
    global _slack_client
    
    if _slack_client is None:
        _slack_client = SlackClient()
        await _slack_client.connect()
    
    return _slack_client


async def close_slack_client():
    """Slack 클라이언트 연결 종료"""
    global _slack_client
    
    if _slack_client:
        await _slack_client.close()
        _slack_client = None