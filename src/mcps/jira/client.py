"""JIRA API 클라이언트"""

import asyncio
from typing import Dict, Any, Optional, List
import httpx
import structlog

from ...shared.utils import retry_with_backoff, measure_time
from ...shared.exceptions import ExternalAPIError, AuthenticationError, RateLimitError
from .config import jira_config
from .models import (
    JiraSearchResult,
    JiraIssue,
    JiraProject,
    JiraStats
)

logger = structlog.get_logger(__name__)


class JiraClient:
    """JIRA API 클라이언트"""
    
    def __init__(self):
        if not jira_config:
            raise ValueError("JIRA 설정이 초기화되지 않았습니다")
        
        self.config = jira_config
        self.client: Optional[httpx.AsyncClient] = None
        self.stats = JiraStats(
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
            logger.info("JIRA client connected", base_url=self.config.base_url)
    
    async def close(self):
        """HTTP 클라이언트 종료"""
        if self.client:
            await self.client.aclose()
            self.client = None
            logger.info("JIRA client disconnected")
    
    @measure_time
    async def search_issues(
        self,
        jql: str,
        start_at: int = 0,
        max_results: int = 50,
        expand: Optional[str] = None
    ) -> JiraSearchResult:
        """JQL을 사용한 이슈 검색"""
        
        if not self.client:
            await self.connect()
        
        params = {
            "jql": jql,
            "startAt": start_at,
            "maxResults": min(max_results, 100)
        }
        
        if expand:
            params["expand"] = expand
        
        try:
            logger.info("JIRA search started", jql=jql, max_results=max_results)
            
            response = await retry_with_backoff(
                self.client,
                "GET",
                self.config.get_search_url(),
                params=params,
                max_retries=self.config.max_retries
            )
            
            self._update_stats(success=True, response_time=response.elapsed.total_seconds())
            
            data = response.json()
            logger.info("JIRA search completed", total_results=data.get("total", 0))
            
            return JiraSearchResult(**data)
            
        except httpx.HTTPStatusError as e:
            self._update_stats(success=False)
            
            if e.response.status_code == 401:
                logger.error("JIRA authentication failed")
                raise AuthenticationError("JIRA 인증 실패", service="jira", operation="search")
            elif e.response.status_code == 403:
                logger.error("JIRA access forbidden")
                raise AuthenticationError("JIRA 접근 권한 없음", service="jira", operation="search")
            elif e.response.status_code == 429:
                logger.warning("JIRA rate limit exceeded")
                raise RateLimitError("JIRA 레이트 리미트 초과", service="jira", operation="search")
            elif e.response.status_code == 400:
                logger.error("Invalid JQL query", jql=jql)
                raise ExternalAPIError(
                    f"잘못된 JQL 쿼리: {jql}",
                    status_code=400,
                    service="jira",
                    operation="search"
                )
            else:
                logger.error("JIRA search failed", status_code=e.response.status_code, error=str(e))
                raise ExternalAPIError(
                    f"JIRA 검색 실패: {e.response.status_code}",
                    status_code=e.response.status_code,
                    service="jira",
                    operation="search"
                )
        
        except Exception as e:
            self._update_stats(success=False)
            logger.error("JIRA search error", error=str(e))
            raise ExternalAPIError(f"JIRA 검색 오류: {str(e)}", service="jira", operation="search")
    
    @measure_time
    async def get_issue(
        self,
        issue_key: str,
        expand: Optional[str] = None
    ) -> JiraIssue:
        """이슈 상세 정보 조회"""
        
        if not self.client:
            await self.connect()
        
        params = {}
        if expand:
            params["expand"] = expand
        
        try:
            logger.info("JIRA issue retrieval started", issue_key=issue_key)
            
            response = await retry_with_backoff(
                self.client,
                "GET",
                self.config.get_issue_url(issue_key),
                params=params,
                max_retries=self.config.max_retries
            )
            
            self._update_stats(success=True, response_time=response.elapsed.total_seconds())
            
            data = response.json()
            logger.info("JIRA issue retrieved", issue_key=issue_key, summary=data.get("fields", {}).get("summary"))
            
            return JiraIssue(**data)
            
        except httpx.HTTPStatusError as e:
            self._update_stats(success=False)
            
            if e.response.status_code == 404:
                logger.warning("JIRA issue not found", issue_key=issue_key)
                raise ExternalAPIError(f"이슈를 찾을 수 없습니다: {issue_key}", status_code=404, service="jira", operation="get_issue")
            elif e.response.status_code == 401:
                logger.error("JIRA authentication failed")
                raise AuthenticationError("JIRA 인증 실패", service="jira", operation="get_issue")
            elif e.response.status_code == 403:
                logger.error("JIRA access forbidden", issue_key=issue_key)
                raise AuthenticationError("이슈 접근 권한 없음", service="jira", operation="get_issue")
            else:
                logger.error("JIRA issue retrieval failed", issue_key=issue_key, status_code=e.response.status_code)
                raise ExternalAPIError(
                    f"이슈 조회 실패: {e.response.status_code}",
                    status_code=e.response.status_code,
                    service="jira",
                    operation="get_issue"
                )
        
        except Exception as e:
            self._update_stats(success=False)
            logger.error("JIRA issue retrieval error", issue_key=issue_key, error=str(e))
            raise ExternalAPIError(f"이슈 조회 오류: {str(e)}", service="jira", operation="get_issue")
    
    @measure_time
    async def get_project(
        self,
        project_key: str,
        expand: Optional[str] = None
    ) -> JiraProject:
        """프로젝트 정보 조회"""
        
        if not self.client:
            await self.connect()
        
        params = {}
        if expand:
            params["expand"] = expand
        
        try:
            logger.info("JIRA project retrieval started", project_key=project_key)
            
            response = await retry_with_backoff(
                self.client,
                "GET",
                self.config.get_project_url(project_key),
                params=params,
                max_retries=self.config.max_retries
            )
            
            self._update_stats(success=True, response_time=response.elapsed.total_seconds())
            
            data = response.json()
            logger.info("JIRA project retrieved", project_key=project_key, name=data.get("name"))
            
            return JiraProject(**data)
            
        except httpx.HTTPStatusError as e:
            self._update_stats(success=False)
            
            if e.response.status_code == 404:
                logger.warning("JIRA project not found", project_key=project_key)
                raise ExternalAPIError(f"프로젝트를 찾을 수 없습니다: {project_key}", status_code=404, service="jira", operation="get_project")
            elif e.response.status_code == 401:
                logger.error("JIRA authentication failed")
                raise AuthenticationError("JIRA 인증 실패", service="jira", operation="get_project")
            elif e.response.status_code == 403:
                logger.error("JIRA access forbidden", project_key=project_key)
                raise AuthenticationError("프로젝트 접근 권한 없음", service="jira", operation="get_project")
            else:
                logger.error("JIRA project retrieval failed", project_key=project_key, status_code=e.response.status_code)
                raise ExternalAPIError(
                    f"프로젝트 조회 실패: {e.response.status_code}",
                    status_code=e.response.status_code,
                    service="jira",
                    operation="get_project"
                )
        
        except Exception as e:
            self._update_stats(success=False)
            logger.error("JIRA project retrieval error", project_key=project_key, error=str(e))
            raise ExternalAPIError(f"프로젝트 조회 오류: {str(e)}", service="jira", operation="get_project")
    
    async def health_check(self) -> Dict[str, Any]:
        """JIRA 연결 상태 확인"""
        
        if not self.client:
            await self.connect()
        
        try:
            # 간단한 API 호출로 연결 상태 확인
            response = await self.client.get(f"{self.config.api_base_url}/serverInfo")
            response.raise_for_status()
            
            return {
                "status": "healthy",
                "response_time_ms": response.elapsed.total_seconds() * 1000,
                "stats": self.stats.dict()
            }
            
        except Exception as e:
            logger.error("JIRA health check failed", error=str(e))
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
    
    def get_stats(self) -> JiraStats:
        """통계 정보 반환"""
        return self.stats


# 전역 클라이언트 인스턴스 관리
_jira_client: Optional[JiraClient] = None


async def get_jira_client() -> JiraClient:
    """JIRA 클라이언트 인스턴스 반환"""
    global _jira_client
    
    if _jira_client is None:
        _jira_client = JiraClient()
        await _jira_client.connect()
    
    return _jira_client


async def close_jira_client():
    """JIRA 클라이언트 연결 종료"""
    global _jira_client
    
    if _jira_client:
        await _jira_client.close()
        _jira_client = None