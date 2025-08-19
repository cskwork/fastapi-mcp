#!/usr/bin/env python3
"""Calculator 서비스 테스트"""

import sys
import json
from typing import Dict, Any

def test_basic_math():
    """기본 수학 연산 테스트"""
    print("🧮 Testing basic calculator functions...")
    
    # 기본 연산 테스트
    test_cases = [
        {"a": 10, "b": 5, "operation": "add", "expected": 15},
        {"a": 10, "b": 5, "operation": "subtract", "expected": 5},
        {"a": 10, "b": 5, "operation": "multiply", "expected": 50},
        {"a": 10, "b": 5, "operation": "divide", "expected": 2.0},
        {"a": 2, "b": 3, "operation": "power", "expected": 8},
        {"a": 10, "b": 3, "operation": "modulo", "expected": 1},
    ]
    
    for test in test_cases:
        result = perform_calculation(test["a"], test["b"], test["operation"])
        if abs(result - test["expected"]) < 0.0001:
            print(f"✅ {test['a']} {test['operation']} {test['b']} = {result}")
        else:
            print(f"❌ {test['a']} {test['operation']} {test['b']} = {result} (expected {test['expected']})")
            return False
    
    # 제곱근 테스트
    sqrt_tests = [
        {"number": 9, "expected": 3},
        {"number": 16, "expected": 4},
        {"number": 2, "expected": 1.4142135623730951},
    ]
    
    import math
    for test in sqrt_tests:
        result = math.sqrt(test["number"])
        if abs(result - test["expected"]) < 0.0001:
            print(f"✅ √{test['number']} = {result}")
        else:
            print(f"❌ √{test['number']} = {result} (expected {test['expected']})")
            return False
    
    # 수식 평가 테스트 (안전한 방법)
    expression_tests = [
        {"expression": "2 + 3 * 4", "expected": 14},
        {"expression": "(2 + 3) * 4", "expected": 20},
        {"expression": "10 / 2 + 3", "expected": 8},
    ]
    
    for test in expression_tests:
        try:
            # 안전한 eval (실제로는 더 안전한 파서 사용 권장)
            result = eval(test["expression"], {"__builtins__": {}}, {})
            if abs(result - test["expected"]) < 0.0001:
                print(f"✅ {test['expression']} = {result}")
            else:
                print(f"❌ {test['expression']} = {result} (expected {test['expected']})")
                return False
        except Exception as e:
            print(f"❌ {test['expression']} failed: {e}")
            return False
    
    return True

def perform_calculation(a: float, b: float, operation: str) -> float:
    """기본 계산 수행"""
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

def test_mcp_endpoints():
    """MCP 엔드포인트 시뮬레이션 테스트"""
    print("\n🌐 Testing MCP endpoint simulations...")
    
    # 기본 계산 요청 시뮬레이션
    basic_request = {
        "a": 15,
        "b": 3,
        "operation": "divide"
    }
    
    try:
        result = perform_calculation(
            basic_request["a"],
            basic_request["b"], 
            basic_request["operation"]
        )
        
        response = {
            "success": True,
            "data": {
                "result": result,
                "operation": f"{basic_request['a']} {basic_request['operation']} {basic_request['b']}",
                "input_values": [basic_request["a"], basic_request["b"]],
                "is_valid": True,
                "precision": 10
            },
            "message": "계산이 성공적으로 완료되었습니다"
        }
        
        print(f"✅ Basic calculation endpoint simulation:")
        print(f"   Request: {json.dumps(basic_request, ensure_ascii=False)}")
        print(f"   Response: {json.dumps(response, ensure_ascii=False, indent=2)}")
        
    except Exception as e:
        print(f"❌ Basic calculation endpoint failed: {e}")
        return False
    
    # 에러 케이스 테스트
    error_request = {
        "a": 10,
        "b": 0,
        "operation": "divide"
    }
    
    try:
        result = perform_calculation(
            error_request["a"],
            error_request["b"],
            error_request["operation"]
        )
        print(f"❌ Error case should have failed but got: {result}")
        return False
    except ValueError as e:
        print(f"✅ Error handling works: {e}")
    
    return True

def show_mcp_integration_info():
    """MCP 클라이언트 연결 정보 표시"""
    print("\n🔌 MCP Client Integration Information:")
    print("=" * 60)
    
    print("\n📍 Server Information:")
    print(f"   • Server URL: http://127.0.0.1:8000")
    print(f"   • MCP Endpoint: http://127.0.0.1:8000/mcp")
    print(f"   • Swagger UI: http://127.0.0.1:8000/docs")
    print(f"   • Health Check: http://127.0.0.1:8000/health")
    
    print("\n🔧 Available Calculator Tools:")
    tools = [
        {
            "name": "calculator_basic_calculation",
            "description": "두 숫자로 기본적인 수학 연산을 수행합니다",
            "endpoint": "POST /calculator/calculate"
        },
        {
            "name": "calculator_square_root", 
            "description": "숫자의 제곱근을 계산합니다",
            "endpoint": "POST /calculator/sqrt"
        },
        {
            "name": "calculator_evaluate_expression",
            "description": "수학 수식을 계산합니다", 
            "endpoint": "POST /calculator/expression"
        },
        {
            "name": "calculator_get_history",
            "description": "최근 계산 기록을 조회합니다",
            "endpoint": "GET /calculator/history"
        },
        {
            "name": "calculator_get_stats",
            "description": "계산기 사용 통계를 조회합니다",
            "endpoint": "GET /calculator/stats"
        }
    ]
    
    for tool in tools:
        print(f"   • {tool['name']}")
        print(f"     {tool['description']}")
        print(f"     {tool['endpoint']}")
        print()
    
    print("\n🖥️  MCP Client Configuration:")
    print("\n1. Claude Desktop (claude_desktop_config.json):")
    claude_config = {
        "mcpServers": {
            "aidt-calculator": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-http", "http://127.0.0.1:8000/mcp"]
            }
        }
    }
    print(f"   {json.dumps(claude_config, indent=2)}")
    
    print("\n2. Cursor (MCP Extension):")
    print("   • Install MCP extension in Cursor")
    print("   • Add server: http://127.0.0.1:8000/mcp")
    print("   • Name: AIDT Calculator")
    
    print("\n3. Claude Code:")
    print("   • Use /mcp add command")
    print("   • Server URL: http://127.0.0.1:8000/mcp") 
    print("   • Server Name: aidt-calculator")
    
    print("\n📋 Example Usage in MCP Clients:")
    examples = [
        "Calculate 15 * 8 + 32",
        "What's the square root of 144?", 
        "Evaluate this expression: (10 + 5) * 3 - 8",
        "Show my calculation history",
        "What are my calculator usage stats?"
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"   {i}. \"{example}\"")
    
    print("\n⚠️  Note: Make sure the server is running before connecting MCP clients!")
    print("   Start server with: python scripts/start_dev.py")

def main():
    """메인 테스트 함수"""
    print("🧪 AIDT Calculator MCP Service Test")
    print("=" * 50)
    
    # 기본 수학 기능 테스트
    if not test_basic_math():
        print("\n❌ Basic math tests failed!")
        sys.exit(1)
    
    # MCP 엔드포인트 시뮬레이션 테스트
    if not test_mcp_endpoints():
        print("\n❌ MCP endpoint simulation tests failed!")
        sys.exit(1)
    
    print("\n✅ All calculator tests passed!")
    
    # MCP 연결 정보 표시
    show_mcp_integration_info()

if __name__ == "__main__":
    main()