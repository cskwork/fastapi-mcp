"""Confluence API 클라이언트"""

import asyncio
from typing import Dict, Any, Optional, List
import httpx
import structlog

from ...shared.utils import retry_with_backoff, measure_time
from ...shared.exceptions import ExternalAPIError, AuthenticationError, RateLimitError
from .config import confluence_config
from .models import (
    ConfluenceSearchResult, 
    ConfluenceContent, 
    ConfluenceSpace,
    ConfluenceStats
)

logger = structlog.get_logger(__name__)


class ConfluenceClient:
    """Confluence API 클라이언트"""
    
    def __init__(self):
        if not confluence_config:
            raise ValueError("Confluence 설정이 초기화되지 않았습니다")
        
        self.config = confluence_config
        self.client: Optional[httpx.AsyncClient] = None
        self.stats = ConfluenceStats(
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
                auth=self.config.auth_tuple,
                timeout=httpx.Timeout(self.config.timeout),
                headers=self.config.headers,
                limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
            )
            logger.info("Confluence client connected", base_url=self.config.base_url)
    
    async def close(self):
        """HTTP 클라이언트 종료"""
        if self.client:
            await self.client.aclose()
            self.client = None
            logger.info("Confluence client disconnected")
    
    @measure_time
    async def search(
        self, 
        cql: str, 
        limit: int = 25, 
        cursor: Optional[str] = None,
        expand: Optional[str] = None
    ) -> ConfluenceSearchResult:
        """CQL을 사용한 콘텐츠 검색"""
        
        if not self.client:
            await self.connect()
        
        params = {
            "cql": cql,
            "limit": min(limit, self.config.max_results)
        }
        
        if cursor:
            params["cursor"] = cursor
        
        if expand:
            params["expand"] = expand
        
        try:
            logger.info("Confluence search started", cql=cql, limit=limit)
            
            response = await retry_with_backoff(
                self.client,
                "GET",
                self.config.get_search_url(),
                params=params,
                max_retries=self.config.max_retries
            )
            
            self._update_stats(success=True, response_time=response.elapsed.total_seconds())
            
            data = response.json()
            logger.info("Confluence search completed", results_count=data.get("size", 0))
            
            return ConfluenceSearchResult(**data)
            
        except httpx.HTTPStatusError as e:
            self._update_stats(success=False)
            
            if e.response.status_code == 401:
                logger.error("Confluence authentication failed")
                raise AuthenticationError("Confluence 인증 실패", service="confluence", operation="search")
            elif e.response.status_code == 403:
                logger.error("Confluence access forbidden")
                raise AuthenticationError("Confluence 접근 권한 없음", service="confluence", operation="search")
            elif e.response.status_code == 429:
                logger.warning("Confluence rate limit exceeded")
                raise RateLimitError("Confluence 레이트 리미트 초과", service="confluence", operation="search")
            else:
                logger.error("Confluence search failed", status_code=e.response.status_code, error=str(e))
                raise ExternalAPIError(
                    f"Confluence 검색 실패: {e.response.status_code}",
                    status_code=e.response.status_code,
                    service="confluence",
                    operation="search"
                )
        
        except Exception as e:
            self._update_stats(success=False)
            logger.error("Confluence search error", error=str(e))
            raise ExternalAPIError(f"Confluence 검색 오류: {str(e)}", service="confluence", operation="search")
    
    @measure_time
    async def get_page(
        self, 
        page_id: str, 
        expand: str = "body.storage,version"
    ) -> ConfluenceContent:
        """페이지 상세 정보 조회"""
        
        if not self.client:
            await self.connect()
        
        params = {"expand": expand}
        
        try:
            logger.info("Confluence page retrieval started", page_id=page_id)
            
            response = await retry_with_backoff(
                self.client,
                "GET",
                self.config.get_content_url(page_id),
                params=params,
                max_retries=self.config.max_retries
            )
            
            self._update_stats(success=True, response_time=response.elapsed.total_seconds())
            
            data = response.json()
            logger.info("Confluence page retrieved", page_id=page_id, title=data.get("title"))
            
            return ConfluenceContent(**data)
            
        except httpx.HTTPStatusError as e:
            self._update_stats(success=False)
            
            if e.response.status_code == 404:
                logger.warning("Confluence page not found", page_id=page_id)
                raise ExternalAPIError(f"페이지를 찾을 수 없습니다: {page_id}", status_code=404, service="confluence", operation="get_page")
            elif e.response.status_code == 401:
                logger.error("Confluence authentication failed")
                raise AuthenticationError("Confluence 인증 실패", service="confluence", operation="get_page")
            elif e.response.status_code == 403:
                logger.error("Confluence access forbidden", page_id=page_id)
                raise AuthenticationError("페이지 접근 권한 없음", service="confluence", operation="get_page")
            else:
                logger.error("Confluence page retrieval failed", page_id=page_id, status_code=e.response.status_code)
                raise ExternalAPIError(
                    f"페이지 조회 실패: {e.response.status_code}",
                    status_code=e.response.status_code,
                    service="confluence",
                    operation="get_page"
                )
        
        except Exception as e:
            self._update_stats(success=False)
            logger.error("Confluence page retrieval error", page_id=page_id, error=str(e))
            raise ExternalAPIError(f"페이지 조회 오류: {str(e)}", service="confluence", operation="get_page")
    
    @measure_time
    async def get_space(
        self, 
        space_key: str, 
        expand: Optional[str] = None
    ) -> ConfluenceSpace:
        """스페이스 정보 조회"""
        
        if not self.client:
            await self.connect()
        
        params = {}
        if expand:
            params["expand"] = expand
        
        try:
            logger.info("Confluence space retrieval started", space_key=space_key)
            
            response = await retry_with_backoff(
                self.client,
                "GET",
                self.config.get_space_url(space_key),
                params=params,
                max_retries=self.config.max_retries
            )
            
            self._update_stats(success=True, response_time=response.elapsed.total_seconds())
            
            data = response.json()
            logger.info("Confluence space retrieved", space_key=space_key, name=data.get("name"))
            
            return ConfluenceSpace(**data)
            
        except httpx.HTTPStatusError as e:
            self._update_stats(success=False)
            
            if e.response.status_code == 404:
                logger.warning("Confluence space not found", space_key=space_key)
                raise ExternalAPIError(f"스페이스를 찾을 수 없습니다: {space_key}", status_code=404, service="confluence", operation="get_space")
            elif e.response.status_code == 401:
                logger.error("Confluence authentication failed")
                raise AuthenticationError("Confluence 인증 실패", service="confluence", operation="get_space")
            elif e.response.status_code == 403:
                logger.error("Confluence access forbidden", space_key=space_key)
                raise AuthenticationError("스페이스 접근 권한 없음", service="confluence", operation="get_space")
            else:
                logger.error("Confluence space retrieval failed", space_key=space_key, status_code=e.response.status_code)
                raise ExternalAPIError(
                    f"스페이스 조회 실패: {e.response.status_code}",
                    status_code=e.response.status_code,
                    service="confluence",
                    operation="get_space"
                )
        
        except Exception as e:
            self._update_stats(success=False)
            logger.error("Confluence space retrieval error", space_key=space_key, error=str(e))
            raise ExternalAPIError(f"스페이스 조회 오류: {str(e)}", service="confluence", operation="get_space")
    
    async def health_check(self) -> Dict[str, Any]:
        """Confluence 연결 상태 확인"""
        
        if not self.client:
            await self.connect()
        
        try:
            # 간단한 API 호출로 연결 상태 확인
            response = await self.client.get(
                self.config.get_space_url(),
                params={"limit": 1}
            )
            response.raise_for_status()
            
            return {
                "status": "healthy",
                "response_time_ms": response.elapsed.total_seconds() * 1000,
                "stats": self.stats.dict()
            }
            
        except Exception as e:
            logger.error("Confluence health check failed", error=str(e))
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
    
    def get_stats(self) -> ConfluenceStats:
        """통계 정보 반환"""
        return self.stats


# 전역 클라이언트 인스턴스 관리
_confluence_client: Optional[ConfluenceClient] = None


async def get_confluence_client() -> ConfluenceClient:
    """Confluence 클라이언트 인스턴스 반환"""
    global _confluence_client
    
    if _confluence_client is None:
        _confluence_client = ConfluenceClient()
        await _confluence_client.connect()
    
    return _confluence_client


async def close_confluence_client():
    """Confluence 클라이언트 연결 종료"""
    global _confluence_client
    
    if _confluence_client:
        await _confluence_client.close()
        _confluence_client = None