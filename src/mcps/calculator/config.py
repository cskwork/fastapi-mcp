"""Calculator MCP 설정"""

from typing import Dict, Any


class CalculatorConfig:
    """Calculator 설정 관리자"""
    
    def __init__(self):
        # Calculator는 외부 API 호출이 없으므로 설정이 단순합니다
        self.max_precision = 15  # 최대 소수점 자릿수
        self.max_number_size = 1e15  # 최대 숫자 크기
        self.max_expression_length = 200  # 최대 수식 길이
        self.max_history_size = 100  # 최대 기록 보관 수
        self.timeout = 5.0  # 계산 타임아웃 (초)
        self.enable_history = True  # 기록 저장 여부
        self.enable_stats = True  # 통계 수집 여부
    
    @property
    def validation_config(self) -> Dict[str, Any]:
        """유효성 검증 설정"""
        return {
            "max_precision": self.max_precision,
            "max_number_size": self.max_number_size,
            "max_expression_length": self.max_expression_length
        }
    
    @property
    def operation_limits(self) -> Dict[str, Any]:
        """연산별 제한 설정"""
        return {
            "division_by_zero_check": True,
            "sqrt_negative_check": True,
            "overflow_check": True,
            "underflow_check": True
        }
    
    def get_allowed_operations(self) -> list:
        """허용된 연산 목록"""
        return [
            "add", "subtract", "multiply", "divide", 
            "power", "sqrt", "modulo"
        ]
    
    def get_allowed_expression_chars(self) -> str:
        """수식에서 허용된 문자들"""
        return "0123456789+-*/()., "
    
    def validate_config(self) -> bool:
        """설정 유효성 검증"""
        if self.max_precision < 1 or self.max_precision > 20:
            return False
        
        if self.max_number_size <= 0:
            return False
        
        if self.max_expression_length < 1:
            return False
        
        if self.timeout <= 0:
            return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """설정을 딕셔너리로 변환"""
        return {
            "max_precision": self.max_precision,
            "max_number_size": self.max_number_size,
            "max_expression_length": self.max_expression_length,
            "max_history_size": self.max_history_size,
            "timeout": self.timeout,
            "enable_history": self.enable_history,
            "enable_stats": self.enable_stats,
            "allowed_operations": self.get_allowed_operations(),
            "allowed_expression_chars": self.get_allowed_expression_chars()
        }


# 전역 설정 인스턴스 (항상 사용 가능)
calculator_config = CalculatorConfig()