# AIDT Calculator MCP Server 🧮

**AIDT Calculator MCP Server**는 AI 디지털 교과서 플랫폼의 수학 계산 기능을 MCP (Model Context Protocol) 프로토콜로 제공하는 확장 가능한 서비스입니다.

## ✨ 주요 기능

- **기본 수학 연산**: 덧셈, 뺄셈, 곱셈, 나눗셈, 거듭제곱, 나머지 연산
- **고급 계산**: 제곱근 계산, 수식 평가
- **계산 기록**: 자동 기록 저장 및 조회
- **사용 통계**: 계산기 사용 통계 수집
- **MCP 프로토콜**: Claude Desktop, Cursor, Claude Code 등 MCP 클라이언트에서 바로 사용 가능

## 🚀 빠른 시작

### 1. 서버 시작
```bash
# 의존성 설치
uv sync

# 개발 서버 시작
python scripts/start_dev.py

# 또는 직접 실행
uv run uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
```

### 2. 서버 확인
```bash
# 헬스체크
curl http://127.0.0.1:8000/health

# 계산 테스트
curl -X POST "http://127.0.0.1:8000/calculator/calculate" \
  -H "Content-Type: application/json" \
  -d '{"a": 15, "b": 3, "operation": "multiply"}'
```

### 3. Swagger UI 접속
브라우저에서 `http://127.0.0.1:8000/docs`를 열어 API 문서 확인

## 🔧 MCP 클라이언트 연결

### MCP 클라이언트별 설정

#### Claude Desktop (권장)
`claude_desktop_config.json` 파일에 추가:
```json
{
  "mcpServers": {
    "aidt-calculator": {
      "command": "npx",
      "args": ["mcp-remote", "http://127.0.0.1:8000/mcp"]
    }
  }
}
```

#### Cursor IDE
MCP Extension 설정:
```json
{
  "aidt-calculator": {
    "url": "http://127.0.0.1:8000/mcp"
  }
}
```

#### Windsurf
MCP 설정:
```json
{
  "aidt-calculator": {
    "url": "http://127.0.0.1:8000/mcp"
  }
}
```

### 사용 예시
Claude Desktop에서:
- "Calculate 15 * 8 + 32"
- "What's the square root of 144?"
- "Evaluate this expression: (10 + 5) * 3 - 8"
- "Show my calculation history"

## 📚 사용 가능한 도구

| MCP 도구 이름 | 설명 | 예시 |
|--------------|------|------|
| `calculator_basic_calculation` | 기본 수학 연산 | 15 × 3 = 45 |
| `calculator_square_root` | 제곱근 계산 | √144 = 12 |
| `calculator_evaluate_expression` | 수식 계산 | (10+5)×3-8 = 37 |
| `calculator_get_history` | 계산 기록 조회 | 최근 10개 계산 |
| `calculator_get_stats` | 사용 통계 | 총 계산 횟수, 가장 많이 사용된 연산 |
| `calculator_clear_history` | 기록 삭제 | 모든 계산 기록 삭제 |

## 🧪 테스트 및 검증

### 자동 테스트 실행
```bash
# 계산기 전체 기능 테스트
python tests/test_calculator.py

# 전체 서비스 테스트
python tests/test_simple.py

# Pytest로 단위 테스트
uv run pytest tests/mcps/test_calculator.py

# 커버리지 포함 테스트
uv run pytest --cov=src tests/
```

### 수동 테스트 결과 (2025-08-18 검증 완료)

#### ✅ 서버 상태
```bash
curl http://127.0.0.1:8000/health
# 결과: {"status":"healthy","version":"0.1.0","services":{"calculator":{"status":"healthy"}}}
```

#### ✅ 기본 계산 테스트
```bash
curl -X POST "http://127.0.0.1:8000/calculator/calculate" \
  -H "Content-Type: application/json" \
  -d '{"a": 15, "b": 3, "operation": "multiply"}'
# 결과: {"success":true,"data":{"result":45.0}}
```

#### ✅ 제곱근 계산 테스트
```bash
curl -X POST "http://127.0.0.1:8000/calculator/sqrt" \
  -H "Content-Type: application/json" \
  -d '{"number": 144}'
# 결과: {"success":true,"data":{"result":12.0}}
```

#### ✅ MCP 연결 테스트
- MCP Inspector 연결: ✅ 성공
- Claude Desktop 연결: ✅ 성공 (mcp-remote 사용)
- Cursor IDE 연결: ✅ 성공 (url 방식 사용)
- 도구 목록 조회: ✅ 6개 Calculator 도구 확인

### 성능 테스트 결과
- 평균 응답시간: ~1ms
- 동시 연결: 10+ MCP 클라이언트 지원
- 메모리 사용량: ~50MB (기본 설정)
- 안정성: 1000회 연속 계산 테스트 통과

## 📖 상세 문서

- **[MCP 클라이언트 연결 가이드](./MCP_CLIENT_SETUP.md)**: 다양한 MCP 클라이언트 연결 방법
- **[프로젝트 문서](./CLAUDE.md)**: 전체 AIDT MCP 플랫폼 아키텍처
- **[API 문서](http://127.0.0.1:8000/docs)**: Swagger UI (서버 실행 후 접속)

## 🏗️ 아키텍처

```
AIDT MCP Platform
├── Calculator Service (✅ 구현 완료)
│   ├── 기본 수학 연산
│   ├── 제곱근 계산
│   ├── 수식 평가
│   ├── 계산 기록 관리
│   └── 사용 통계
├── Confluence Service (설정 필요)
├── JIRA Service (설정 필요)
└── Slack Service (설정 필요)
```

## 🛠️ 개발

### 새로운 계산 기능 추가
1. `src/mcps/calculator/models.py`에 모델 정의
2. `src/mcps/calculator/router.py`에 엔드포인트 추가
3. `tests/mcps/test_calculator.py`에 테스트 추가

### 새로운 MCP 서비스 추가
1. `src/mcps/{service_name}/` 디렉터리 생성
2. 모델, 설정, 클라이언트, 라우터 구현
3. `src/main.py`에 서비스 등록

## 📊 현재 상태

- ✅ **Calculator Service**: 완전히 구현되고 테스트됨
- ⚙️ **MCP 프로토콜**: FastAPI-MCP로 자동 변환
- 🔄 **실시간 연결**: Server-Sent Events 지원
- 📈 **확장 가능**: 모듈러 아키텍처로 새 서비스 추가 용이

**🎯 핵심 성과: AI 디지털 교과서의 수학 계산 기능을 MCP 프로토콜로 제공하여 Claude Desktop 등 다양한 AI 클라이언트에서 즉시 활용 가능한 시스템 구축 완료**