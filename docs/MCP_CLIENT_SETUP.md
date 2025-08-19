# AIDT MCP Server - 클라이언트 연결 가이드

AIDT FastAPI MCP 멀티서버에 다양한 MCP 클라이언트를 연결하는 방법을 설명합니다. 이 서버는 Calculator, Confluence, JIRA, Slack 등 여러 서비스를 통합하여 제공합니다.

## 📍 서버 정보

- **서버 URL**: `http://127.0.0.1:8000`
- **MCP 엔드포인트**: `http://127.0.0.1:8000/mcp`
- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **Health Check**: `http://127.0.0.1:8000/health`

## 🚀 서버 시작하기

```bash
# 개발 서버 시작
python scripts/start_dev.py

# 또는 직접 uvicorn 사용
uv run uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
```

## 🔧 사용 가능한 MCP 도구들

### Calculator 도구 (기본 활성화)
| 도구 이름 | 설명 | 엔드포인트 |
|----------|------|-----------|
| `calculator_basic_calculation` | 두 숫자로 기본적인 수학 연산 (덧셈, 뺄셈, 곱셈, 나눗셈, 거듭제곱, 나머지) | `POST /calculator/calculate` |
| `calculator_square_root` | 숫자의 제곱근 계산 | `POST /calculator/sqrt` |
| `calculator_evaluate_expression` | 수학 수식 계산 | `POST /calculator/expression` |
| `calculator_get_history` | 최근 계산 기록 조회 | `GET /calculator/history` |
| `calculator_get_stats` | 계산기 사용 통계 조회 | `GET /calculator/stats` |
| `calculator_clear_history` | 계산 기록 삭제 | `DELETE /calculator/history` |

### Confluence 도구 (활성화 시 사용 가능)
| 도구 이름 | 설명 | 엔드포인트 |
|----------|------|-----------|
| `confluence_search_content` | CQL을 사용한 Confluence 콘텐츠 검색 | `GET /confluence/search` |
| `confluence_get_page` | 페이지 ID로 특정 페이지 조회 | `GET /confluence/page` |
| `confluence_get_space` | 스페이스 키로 스페이스 정보 조회 | `GET /confluence/space` |

### JIRA 도구 (활성화 시 사용 가능)
| 도구 이름 | 설명 | 엔드포인트 |
|----------|------|-----------|
| `jira_search_issues` | JQL을 사용한 JIRA 이슈 검색 | `GET /jira/search` |
| `jira_get_issue` | 이슈 키로 특정 이슈 조회 | `GET /jira/issue` |
| `jira_get_project` | 프로젝트 키로 프로젝트 정보 조회 | `GET /jira/project` |

### Slack 도구 (활성화 시 사용 가능)
| 도구 이름 | 설명 | 엔드포인트 |
|----------|------|-----------|
| `slack_get_channel_info` | 채널 정보 조회 | `GET /slack/channel/info` |
| `slack_get_channel_history` | 채널 메시지 히스토리 조회 | `GET /slack/channel/history` |
| `slack_send_message` | 채널에 메시지 전송 | `POST /slack/message/send` |
| `slack_get_user_info` | 사용자 정보 조회 | `GET /slack/user/info` |

## 🖥️ MCP 클라이언트 설정

### 연결 방법별 설정

#### 📋 설정 요약표

| 클라이언트 | 연결 방법 | 설정 방식 | 상태 |
|------------|-----------|-----------|------|
| Claude Desktop | `mcp-remote` 명령어 | `claude_desktop_config.json` | ✅ 테스트 완료 |
| Cursor IDE | URL 직접 연결 | MCP Extension 설정 | ✅ 테스트 완료 |
| Windsurf | URL 직접 연결 | MCP 설정 | ✅ 권장 |
| Claude Code CLI | URL 직접 연결 | `mcp add` 명령어 | ✅ 권장 |
| VS Code | MCP Extension | `settings.json` | ⚠️ 확인 필요 |

### 1. Claude Desktop (권장)

FastAPI MCP 서버와 연결하기 위해 **mcp-remote** 명령어를 사용합니다.

#### 설정 파일 위치:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

#### 설정 내용:
```json
{
  "mcpServers": {
    "aidt-mcp": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "http://127.0.0.1:8000/mcp"
      ]
    }
  }
}
```

#### 연결 확인:
1. Claude Desktop 재시작
2. 새 대화 시작
3. 🔌 아이콘이 나타나면 연결 성공
4. 테스트: "Calculate 15 * 8 + 32" 또는 "Search Confluence for documentation"

### 2. Cursor IDE (권장)

Cursor에서는 **URL 방식**을 사용하여 직접 연결합니다.

#### 설치 및 설정:
1. Cursor에서 MCP Extension 설치
2. Extension 설정에서 새 MCP 서버 추가:

```json
{
  "aidt-mcp": {
    "url": "http://127.0.0.1:8000/mcp"
  }
}
```

**중요**: Cursor에서는 `command` 방식이 아닌 `url` 방식을 사용해야 합니다.

#### 사용 방법:
1. Cursor 사이드바에서 MCP 탭 열기
2. AIDT MCP 서버 선택
3. 사용 가능한 도구 목록 확인 (calculator, confluence, jira, slack)
4. 코드에서 직접 도구 호출

### 3. Windsurf

Windsurf MCP 설정에서 URL 방식 사용:

```json
{
  "aidt-mcp": {
    "url": "http://127.0.0.1:8000/mcp"
  }
}
```

### 4. Claude Code CLI

Claude Code CLI에서 MCP 서버 추가:

```bash
# MCP 서버 추가
claude-code mcp add aidt-mcp http://127.0.0.1:8000/mcp

# 연결 확인
claude-code mcp list

# 사용 예시
claude-code chat "Calculate the square root of 144"
claude-code chat "Search Confluence for 'API documentation'"
claude-code chat "What are my recent JIRA issues?"
```

### 5. VS Code (MCP Extension)

VS Code에서 MCP Extension 사용:

#### 설정 파일 (settings.json):
```json
{
  "mcp.servers": {
    "aidt-mcp": {
      "url": "http://127.0.0.1:8000/mcp",
      "name": "AIDT MCP Server",
      "description": "AIDT 통합 MCP 서버 (Calculator, Confluence, JIRA, Slack)"
    }
  }
}
```

### 5. 직접 HTTP 클라이언트 사용

#### cURL 예시:

```bash
# 기본 계산
curl -X POST "http://127.0.0.1:8000/calculator/calculate" \
  -H "Content-Type: application/json" \
  -d '{"a": 15, "b": 3, "operation": "multiply"}'

# 제곱근 계산
curl -X POST "http://127.0.0.1:8000/calculator/sqrt" \
  -H "Content-Type: application/json" \
  -d '{"number": 144}'

# 수식 계산
curl -X POST "http://127.0.0.1:8000/calculator/expression" \
  -H "Content-Type: application/json" \
  -d '{"expression": "(10 + 5) * 3 - 8"}'

# 계산 기록 조회
curl -X GET "http://127.0.0.1:8000/calculator/history?limit=5"

# 통계 조회
curl -X GET "http://127.0.0.1:8000/calculator/stats"
```

#### Python 클라이언트 예시:

```python
import httpx
import json

# 기본 계산
async def calculate_basic():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://127.0.0.1:8000/calculator/calculate",
            json={"a": 25, "b": 4, "operation": "divide"}
        )
        result = response.json()
        print(f"결과: {result['data']['result']}")

# 수식 계산
async def evaluate_expression():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://127.0.0.1:8000/calculator/expression",
            json={"expression": "2 * (3 + 4) - 1"}
        )
        result = response.json()
        print(f"수식 결과: {result['data']['result']}")
```

## 📋 사용 예시

### Claude Desktop에서:
```
사용자: "Calculate 15 * 8 + 32"
AI: calculator_basic_calculation을 사용하여 계산하겠습니다.
    15 * 8 = 120
    120 + 32 = 152
    결과: 152

사용자: "What's the square root of 144?"
AI: calculator_square_root를 사용하여 계산하겠습니다.
    √144 = 12

사용자: "Show my calculation history"
AI: calculator_get_history를 사용하여 기록을 조회하겠습니다.
    [최근 계산 기록 표시]
```

### Cursor IDE에서:
```javascript
// MCP 도구를 코드에서 직접 사용
const result = await mcpTools.calculator_basic_calculation({
  a: 10,
  b: 5,
  operation: "multiply"
});
console.log(`결과: ${result.data.result}`); // 결과: 50
```

## 🔍 연결 확인 및 테스트

### 1. 서버 상태 확인
```bash
# 서버 시작 확인
curl http://127.0.0.1:8000/health

# 활성화된 서비스 확인
curl http://127.0.0.1:8000/

# API 문서 확인
open http://127.0.0.1:8000/docs
```

### 2. MCP Inspector로 테스트
```bash
# MCP Inspector 실행 (공식 도구)
npx @modelcontextprotocol/inspector http://127.0.0.1:8000/mcp

# 또는 포트 지정
npx @modelcontextprotocol/inspector http://127.0.0.1:8000/mcp --port 3001
```

### 3. 도구별 테스트 명령어
```bash
# Calculator 테스트
python tests/test_calculator.py

# 전체 서비스 테스트
python tests/test_simple.py

# 헬스체크 스크립트
python scripts/health_check.py --json
```

## 🚨 문제 해결

### 연결 실패 시 체크리스트
1. ✅ **서버 실행 확인**: `curl http://127.0.0.1:8000/health`
2. ✅ **포트 사용 확인**: `lsof -i :8000`
3. ✅ **환경변수 설정**: `.env` 파일 존재 및 `MCP_ENABLED_SERVICES` 설정
4. ✅ **클라이언트 설정**: 올바른 URL (`/mcp`) 및 연결 방식 사용
5. ✅ **방화벽 설정**: 로컬 연결 차단 여부 확인

### 일반적인 오류 및 해결방법

#### `404 Not Found` 오류
```bash
# 잘못된 URL 사용
❌ http://127.0.0.1:8000/mcp/calculator
❌ http://127.0.0.1:8000/mcp/confluence

# 올바른 URL
✅ http://127.0.0.1:8000/mcp
```

#### `406 Not Acceptable` 오류
- **원인**: 클라이언트가 잘못된 헤더 전송
- **해결**: MCP 클라이언트(Inspector, Claude Desktop 등) 사용 권장
- **또는**: curl에서 올바른 헤더 사용

#### `Connection refused` 오류
```bash
# 서버 시작
python scripts/start_dev.py

# 또는 직접 실행
uv run uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
```

#### Cursor 연결 실패
- **확인사항**: `url` 방식 사용 (command 방식 아님)
- **올바른 설정**:
```json
{
  "aidt-mcp": {
    "url": "http://127.0.0.1:8000/mcp"
  }
}
```

### 로그 확인 방법
```bash
# 실시간 서버 로그 확인
tail -f logs/app.log

# 디버그 모드로 실행
LOG_LEVEL=DEBUG uv run uvicorn src.main:app --reload

# 특정 서비스 로그 필터링
grep "calculator" logs/app.log
grep "ERROR" logs/app.log
```

### 성능 및 오류 관련
- **Calculator 오류**: 0으로 나누기, 큰 숫자(1e15 초과), 잘못된 수식
- **Confluence/JIRA 오류**: API 토큰 만료, 네트워크 연결, 권한 부족
- **Slack 오류**: 봇 토큰 만료, 채널 권한, 메시지 제한

## 🛠️ 개발자를 위한 확장

### 새로운 계산 기능 추가:

1. **모델 수정** (`src/mcps/calculator/models.py`):
```python
class NewCalculationRequest(BaseModel):
    # 새로운 요청 모델 정의
```

2. **라우터 추가** (`src/mcps/calculator/router.py`):
```python
@router.post("/new_function", operation_id="calculator_new_function")
async def new_calculation_function(...):
    # 새로운 계산 기능 구현
```

3. **테스트 추가** (`tests/mcps/test_calculator.py`):
```python
async def test_new_calculation_function():
    # 새로운 기능 테스트
```

### MCP 도구 자동 생성:
FastAPI MCP는 모든 라우터 엔드포인트를 자동으로 MCP 도구로 변환합니다. `operation_id`를 설정하면 해당 이름으로 MCP 도구가 생성됩니다.

## 📖 참고 자료

- [FastAPI MCP 공식 문서](https://fastapi-mcp.tadata.com/)
- [Model Context Protocol 사양](https://modelcontextprotocol.io/)
- [Claude Desktop MCP 가이드](https://claude.ai/docs/mcp)
- [AIDT 프로젝트 문서](./CLAUDE.md)

## 🔗 추가 자료

### 공식 문서
- [FastAPI MCP 공식 문서](https://fastapi-mcp.tadata.com/)
- [Model Context Protocol 사양](https://modelcontextprotocol.io/)
- [MCP Inspector](https://github.com/modelcontextprotocol/inspector)

### AIDT 프로젝트 문서
- [메인 README](../README.md)
- [Calculator 전용 가이드](./README_CALCULATOR.md)
- [개발자 가이드](../CLAUDE.md)

### 외부 연동 문서
- [Confluence Cloud API](https://developer.atlassian.com/cloud/confluence/rest/v2/)
- [JIRA Cloud API](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)
- [Slack Web API](https://api.slack.com/web)

## 🎯 핵심 요약

### ✅ 클라이언트별 권장 설정
| 클라이언트 | 연결 방법 | 설정 |
|------------|-----------|------|
| **Claude Desktop** | `mcp-remote` | `"command": "npx", "args": ["mcp-remote", "http://127.0.0.1:8000/mcp"]` |
| **Cursor IDE** | `url` | `"url": "http://127.0.0.1:8000/mcp"` |
| **Windsurf** | `url` | `"url": "http://127.0.0.1:8000/mcp"` |

### 🔧 사용 가능한 도구들
- **Calculator** (6개 도구) - 항상 활성화
- **Confluence** (3개 도구) - API 토큰 필요
- **JIRA** (3개 도구) - API 토큰 필요  
- **Slack** (4개 도구) - 봇 토큰 필요

### 🚀 빠른 시작
1. **서버 시작**: `python scripts/start_dev.py`
2. **상태 확인**: `curl http://127.0.0.1:8000/health`
3. **클라이언트 설정**: 위 표 참고
4. **테스트**: "Calculate 15 * 8" 등 요청

**AIDT MCP Server는 AI 디지털 교과서 플랫폼을 위한 통합 MCP 서버로, Calculator, Confluence, JIRA, Slack 서비스를 단일 엔드포인트에서 제공하는 확장 가능한 멀티서비스 플랫폼입니다.**