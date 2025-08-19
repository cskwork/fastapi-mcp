"""Confluence MCP 모델들"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, field_validator
from datetime import datetime

from ...shared.models import BaseResponseModel


class ConfluenceSearchRequest(BaseModel):
    """Confluence 검색 요청 모델"""
    
    cql: str = Field(..., min_length=1, max_length=1000, description="CQL 검색 쿼리")
    limit: int = Field(default=25, ge=1, le=100, description="결과 제한 수")
    cursor: Optional[str] = Field(None, description="페이지네이션 커서")
    expand: Optional[str] = Field(None, description="확장할 필드들")
    
    @field_validator("cql")
    @classmethod
    def validate_cql(cls, v):
        # 기본적인 CQL 검증
        if not v or not v.strip():
            raise ValueError("CQL 쿼리는 비어있을 수 없습니다")
        
        # 위험한 패턴 검사
        dangerous_patterns = [
            "user.", "accountid", "script", ";", "--", "/*", "*/",
            "drop", "delete", "update", "insert", "create", "alter"
        ]
        
        v_lower = v.lower()
        for pattern in dangerous_patterns:
            if pattern in v_lower:
                raise ValueError(f"금지된 CQL 패턴: {pattern}")
        
        return v.strip()


class ConfluencePageRequest(BaseModel):
    """Confluence 페이지 조회 요청 모델"""
    
    page_id: str = Field(..., description="페이지 ID")
    expand: str = Field(default="body.storage,version", description="확장할 필드들")
    
    @field_validator("page_id")
    @classmethod
    def validate_page_id(cls, v):
        if not v or not v.strip():
            raise ValueError("페이지 ID는 비어있을 수 없습니다")
        return v.strip()


class ConfluenceSpaceRequest(BaseModel):
    """Confluence 스페이스 조회 요청 모델"""
    
    space_key: str = Field(..., description="스페이스 키")
    expand: Optional[str] = Field(None, description="확장할 필드들")
    
    @field_validator("space_key")
    @classmethod
    def validate_space_key(cls, v):
        if not v or not v.strip():
            raise ValueError("스페이스 키는 비어있을 수 없습니다")
        return v.strip()


class ConfluenceContent(BaseModel):
    """Confluence 콘텐츠 모델"""
    
    id: str = Field(description="콘텐츠 ID")
    title: str = Field(description="제목")
    type: str = Field(description="콘텐츠 타입 (page, blogpost 등)")
    status: str = Field(description="상태")
    space: Optional[Dict[str, Any]] = Field(None, description="스페이스 정보")
    version: Optional[Dict[str, Any]] = Field(None, description="버전 정보")
    body: Optional[Dict[str, Any]] = Field(None, description="본문 내용")
    ancestors: Optional[List[Dict[str, Any]]] = Field(None, description="상위 페이지들")
    children: Optional[Dict[str, Any]] = Field(None, description="하위 페이지들")
    metadata: Optional[Dict[str, Any]] = Field(None, description="메타데이터")
    created_date: Optional[datetime] = Field(None, description="생성일")
    updated_date: Optional[datetime] = Field(None, description="수정일")


class ConfluenceSearchResult(BaseModel):
    """Confluence 검색 결과 모델"""
    
    results: List[ConfluenceContent] = Field(description="검색 결과 목록")
    start: int = Field(description="시작 인덱스")
    limit: int = Field(description="제한 수")
    size: int = Field(description="실제 결과 수")
    total_size: Optional[int] = Field(None, description="전체 결과 수")
    cursor: Optional[str] = Field(None, description="다음 페이지 커서")
    _links: Optional[Dict[str, Any]] = Field(None, description="링크 정보")


class ConfluenceSpace(BaseModel):
    """Confluence 스페이스 모델"""
    
    id: str = Field(description="스페이스 ID")
    key: str = Field(description="스페이스 키")
    name: str = Field(description="스페이스 이름")
    type: str = Field(description="스페이스 타입")
    status: str = Field(description="상태")
    description: Optional[Dict[str, Any]] = Field(None, description="설명")
    homepage: Optional[Dict[str, Any]] = Field(None, description="홈페이지 정보")
    metadata: Optional[Dict[str, Any]] = Field(None, description="메타데이터")
    _links: Optional[Dict[str, Any]] = Field(None, description="링크 정보")


class ConfluenceUser(BaseModel):
    """Confluence 사용자 모델"""
    
    account_id: str = Field(description="계정 ID")
    display_name: str = Field(description="표시 이름")
    email: Optional[str] = Field(None, description="이메일")
    profile_picture: Optional[Dict[str, Any]] = Field(None, description="프로필 사진")
    _links: Optional[Dict[str, Any]] = Field(None, description="링크 정보")


class ConfluenceAttachment(BaseModel):
    """Confluence 첨부파일 모델"""
    
    id: str = Field(description="첨부파일 ID")
    title: str = Field(description="파일명")
    type: str = Field(description="콘텐츠 타입")
    status: str = Field(description="상태")
    metadata: Optional[Dict[str, Any]] = Field(None, description="메타데이터")
    download_link: Optional[str] = Field(None, description="다운로드 링크")
    file_size: Optional[int] = Field(None, description="파일 크기")
    media_type: Optional[str] = Field(None, description="미디어 타입")


class ConfluenceSearchResponse(BaseResponseModel):
    """Confluence 검색 응답 모델"""
    
    data: ConfluenceSearchResult = Field(description="검색 결과 데이터")


class ConfluencePageResponse(BaseResponseModel):
    """Confluence 페이지 응답 모델"""
    
    data: ConfluenceContent = Field(description="페이지 데이터")


class ConfluenceSpaceResponse(BaseResponseModel):
    """Confluence 스페이스 응답 모델"""
    
    data: ConfluenceSpace = Field(description="스페이스 데이터")


class ConfluenceErrorDetail(BaseModel):
    """Confluence 오류 상세 정보"""
    
    message: str = Field(description="오류 메시지")
    status_code: Optional[int] = Field(None, description="HTTP 상태 코드")
    confluence_error_code: Optional[str] = Field(None, description="Confluence 오류 코드")
    request_id: Optional[str] = Field(None, description="요청 ID")
    
    
class ConfluenceStats(BaseModel):
    """Confluence 통계 정보"""
    
    total_requests: int = Field(description="총 요청 수")
    successful_requests: int = Field(description="성공한 요청 수")
    failed_requests: int = Field(description="실패한 요청 수")
    average_response_time: float = Field(description="평균 응답 시간(ms)")
    rate_limit_remaining: Optional[int] = Field(None, description="남은 레이트 리미트")
    last_request_time: Optional[datetime] = Field(None, description="마지막 요청 시간")