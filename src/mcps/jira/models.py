"""JIRA MCP 모델들"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime

from ...shared.models import BaseResponseModel


class JiraIssueRequest(BaseModel):
    """JIRA 이슈 조회 요청 모델"""
    
    issue_key: str = Field(..., description="이슈 키 (예: ABC-123)")
    expand: Optional[str] = Field(None, description="확장할 필드들")
    
    @field_validator("issue_key")
    @classmethod
    def validate_issue_key(cls, v):
        if not v or not v.strip():
            raise ValueError("이슈 키는 비어있을 수 없습니다")
        return v.strip().upper()


class JiraSearchRequest(BaseModel):
    """JIRA 검색 요청 모델"""
    
    jql: str = Field(..., min_length=1, max_length=2000, description="JQL 검색 쿼리")
    start_at: int = Field(default=0, ge=0, description="시작 인덱스")
    max_results: int = Field(default=50, ge=1, le=100, description="최대 결과 수")
    expand: Optional[str] = Field(None, description="확장할 필드들")
    
    @field_validator("jql")
    @classmethod
    def validate_jql(cls, v):
        if not v or not v.strip():
            raise ValueError("JQL 쿼리는 비어있을 수 없습니다")
        
        # 위험한 패턴 검사
        dangerous_patterns = [
            "delete", "drop", "truncate", "update", "insert",
            "script", "javascript", "eval", "exec"
        ]
        
        v_lower = v.lower()
        for pattern in dangerous_patterns:
            if pattern in v_lower:
                raise ValueError(f"금지된 JQL 패턴: {pattern}")
        
        return v.strip()


class JiraProjectRequest(BaseModel):
    """JIRA 프로젝트 조회 요청 모델"""
    
    project_key: str = Field(..., description="프로젝트 키")
    expand: Optional[str] = Field(None, description="확장할 필드들")
    
    @field_validator("project_key")
    @classmethod
    def validate_project_key(cls, v):
        if not v or not v.strip():
            raise ValueError("프로젝트 키는 비어있을 수 없습니다")
        return v.strip().upper()


class JiraUser(BaseModel):
    """JIRA 사용자 모델"""
    
    account_id: str = Field(description="계정 ID")
    display_name: str = Field(description="표시 이름")
    email_address: Optional[str] = Field(None, description="이메일 주소")
    avatar_urls: Optional[Dict[str, str]] = Field(None, description="아바타 URL들")
    active: bool = Field(description="활성 상태")


class JiraIssueType(BaseModel):
    """JIRA 이슈 타입 모델"""
    
    id: str = Field(description="이슈 타입 ID")
    name: str = Field(description="이슈 타입 이름")
    description: Optional[str] = Field(None, description="설명")
    icon_url: Optional[str] = Field(None, description="아이콘 URL")
    subtask: bool = Field(description="서브태스크 여부")


class JiraStatus(BaseModel):
    """JIRA 상태 모델"""
    
    id: str = Field(description="상태 ID")
    name: str = Field(description="상태 이름")
    description: Optional[str] = Field(None, description="설명")
    icon_url: Optional[str] = Field(None, description="아이콘 URL")
    status_category: Optional[Dict[str, Any]] = Field(None, description="상태 카테고리")


class JiraPriority(BaseModel):
    """JIRA 우선순위 모델"""
    
    id: str = Field(description="우선순위 ID")
    name: str = Field(description="우선순위 이름")
    description: Optional[str] = Field(None, description="설명")
    icon_url: Optional[str] = Field(None, description="아이콘 URL")


class JiraProject(BaseModel):
    """JIRA 프로젝트 모델"""
    
    id: str = Field(description="프로젝트 ID")
    key: str = Field(description="프로젝트 키")
    name: str = Field(description="프로젝트 이름")
    description: Optional[str] = Field(None, description="프로젝트 설명")
    project_type_key: str = Field(description="프로젝트 타입")
    lead: Optional[JiraUser] = Field(None, description="프로젝트 리드")
    avatar_urls: Optional[Dict[str, str]] = Field(None, description="아바타 URL들")
    url: Optional[str] = Field(None, description="프로젝트 URL")


class JiraIssueFields(BaseModel):
    """JIRA 이슈 필드 모델"""
    
    summary: str = Field(description="요약")
    description: Optional[str] = Field(None, description="설명")
    issue_type: JiraIssueType = Field(description="이슈 타입")
    status: JiraStatus = Field(description="상태")
    priority: Optional[JiraPriority] = Field(None, description="우선순위")
    project: JiraProject = Field(description="프로젝트")
    assignee: Optional[JiraUser] = Field(None, description="담당자")
    reporter: Optional[JiraUser] = Field(None, description="보고자")
    creator: Optional[JiraUser] = Field(None, description="생성자")
    created: Optional[datetime] = Field(None, description="생성일")
    updated: Optional[datetime] = Field(None, description="수정일")
    resolution_date: Optional[datetime] = Field(None, description="해결일")
    due_date: Optional[datetime] = Field(None, description="마감일")
    labels: List[str] = Field(default=[], description="라벨 목록")
    components: List[Dict[str, Any]] = Field(default=[], description="컴포넌트 목록")
    versions: List[Dict[str, Any]] = Field(default=[], description="영향받는 버전")
    fix_versions: List[Dict[str, Any]] = Field(default=[], description="수정 버전")
    custom_fields: Optional[Dict[str, Any]] = Field(None, description="커스텀 필드")


class JiraIssue(BaseModel):
    """JIRA 이슈 모델"""
    
    id: str = Field(description="이슈 ID")
    key: str = Field(description="이슈 키")
    self: str = Field(description="이슈 URL")
    fields: JiraIssueFields = Field(description="이슈 필드")
    changelog: Optional[Dict[str, Any]] = Field(None, description="변경 이력")


class JiraSearchResult(BaseModel):
    """JIRA 검색 결과 모델"""
    
    expand: str = Field(description="확장된 필드")
    start_at: int = Field(description="시작 인덱스")
    max_results: int = Field(description="최대 결과 수")
    total: int = Field(description="전체 결과 수")
    issues: List[JiraIssue] = Field(description="이슈 목록")


class JiraComment(BaseModel):
    """JIRA 댓글 모델"""
    
    id: str = Field(description="댓글 ID")
    author: JiraUser = Field(description="작성자")
    body: str = Field(description="댓글 내용")
    created: datetime = Field(description="생성일")
    updated: datetime = Field(description="수정일")
    visibility: Optional[Dict[str, Any]] = Field(None, description="가시성 설정")


class JiraAttachment(BaseModel):
    """JIRA 첨부파일 모델"""
    
    id: str = Field(description="첨부파일 ID")
    filename: str = Field(description="파일명")
    author: JiraUser = Field(description="업로드한 사용자")
    created: datetime = Field(description="업로드일")
    size: int = Field(description="파일 크기")
    mime_type: str = Field(description="MIME 타입")
    content: str = Field(description="다운로드 URL")
    thumbnail: Optional[str] = Field(None, description="썸네일 URL")


class JiraIssueResponse(BaseResponseModel):
    """JIRA 이슈 응답 모델"""
    
    data: JiraIssue = Field(description="이슈 데이터")


class JiraSearchResponse(BaseResponseModel):
    """JIRA 검색 응답 모델"""
    
    data: JiraSearchResult = Field(description="검색 결과 데이터")


class JiraProjectResponse(BaseResponseModel):
    """JIRA 프로젝트 응답 모델"""
    
    data: JiraProject = Field(description="프로젝트 데이터")


class JiraStats(BaseModel):
    """JIRA 통계 정보"""
    
    total_requests: int = Field(description="총 요청 수")
    successful_requests: int = Field(description="성공한 요청 수")
    failed_requests: int = Field(description="실패한 요청 수")
    average_response_time: float = Field(description="평균 응답 시간(ms)")
    last_request_time: Optional[datetime] = Field(None, description="마지막 요청 시간")