# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AIDT MCP는 AIDT (AI Digital Textbook) 시스템을 위한 확장 가능한 FastAPI 기반 MCP (Model Context Protocol) 멀티서버 플랫폼입니다. 여러 외부 서비스(Confluence, JIRA, Slack)와의 통합을 제공하며, 모듈러 아키텍처로 새로운 서비스를 쉽게 추가할 수 있습니다.

## Essential Commands

### Development Setup
```bash
# 의존성 설치 (uv 패키지 매니저 사용)
uv sync

# 개발 서버 시작 (권장 방법)
python scripts/start_dev.py

# 또는 직접 실행
uv run uvicorn src.main:app --reload --host 127.0.0.1 --port 8000

# 간단한 기능 테스트
python test_simple.py
```

### Testing
```bash
# 모든 테스트 실행
uv run pytest

# 특정 서비스 테스트
uv run pytest tests/mcps/test_confluence.py
uv run pytest tests/mcps/test_jira.py
uv run pytest tests/mcps/test_slack.py

# 커버리지 포함 테스트
uv run pytest --cov=src

# 테스트 마커별 실행
uv run pytest -m "not slow"  # 느린 테스트 제외
uv run pytest -m integration  # 통합 테스트만
```

### Code Quality
```bash
# 코드 포맷팅
uv run black src/
uv run isort src/

# 린팅
uv run ruff src/

# 타입 체크
uv run mypy src/
```

### Health Checks
```bash
# 서비스 헬스체크
python scripts/health_check.py

# JSON 형식으로 출력
python scripts/health_check.py --json

# 다른 URL 체크
python scripts/health_check.py --url http://localhost:8001
```

### Docker Environment
```bash
# 개발용 Docker 환경
docker-compose up --build

# 프로덕션용 Docker 빌드
docker build -t aidt-mcp .
docker run -p 8000:8000 --env-file .env aidt-mcp
```

## Architecture Overview

### Modular MCP Service Architecture
이 프로젝트는 FastAPI MCP를 활용한 모듈러 아키텍처를 사용합니다:

- **FastAPI 기반**: 각 서비스는 표준 FastAPI 엔드포인트로 구현
- **자동 MCP 변환**: FastAPI MCP가 모든 엔드포인트를 MCP 프로토콜로 자동 변환
- **타입 안전성**: Pydantic 모델 기반 전체 시스템
- **서비스 독립성**: 각 MCP 서비스 (confluence, jira, slack)는 독립적으로 활성화/비활성화 가능

### Key Components

#### 1. Main Application (src/main.py)
- FastAPI 애플리케이션과 MCP 서버 통합
- 서비스별 동적 라우터 등록
- 생명주기 관리 (startup/shutdown)
- 글로벌 미들웨어 및 예외 처리

#### 2. Service Modules (src/mcps/)
각 서비스는 동일한 구조를 따릅니다:
```
mcps/{service}/
├── models.py      # Pydantic 모델 정의
├── config.py      # 서비스별 설정
├── client.py      # API 클라이언트 구현
└── router.py      # FastAPI 라우터 (자동으로 MCP 툴이 됨)
```

#### 3. Configuration System (src/config/)
- **settings.py**: 환경별 설정 관리
- **logging.py**: 구조화된 로깅 설정
- Pydantic Settings 기반 환경변수 처리

#### 4. Shared Components (src/shared/)
- **auth.py**: JWT 인증 시스템
- **middleware.py**: 요청 로깅, 에러 처리, 보안 헤더, 레이트 리미팅
- **exceptions.py**: 커스텀 예외 클래스
- **models.py**: 공통 응답 모델
- **utils.py**: 헬퍼 함수들

### MCP Integration Pattern

이 프로젝트의 핵심은 **FastAPI MCP**를 통한 자동 변환입니다:

1. **Standard FastAPI**: 일반적인 FastAPI 엔드포인트 작성
2. **Operation IDs**: 각 엔드포인트에 명확한 `operation_id` 설정
3. **Auto MCP Tools**: FastAPI MCP가 자동으로 MCP 프로토콜 툴로 변환
4. **Dual Access**: 동일한 기능을 REST API와 MCP 프로토콜 모두로 접근 가능

예시:
```python
@router.get("/search", operation_id="confluence_search")
async def search_confluence(...):
    # 이 엔드포인트는 자동으로 MCP 툴 "confluence_search"가 됨
```

## Configuration Patterns

### Environment Variable System
```bash
# 기본 애플리케이션 설정
SECRET_KEY=your-secret-key
MCP_ENABLED_SERVICES=confluence,jira,slack  # 콤마로 구분된 서비스 목록
ENVIRONMENT=development  # development, staging, production, test

# 서비스별 설정 (활성화된 서비스만 필요)
CONFLUENCE_BASE_URL=https://your-domain.atlassian.net
CONFLUENCE_EMAIL=your-email@domain.com
CONFLUENCE_API_TOKEN=your-api-token

JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@domain.com
JIRA_API_TOKEN=your-api-token

SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_APP_TOKEN=xapp-your-app-token
SLACK_SIGNING_SECRET=your-signing-secret
```

### Dynamic Service Loading
서비스는 `MCP_ENABLED_SERVICES` 환경변수에 따라 동적으로 로드됩니다:
- 설정되지 않은 서비스는 자동으로 제외
- 각 서비스는 독립적으로 실패할 수 있음 (다른 서비스에 영향 없음)
- 런타임에 서비스 상태 확인 가능

## Adding New MCP Services

새로운 서비스 추가 시 다음 단계를 따르세요:

### 1. 서비스 모듈 생성
```bash
mkdir src/mcps/{service_name}
touch src/mcps/{service_name}/__init__.py
touch src/mcps/{service_name}/models.py
touch src/mcps/{service_name}/config.py
touch src/mcps/{service_name}/client.py
touch src/mcps/{service_name}/router.py
```

### 2. 설정 클래스 추가 (config/settings.py)
```python
class NewServiceSettings(BaseConfig):
    api_key: str = Field(..., env="NEW_SERVICE_API_KEY")
    base_url: str = Field(..., env="NEW_SERVICE_BASE_URL")
```

### 3. 메인 애플리케이션에 등록 (main.py)
- `_initialize_services()` 함수에 초기화 로직 추가
- `register_service_routers()` 함수에 라우터 등록 로직 추가

### 4. 테스트 추가
```bash
touch tests/mcps/test_{service_name}.py
```

## Error Handling Strategy

### Exception Hierarchy
- **MCPBaseException**: 모든 MCP 관련 예외의 기본 클래스
- 서비스별 예외: 인증, 네트워크, 유효성 검사 등
- 자동 재시도: tenacity 라이브러리 사용

### Resilience Patterns
- **Circuit Breaker**: 외부 서비스 장애 시 시스템 보호
- **Exponential Backoff**: 재시도 시 지수 백오프
- **Request Timeout**: 모든 외부 요청에 타임아웃 설정
- **Graceful Degradation**: 개별 서비스 실패가 전체 시스템에 영향을 주지 않음

## Security Considerations

### Authentication
- JWT 토큰 기반 인증 (선택적)
- 서비스별 API 키/토큰 관리
- 환경변수를 통한 시크릿 관리

### Input Validation
- Pydantic 모델을 통한 입력 검증
- CQL/JQL 쿼리 검증
- XSS/인젝션 방지

### Security Headers
- 보안 헤더 자동 추가
- CORS 설정 관리
- 레이트 리미팅 (프로덕션 환경)

## Development Workflow

### 1. 환경 설정
```bash
# 프로젝트 클론 후
cp .env.example .env
# .env 파일 편집하여 실제 API 키 설정
uv sync
```

### 2. 개발 서버 시작
```bash
python scripts/start_dev.py
# 또는
uv run uvicorn src.main:app --reload
```

### 3. API 테스트
- **Swagger UI**: http://localhost:8000/docs
- **MCP 엔드포인트**: http://localhost:8000/mcp
- **헬스체크**: http://localhost:8000/health

### 4. 코드 품질 확인
```bash
uv run black src/ && uv run isort src/ && uv run ruff src/ && uv run mypy src/
```

## Deployment Considerations

### Docker Deployment
- 멀티스테이지 Dockerfile로 최적화된 이미지
- 환경변수를 통한 설정 관리
- 헬스체크 포함

### Kubernetes Deployment
- ConfigMap/Secret을 통한 설정 관리
- 서비스별 독립적인 확장 가능
- Ingress를 통한 라우팅

### Environment Specific Settings
- **development**: 디버그 모드, 상세 로깅
- **staging**: 운영과 유사한 환경에서 테스트
- **production**: 보안 강화, 성능 최적화

**핵심 요약**: FastAPI MCP를 활용하여 표준 REST API와 MCP 프로토콜을 동시에 제공하는 확장 가능한 멀티서비스 플랫폼입니다.