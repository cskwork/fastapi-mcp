"""Calculator MCP 라우터"""

import math
import time
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
import structlog
from datetime import datetime

from ...shared.utils import format_error_response, create_success_response
from ...shared.exceptions import MCPBaseException
from ...shared.auth import get_optional_user
from .config import calculator_config
from .models import (
    BasicCalculationRequest,
    SingleNumberRequest,
    MultiNumberRequest,
    ExpressionRequest,
    BasicCalculationResponse,
    MultiCalculationResponse,
    HistoryResponse,
    StatsResponse,
    CalculationResult,
    CalculationHistory,
    CalculatorStats,
    CalculatorErrorDetail
)

logger = structlog.get_logger(__name__)

router = APIRouter(tags=["calculator"])

# 간단한 인메모리 저장소 (실제 환경에서는 Redis나 DB 사용)
calculation_history: List[CalculationHistory] = []
calculation_stats = {
    "total": 0,
    "successful": 0,
    "failed": 0,
    "operations": {},
    "total_time": 0.0
}


def _add_to_history(operation: str, input_values, result: float):
    """계산 기록 추가"""
    if not calculator_config.enable_history:
        return
    
    history_item = CalculationHistory(
        operation=operation,
        input_values=input_values,
        result=result,
        timestamp=datetime.now().isoformat()
    )
    
    calculation_history.append(history_item)
    
    # 최대 기록 수 제한
    if len(calculation_history) > calculator_config.max_history_size:
        calculation_history.pop(0)


def _update_stats(operation: str, success: bool, execution_time: float):
    """통계 업데이트"""
    if not calculator_config.enable_stats:
        return
    
    calculation_stats["total"] += 1
    if success:
        calculation_stats["successful"] += 1
    else:
        calculation_stats["failed"] += 1
    
    if operation not in calculation_stats["operations"]:
        calculation_stats["operations"][operation] = 0
    calculation_stats["operations"][operation] += 1
    
    calculation_stats["total_time"] += execution_time


def _perform_basic_calculation(a: float, b: float, operation: str) -> float:
    """기본 이항 연산 수행"""
    if operation == "add":
        return a + b
    elif operation == "subtract":
        return a - b
    elif operation == "multiply":
        return a * b
    elif operation == "divide":
        if b == 0:
            raise ValueError("0으로 나눌 수 없습니다")
        return a / b
    elif operation == "power":
        return pow(a, b)
    elif operation == "modulo":
        if b == 0:
            raise ValueError("0으로 나눌 수 없습니다")
        return a % b
    else:
        raise ValueError(f"지원하지 않는 연산입니다: {operation}")


def _safe_eval_expression(expression: str) -> float:
    """안전한 수식 계산"""
    # 보안을 위해 허용된 문자만 포함하는지 재확인
    allowed_chars = set(calculator_config.get_allowed_expression_chars())
    if not all(c in allowed_chars for c in expression):
        raise ValueError("수식에 허용되지 않은 문자가 포함되어 있습니다")
    
    try:
        # eval 대신 안전한 방법으로 계산 (간단한 경우만)
        # 실제로는 더 안전한 파서를 사용해야 함
        result = eval(expression, {"__builtins__": {}}, {})
        if not isinstance(result, (int, float)):
            raise ValueError("유효하지 않은 수식입니다")
        return float(result)
    except Exception as e:
        raise ValueError(f"수식 계산 중 오류: {str(e)}")


@router.post("/calculate", 
            response_model=BasicCalculationResponse,
            operation_id="calculator_basic_calculation",
            summary="기본 계산 수행",
            description="두 숫자로 기본적인 수학 연산을 수행합니다")
async def basic_calculation(
    request: BasicCalculationRequest,
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """기본 계산 수행"""
    
    start_time = time.time()
    operation = request.operation.value
    
    try:
        logger.info(
            "Basic calculation requested",
            a=request.a,
            b=request.b,
            operation=operation,
            user_id=user.get("sub") if user else None
        )
        
        result = _perform_basic_calculation(request.a, request.b, operation)
        
        # 결과 검증
        if abs(result) > calculator_config.max_number_size:
            raise ValueError("계산 결과가 너무 큽니다")
        
        calculation_result = CalculationResult(
            result=round(result, calculator_config.max_precision),
            operation=f"{request.a} {operation} {request.b}",
            input_values=[request.a, request.b],
            is_valid=True,
            precision=calculator_config.max_precision
        )
        
        execution_time = (time.time() - start_time) * 1000
        _add_to_history(operation, [request.a, request.b], result)
        _update_stats(operation, True, execution_time)
        
        logger.info(
            "Basic calculation completed",
            result=result,
            execution_time_ms=execution_time
        )
        
        return create_success_response(calculation_result)
        
    except Exception as e:
        execution_time = (time.time() - start_time) * 1000
        _update_stats(operation, False, execution_time)
        
        logger.error(
            "Basic calculation failed",
            error=str(e),
            a=request.a,
            b=request.b,
            operation=operation
        )
        
        raise HTTPException(
            status_code=400,
            detail=format_error_response(
                message=str(e),
                error_type="CalculationError"
            )
        )


@router.post("/sqrt", 
            response_model=BasicCalculationResponse,
            operation_id="calculator_square_root",
            summary="제곱근 계산",
            description="숫자의 제곱근을 계산합니다")
async def square_root(
    request: SingleNumberRequest,
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """제곱근 계산"""
    
    start_time = time.time()
    operation = "sqrt"
    
    try:
        logger.info(
            "Square root calculation requested",
            number=request.number,
            user_id=user.get("sub") if user else None
        )
        
        if request.number < 0:
            raise ValueError("음수의 제곱근은 계산할 수 없습니다")
        
        result = math.sqrt(request.number)
        
        calculation_result = CalculationResult(
            result=round(result, calculator_config.max_precision),
            operation=f"√{request.number}",
            input_values=[request.number],
            is_valid=True,
            precision=calculator_config.max_precision
        )
        
        execution_time = (time.time() - start_time) * 1000
        _add_to_history(operation, [request.number], result)
        _update_stats(operation, True, execution_time)
        
        return create_success_response(calculation_result)
        
    except Exception as e:
        execution_time = (time.time() - start_time) * 1000
        _update_stats(operation, False, execution_time)
        
        logger.error(
            "Square root calculation failed",
            error=str(e),
            number=request.number
        )
        
        raise HTTPException(
            status_code=400,
            detail=format_error_response(
                message=str(e),
                error_type="CalculationError"
            )
        )


@router.post("/expression", 
            response_model=BasicCalculationResponse,
            operation_id="calculator_evaluate_expression",
            summary="수식 계산",
            description="수학 수식을 계산합니다")
async def evaluate_expression(
    request: ExpressionRequest,
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """수식 계산"""
    
    start_time = time.time()
    operation = "expression"
    
    try:
        logger.info(
            "Expression evaluation requested",
            expression=request.expression,
            user_id=user.get("sub") if user else None
        )
        
        result = _safe_eval_expression(request.expression)
        
        if abs(result) > calculator_config.max_number_size:
            raise ValueError("계산 결과가 너무 큽니다")
        
        calculation_result = CalculationResult(
            result=round(result, calculator_config.max_precision),
            operation=request.expression,
            input_values=request.expression,
            is_valid=True,
            precision=calculator_config.max_precision
        )
        
        execution_time = (time.time() - start_time) * 1000
        _add_to_history(operation, request.expression, result)
        _update_stats(operation, True, execution_time)
        
        return create_success_response(calculation_result)
        
    except Exception as e:
        execution_time = (time.time() - start_time) * 1000
        _update_stats(operation, False, execution_time)
        
        logger.error(
            "Expression evaluation failed",
            error=str(e),
            expression=request.expression
        )
        
        raise HTTPException(
            status_code=400,
            detail=format_error_response(
                message=str(e),
                error_type="ExpressionError"
            )
        )


@router.get("/history", 
           response_model=HistoryResponse,
           operation_id="calculator_get_history",
           summary="계산 기록 조회",
           description="최근 계산 기록을 조회합니다")
async def get_calculation_history(
    limit: int = Query(10, description="조회할 기록 수", ge=1, le=100),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """계산 기록 조회"""
    
    try:
        logger.info(
            "Calculation history requested",
            limit=limit,
            user_id=user.get("sub") if user else None
        )
        
        # 최신 기록부터 반환
        recent_history = calculation_history[-limit:] if len(calculation_history) >= limit else calculation_history
        recent_history.reverse()
        
        return create_success_response(recent_history)
        
    except Exception as e:
        logger.error(
            "Failed to get calculation history",
            error=str(e)
        )
        
        raise HTTPException(
            status_code=500,
            detail=format_error_response(
                message="계산 기록을 가져오는 중 오류가 발생했습니다",
                error_type="HistoryError"
            )
        )


@router.get("/stats", 
           response_model=StatsResponse,
           operation_id="calculator_get_stats",
           summary="계산기 통계 조회",
           description="계산기 사용 통계를 조회합니다")
async def get_calculator_stats(
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """계산기 통계 조회"""
    
    try:
        logger.info(
            "Calculator stats requested",
            user_id=user.get("sub") if user else None
        )
        
        # 가장 많이 사용된 연산 찾기
        most_used_operation = "없음"
        if calculation_stats["operations"]:
            most_used_operation = max(
                calculation_stats["operations"].items(),
                key=lambda x: x[1]
            )[0]
        
        # 평균 계산 시간
        avg_time = 0.0
        if calculation_stats["total"] > 0:
            avg_time = calculation_stats["total_time"] / calculation_stats["total"]
        
        stats = CalculatorStats(
            total_calculations=calculation_stats["total"],
            successful_calculations=calculation_stats["successful"],
            failed_calculations=calculation_stats["failed"],
            most_used_operation=most_used_operation,
            average_calculation_time=round(avg_time, 2)
        )
        
        return create_success_response(stats)
        
    except Exception as e:
        logger.error(
            "Failed to get calculator stats",
            error=str(e)
        )
        
        raise HTTPException(
            status_code=500,
            detail=format_error_response(
                message="통계를 가져오는 중 오류가 발생했습니다",
                error_type="StatsError"
            )
        )


@router.delete("/history", 
              operation_id="calculator_clear_history",
              summary="계산 기록 삭제",
              description="모든 계산 기록을 삭제합니다")
async def clear_calculation_history(
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """계산 기록 삭제"""
    
    try:
        logger.info(
            "Clear calculation history requested",
            user_id=user.get("sub") if user else None
        )
        
        calculation_history.clear()
        
        return create_success_response({"message": "계산 기록이 삭제되었습니다"})
        
    except Exception as e:
        logger.error(
            "Failed to clear calculation history",
            error=str(e)
        )
        
        raise HTTPException(
            status_code=500,
            detail=format_error_response(
                message="기록 삭제 중 오류가 발생했습니다",
                error_type="HistoryError"
            )
        )