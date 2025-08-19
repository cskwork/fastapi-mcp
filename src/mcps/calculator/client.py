"""Calculator MCP 클라이언트 (로컬 계산용)"""

import asyncio
from typing import Optional, Dict, Any
import structlog

from .config import calculator_config

logger = structlog.get_logger(__name__)


class CalculatorClient:
    """계산기 클라이언트 (로컬 계산 수행)"""
    
    def __init__(self):
        self.config = calculator_config
        self.is_healthy = True
        
    async def health_check(self) -> Dict[str, Any]:
        """헬스체크 (항상 정상)"""
        return {
            "status": "healthy",
            "service": "calculator",
            "timestamp": asyncio.get_event_loop().time(),
            "config_valid": self.config.validate_config()
        }
    
    async def get_service_info(self) -> Dict[str, Any]:
        """서비스 정보 반환"""
        return {
            "name": "Calculator MCP Service",
            "version": "1.0.0",
            "description": "로컬 수학 계산 서비스",
            "capabilities": [
                "기본 사칙연산",
                "제곱근 계산", 
                "수식 계산",
                "계산 기록 관리",
                "통계 수집"
            ],
            "supported_operations": self.config.get_allowed_operations(),
            "limits": {
                "max_precision": self.config.max_precision,
                "max_number_size": self.config.max_number_size,
                "max_expression_length": self.config.max_expression_length,
                "max_history_size": self.config.max_history_size
            }
        }


# 전역 클라이언트 인스턴스
_calculator_client: Optional[CalculatorClient] = None


def get_calculator_client() -> CalculatorClient:
    """계산기 클라이언트 인스턴스 반환"""
    global _calculator_client
    
    if _calculator_client is None:
        _calculator_client = CalculatorClient()
        logger.info("Calculator client initialized")
    
    return _calculator_client


async def initialize_calculator_client() -> Optional[CalculatorClient]:
    """계산기 클라이언트 초기화"""
    try:
        client = get_calculator_client()
        health = await client.health_check()
        
        if health["status"] == "healthy":
            logger.info("Calculator client initialized successfully")
            return client
        else:
            logger.error("Calculator client health check failed", health=health)
            return None
            
    except Exception as e:
        logger.error("Failed to initialize calculator client", error=str(e))
        return None