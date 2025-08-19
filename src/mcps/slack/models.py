"""Slack MCP 모델들"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime

from ...shared.models import BaseResponseModel


class SlackChannelRequest(BaseModel):
    """Slack 채널 조회 요청 모델"""
    
    channel: str = Field(..., description="채널 ID 또는 이름")
    
    @field_validator("channel")
    @classmethod
    def validate_channel(cls, v):
        if not v or not v.strip():
            raise ValueError("채널 정보는 비어있을 수 없습니다")
        return v.strip()


class SlackMessageRequest(BaseModel):
    """Slack 메시지 전송 요청 모델"""
    
    channel: str = Field(..., description="채널 ID 또는 이름")
    text: str = Field(..., min_length=1, max_length=4000, description="메시지 내용")
    thread_ts: Optional[str] = Field(None, description="스레드 타임스탬프")
    
    @field_validator("channel")
    @classmethod
    def validate_channel(cls, v):
        if not v or not v.strip():
            raise ValueError("채널 정보는 비어있을 수 없습니다")
        return v.strip()
    
    @field_validator("text")
    @classmethod
    def validate_text(cls, v):
        if not v or not v.strip():
            raise ValueError("메시지 내용은 비어있을 수 없습니다")
        return v.strip()


class SlackHistoryRequest(BaseModel):
    """Slack 메시지 히스토리 요청 모델"""
    
    channel: str = Field(..., description="채널 ID 또는 이름")
    limit: int = Field(default=100, ge=1, le=1000, description="가져올 메시지 수")
    oldest: Optional[str] = Field(None, description="시작 타임스탬프")
    latest: Optional[str] = Field(None, description="종료 타임스탬프")
    
    @field_validator("channel")
    @classmethod
    def validate_channel(cls, v):
        if not v or not v.strip():
            raise ValueError("채널 정보는 비어있을 수 없습니다")
        return v.strip()


class SlackUser(BaseModel):
    """Slack 사용자 모델"""
    
    id: str = Field(description="사용자 ID")
    name: str = Field(description="사용자 이름")
    real_name: Optional[str] = Field(None, description="실제 이름")
    display_name: Optional[str] = Field(None, description="표시 이름")
    email: Optional[str] = Field(None, description="이메일")
    image_24: Optional[str] = Field(None, description="24x24 프로필 이미지")
    image_32: Optional[str] = Field(None, description="32x32 프로필 이미지")
    image_48: Optional[str] = Field(None, description="48x48 프로필 이미지")
    image_72: Optional[str] = Field(None, description="72x72 프로필 이미지")
    is_bot: bool = Field(default=False, description="봇 여부")
    is_admin: bool = Field(default=False, description="관리자 여부")
    is_deleted: bool = Field(default=False, description="삭제된 사용자 여부")


class SlackChannel(BaseModel):
    """Slack 채널 모델"""
    
    id: str = Field(description="채널 ID")
    name: str = Field(description="채널 이름")
    is_channel: bool = Field(description="채널 여부")
    is_group: bool = Field(description="그룹 여부")
    is_im: bool = Field(description="DM 여부")
    is_private: bool = Field(description="비공개 여부")
    is_archived: bool = Field(description="아카이브 여부")
    is_general: bool = Field(description="일반 채널 여부")
    creator: Optional[str] = Field(None, description="생성자 ID")
    created: Optional[datetime] = Field(None, description="생성일")
    topic: Optional[Dict[str, Any]] = Field(None, description="토픽 정보")
    purpose: Optional[Dict[str, Any]] = Field(None, description="목적 정보")
    num_members: Optional[int] = Field(None, description="멤버 수")


class SlackMessage(BaseModel):
    """Slack 메시지 모델"""
    
    type: str = Field(description="메시지 타입")
    subtype: Optional[str] = Field(None, description="메시지 서브타입")
    text: str = Field(description="메시지 내용")
    user: Optional[str] = Field(None, description="사용자 ID")
    bot_id: Optional[str] = Field(None, description="봇 ID")
    username: Optional[str] = Field(None, description="사용자 이름")
    ts: str = Field(description="타임스탬프")
    thread_ts: Optional[str] = Field(None, description="스레드 타임스탬프")
    parent_user_id: Optional[str] = Field(None, description="부모 사용자 ID")
    reply_count: Optional[int] = Field(None, description="답글 수")
    replies: Optional[List[Dict[str, Any]]] = Field(None, description="답글 목록")
    attachments: Optional[List[Dict[str, Any]]] = Field(None, description="첨부파일")
    blocks: Optional[List[Dict[str, Any]]] = Field(None, description="블록 요소")
    reactions: Optional[List[Dict[str, Any]]] = Field(None, description="반응")
    edited: Optional[Dict[str, Any]] = Field(None, description="편집 정보")


class SlackConversationHistory(BaseModel):
    """Slack 대화 히스토리 모델"""
    
    ok: bool = Field(description="성공 여부")
    messages: List[SlackMessage] = Field(description="메시지 목록")
    has_more: bool = Field(description="더 많은 메시지 존재 여부")
    pin_count: Optional[int] = Field(None, description="고정된 메시지 수")
    response_metadata: Optional[Dict[str, Any]] = Field(None, description="응답 메타데이터")


class SlackPostMessageResponse(BaseModel):
    """Slack 메시지 전송 응답 모델"""
    
    ok: bool = Field(description="성공 여부")
    channel: str = Field(description="채널 ID")
    ts: str = Field(description="메시지 타임스탬프")
    message: SlackMessage = Field(description="전송된 메시지")
    warning: Optional[str] = Field(None, description="경고 메시지")


class SlackChannelInfo(BaseModel):
    """Slack 채널 정보 모델"""
    
    ok: bool = Field(description="성공 여부")
    channel: SlackChannel = Field(description="채널 정보")


class SlackUserInfo(BaseModel):
    """Slack 사용자 정보 모델"""
    
    ok: bool = Field(description="성공 여부")
    user: SlackUser = Field(description="사용자 정보")


class SlackChannelResponse(BaseResponseModel):
    """Slack 채널 응답 모델"""
    
    data: SlackChannelInfo = Field(description="채널 정보 데이터")


class SlackMessageResponse(BaseResponseModel):
    """Slack 메시지 응답 모델"""
    
    data: SlackPostMessageResponse = Field(description="메시지 전송 결과")


class SlackHistoryResponse(BaseResponseModel):
    """Slack 히스토리 응답 모델"""
    
    data: SlackConversationHistory = Field(description="대화 히스토리 데이터")


class SlackUserResponse(BaseResponseModel):
    """Slack 사용자 응답 모델"""
    
    data: SlackUserInfo = Field(description="사용자 정보 데이터")


class SlackStats(BaseModel):
    """Slack 통계 정보"""
    
    total_requests: int = Field(description="총 요청 수")
    successful_requests: int = Field(description="성공한 요청 수")
    failed_requests: int = Field(description="실패한 요청 수")
    average_response_time: float = Field(description="평균 응답 시간(ms)")
    messages_sent: int = Field(default=0, description="전송한 메시지 수")
    channels_accessed: int = Field(default=0, description="접근한 채널 수")
    last_request_time: Optional[datetime] = Field(None, description="마지막 요청 시간")


class SlackError(BaseModel):
    """Slack 오류 모델"""
    
    ok: bool = Field(default=False, description="성공 여부")
    error: str = Field(description="오류 코드")
    warning: Optional[str] = Field(None, description="경고 메시지")
    response_metadata: Optional[Dict[str, Any]] = Field(None, description="응답 메타데이터")