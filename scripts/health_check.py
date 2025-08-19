#!/usr/bin/env python3
"""헬스체크 스크립트"""

import asyncio
import sys
import time
from typing import Dict, Any
import httpx
import json


class HealthChecker:
    """헬스체크 수행자"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(timeout=10.0)
    
    async def check_main_health(self) -> Dict[str, Any]:
        """메인 헬스체크"""
        try:
            response = await self.client.get(f"{self.base_url}/health")
            response.raise_for_status()
            return {
                "status": "healthy",
                "response_time": response.elapsed.total_seconds() * 1000,
                "data": response.json()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def check_service_health(self, service: str) -> Dict[str, Any]:
        """개별 서비스 헬스체크"""
        try:
            response = await self.client.get(f"{self.base_url}/{service}/health")
            response.raise_for_status()
            return {
                "status": "healthy",
                "response_time": response.elapsed.total_seconds() * 1000,
                "data": response.json()
            }
        except httpx.HTTPStatusError as e:
            return {
                "status": "unhealthy" if e.response.status_code >= 500 else "unavailable",
                "status_code": e.response.status_code,
                "error": f"HTTP {e.response.status_code}"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def check_root_endpoint(self) -> Dict[str, Any]:
        """루트 엔드포인트 확인"""
        try:
            response = await self.client.get(f"{self.base_url}/")
            response.raise_for_status()
            return {
                "status": "healthy",
                "response_time": response.elapsed.total_seconds() * 1000,
                "data": response.json()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def full_health_check(self) -> Dict[str, Any]:
        """전체 헬스체크"""
        results = {
            "timestamp": time.time(),
            "overall_status": "healthy",
            "checks": {}
        }
        
        # 루트 엔드포인트 체크
        print("🔍 루트 엔드포인트 확인 중...")
        root_result = await self.check_root_endpoint()
        results["checks"]["root"] = root_result
        
        if root_result["status"] != "healthy":
            results["overall_status"] = "unhealthy"
            return results
        
        # 메인 헬스체크
        print("🏥 메인 헬스체크 수행 중...")
        main_result = await self.check_main_health()
        results["checks"]["main"] = main_result
        
        if main_result["status"] != "healthy":
            results["overall_status"] = "unhealthy"
            return results
        
        # 활성화된 서비스 목록 가져오기
        try:
            enabled_services = main_result["data"]["data"]["services"].keys()
            print(f"📋 활성화된 서비스: {', '.join(enabled_services)}")
        except (KeyError, TypeError):
            enabled_services = ["confluence", "jira", "slack"]  # 기본값
        
        # 개별 서비스 헬스체크
        unhealthy_services = []
        for service in enabled_services:
            print(f"🔧 {service} 서비스 헬스체크 중...")
            service_result = await self.check_service_health(service)
            results["checks"][service] = service_result
            
            if service_result["status"] == "unhealthy":
                unhealthy_services.append(service)
        
        # 전체 상태 결정
        if unhealthy_services:
            results["overall_status"] = "degraded"
            results["unhealthy_services"] = unhealthy_services
        
        return results
    
    async def close(self):
        """클라이언트 종료"""
        await self.client.aclose()


def print_results(results: Dict[str, Any]):
    """결과 출력"""
    print("\n" + "="*60)
    print("🏥 AIDT MCP 헬스체크 결과")
    print("="*60)
    
    # 전체 상태
    status_emoji = {
        "healthy": "✅",
        "degraded": "⚠️",
        "unhealthy": "❌"
    }
    
    overall_status = results["overall_status"]
    print(f"\n전체 상태: {status_emoji.get(overall_status, '❓')} {overall_status.upper()}")
    
    # 개별 체크 결과
    print(f"\n📊 개별 체크 결과:")
    for check_name, check_result in results["checks"].items():
        status = check_result["status"]
        emoji = status_emoji.get(status, "❓")
        
        if "response_time" in check_result:
            time_ms = check_result["response_time"]
            print(f"  {emoji} {check_name}: {status} ({time_ms:.1f}ms)")
        else:
            print(f"  {emoji} {check_name}: {status}")
        
        if "error" in check_result:
            print(f"      오류: {check_result['error']}")
    
    # 상세 정보
    if "unhealthy_services" in results:
        print(f"\n⚠️  문제가 있는 서비스: {', '.join(results['unhealthy_services'])}")
    
    print(f"\n⏰ 체크 시간: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(results['timestamp']))}")


async def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AIDT MCP 헬스체크")
    parser.add_argument(
        "--url", 
        default="http://localhost:8000",
        help="서버 URL (기본값: http://localhost:8000)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="JSON 형식으로 결과 출력"
    )
    parser.add_argument(
        "--exit-code",
        action="store_true",
        help="헬스체크 실패 시 1 종료 코드 반환"
    )
    
    args = parser.parse_args()
    
    checker = HealthChecker(args.url)
    
    try:
        results = await checker.full_health_check()
        
        if args.json:
            print(json.dumps(results, indent=2, ensure_ascii=False))
        else:
            print_results(results)
        
        # 종료 코드 설정
        if args.exit_code and results["overall_status"] != "healthy":
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n❌ 헬스체크가 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 헬스체크 중 오류 발생: {e}")
        sys.exit(1)
    finally:
        await checker.close()


if __name__ == "__main__":
    asyncio.run(main())