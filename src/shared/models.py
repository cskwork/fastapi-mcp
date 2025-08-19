"""공통 Pydantic 모델들"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, field_validator
from datetime import datetime


class BaseResponseModel(BaseModel):
    """기본 응답 모델"""
    
    success: bool = Field(description="성공 여부")
    message: str = Field(description="응답 메시지")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="응답 시간")


class SuccessResponse(BaseResponseModel):
    """성공 응답 모델"""
    
    success: bool = Field(default=True)
    data: Optional[Any] = Field(None, description="응답 데이터")
    metadata: Optional[Dict[str, Any]] = Field(None, description="메타데이터")


class ErrorResponse(BaseResponseModel):
    """오류 응답 모델"""
    
    success: bool = Field(default=False)
    error_type: str = Field(description="오류 타입")
    details: Optional[Dict[str, Any]] = Field(None, description="오류 상세 정보")
    service: Optional[str] = Field(None, description="오류 발생 서비스")
    operation: Optional[str] = Field(None, description="오류 발생 작업")


class PaginationModel(BaseModel):
    """페이지네이션 모델"""
    
    page: int = Field(default=1, ge=1, description="페이지 번호")
    size: int = Field(default=25, ge=1, le=100, description="페이지 크기")
    total: Optional[int] = Field(None, description="전체 항목 수")
    has_next: Optional[bool] = Field(None, description="다음 페이지 존재 여부")
    has_prev: Optional[bool] = Field(None, description="이전 페이지 존재 여부")


class SearchQuery(BaseModel):
    """검색 쿼리 모델"""
    
    query: str = Field(..., min_length=1, max_length=1000, description="검색 쿼리")
    filters: Optional[Dict[str, Any]] = Field(None, description="검색 필터")
    sort: Optional[str] = Field(None, description="정렬 기준")
    limit: Optional[int] = Field(25, ge=1, le=100, description="결과 제한")
    
    @field_validator("query")
    @classmethod
    def validate_query(cls, v):
        # 기본적인 검증 - 실제로는 서비스별로 더 정교한 검증 필요
        if not v or not v.strip():
            raise ValueError("검색 쿼리는 비어있을 수 없습니다")
        return v.strip()


class HealthCheckResponse(BaseModel):
    """헬스체크 응답 모델"""
    
    status: str = Field(description="서비스 상태")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = Field(description="서비스 버전")
    environment: str = Field(description="실행 환경")
    services: Dict[str, Dict[str, Any]] = Field(description="개별 서비스 상태")


class ServiceStatus(BaseModel):
    """개별 서비스 상태"""
    
    name: str = Field(description="서비스 이름")
    status: str = Field(description="상태 (healthy/unhealthy/degraded)")
    last_check: datetime = Field(default_factory=datetime.utcnow)
    response_time_ms: Optional[float] = Field(None, description="응답 시간(ms)")
    error: Optional[str] = Field(None, description="오류 메시지")
    metadata: Optional[Dict[str, Any]] = Field(None, description="추가 정보")


class ConfigurationModel(BaseModel):
    """설정 모델"""
    
    service_name: str = Field(description="서비스 이름")
    enabled: bool = Field(default=True, description="활성화 여부")
    timeout: float = Field(default=10.0, ge=0.1, le=300.0, description="타임아웃(초)")
    max_retries: int = Field(default=3, ge=0, le=10, description="최대 재시도 횟수")
    rate_limit: Optional[int] = Field(None, ge=1, description="레이트 리미트 (요청/분)")


class LogEntry(BaseModel):
    """로그 엔트리 모델"""
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    level: str = Field(description="로그 레벨")
    message: str = Field(description="로그 메시지")
    service: Optional[str] = Field(None, description="서비스 이름")
    operation: Optional[str] = Field(None, description="작업 이름")
    duration_ms: Optional[float] = Field(None, description="작업 시간(ms)")
    error: Optional[str] = Field(None, description="오류 메시지")
    metadata: Optional[Dict[str, Any]] = Field(None, description="추가 메타데이터")


class MCPToolRequest(BaseModel):
    """MCP 도구 요청 모델"""
    
    tool_name: str = Field(description="도구 이름")
    parameters: Dict[str, Any] = Field(description="도구 매개변수")
    service: str = Field(description="서비스 이름")
    timeout: Optional[float] = Field(None, description="타임아웃(초)")


class MCPToolResponse(BaseModel):
    """MCP 도구 응답 모델"""
    
    tool_name: str = Field(description="도구 이름")
    success: bool = Field(description="성공 여부")
    result: Optional[Any] = Field(None, description="실행 결과")
    error: Optional[str] = Field(None, description="오류 메시지")
    execution_time_ms: Optional[float] = Field(None, description="실행 시간(ms)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="메타데이터")