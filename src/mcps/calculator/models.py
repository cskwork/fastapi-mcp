"""Calculator MCP 모델들"""

from typing import List, Union
from pydantic import BaseModel, Field, field_validator
from enum import Enum

from ...shared.models import BaseResponseModel


class CalculatorOperation(str, Enum):
    """계산기 연산 타입"""
    ADD = "add"
    SUBTRACT = "subtract"
    MULTIPLY = "multiply"
    DIVIDE = "divide"
    POWER = "power"
    SQRT = "sqrt"
    MODULO = "modulo"


class BasicCalculationRequest(BaseModel):
    """기본 계산 요청 모델"""
    
    a: float = Field(..., description="첫 번째 수")
    b: float = Field(..., description="두 번째 수")
    operation: CalculatorOperation = Field(..., description="수행할 연산")
    
    @field_validator("b")
    @classmethod
    def validate_division_by_zero(cls, v, info):
        # 나눗셈이나 모듈로 연산에서 0으로 나누는 것 방지
        if hasattr(info, 'data') and info.data.get('operation') in ['divide', 'modulo'] and v == 0:
            raise ValueError("0으로 나눌 수 없습니다")
        return v


class SingleNumberRequest(BaseModel):
    """단일 수 계산 요청 모델 (제곱근 등)"""
    
    number: float = Field(..., description="계산할 수")
    
    @field_validator("number")
    @classmethod
    def validate_sqrt_positive(cls, v):
        # 제곱근의 경우 양수만 허용
        if v < 0:
            raise ValueError("제곱근은 양수만 계산할 수 있습니다")
        return v


class MultiNumberRequest(BaseModel):
    """다중 수 계산 요청 모델"""
    
    numbers: List[float] = Field(..., min_items=2, max_items=10, description="계산할 숫자들")
    operation: CalculatorOperation = Field(..., description="수행할 연산")
    
    @field_validator("numbers")
    @classmethod
    def validate_numbers(cls, v):
        if not v:
            raise ValueError("최소 하나의 숫자가 필요합니다")
        # 매우 큰 수나 작은 수 제한
        for num in v:
            if abs(num) > 1e15:
                raise ValueError("너무 큰 수는 계산할 수 없습니다")
        return v


class ExpressionRequest(BaseModel):
    """수식 계산 요청 모델"""
    
    expression: str = Field(..., min_length=1, max_length=200, description="계산할 수식")
    
    @field_validator("expression")
    @classmethod
    def validate_expression(cls, v):
        if not v or not v.strip():
            raise ValueError("수식은 비어있을 수 없습니다")
        
        # 허용된 문자만 포함하는지 확인 (보안을 위해)
        allowed_chars = set("0123456789+-*/()., ")
        if not all(c in allowed_chars for c in v):
            raise ValueError("수식에 허용되지 않은 문자가 포함되어 있습니다")
        
        # 괄호 균형 확인
        if v.count('(') != v.count(')'):
            raise ValueError("괄호가 맞지 않습니다")
        
        return v.strip()


class CalculationResult(BaseModel):
    """계산 결과 모델"""
    
    result: float = Field(description="계산 결과")
    operation: str = Field(description="수행된 연산")
    input_values: Union[List[float], str] = Field(description="입력 값들")
    is_valid: bool = Field(default=True, description="결과 유효성")
    precision: int = Field(default=10, description="소수점 이하 자릿수")
    
    @field_validator("result")
    @classmethod
    def validate_result(cls, v):
        # NaN이나 무한대 체크
        if str(v).lower() in ['nan', 'inf', '-inf']:
            raise ValueError("유효하지 않은 계산 결과입니다")
        return v


class CalculationHistory(BaseModel):
    """계산 기록 모델"""
    
    operation: str = Field(description="수행된 연산")
    input_values: Union[List[float], str] = Field(description="입력 값들")
    result: float = Field(description="계산 결과")
    timestamp: str = Field(description="계산 시간")


class CalculatorStats(BaseModel):
    """계산기 통계 모델"""
    
    total_calculations: int = Field(description="총 계산 수")
    successful_calculations: int = Field(description="성공한 계산 수")
    failed_calculations: int = Field(description="실패한 계산 수")
    most_used_operation: str = Field(description="가장 많이 사용된 연산")
    average_calculation_time: float = Field(description="평균 계산 시간(ms)")


class BasicCalculationResponse(BaseResponseModel):
    """기본 계산 응답 모델"""
    
    data: CalculationResult = Field(description="계산 결과 데이터")


class MultiCalculationResponse(BaseResponseModel):
    """다중 계산 응답 모델"""
    
    data: List[CalculationResult] = Field(description="계산 결과 목록")


class HistoryResponse(BaseResponseModel):
    """계산 기록 응답 모델"""
    
    data: List[CalculationHistory] = Field(description="계산 기록 목록")


class StatsResponse(BaseResponseModel):
    """통계 응답 모델"""
    
    data: CalculatorStats = Field(description="계산기 통계 데이터")


class CalculatorErrorDetail(BaseModel):
    """계산기 오류 상세 정보"""
    
    message: str = Field(description="오류 메시지")
    error_type: str = Field(description="오류 타입")
    invalid_input: Union[str, float, List[float], None] = Field(None, description="잘못된 입력값")
    suggestion: str = Field(description="해결 방법 제안")