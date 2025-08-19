# MCP FastAPI 멀티서버 플랫폼

확장 가능한 MCP (Model Context Protocol) 서버 플랫폼입니다. FastAPI 기반으로 구축되어 여러 외부 서비스(Confluence, JIRA, Slack 등)와의 통합을 제공합니다.

## 🚀 주요 특징

- **모듈러 아키텍처**: 서비스별 독립적인 모듈 구조
- **타입 안전성**: Pydantic 모델 기반 전체 코드베이스
- **확장성**: 새로운 MCP 서비스 쉽게 추가 가능
- **복원력**: 지수 백오프, Circuit Breaker 패턴 적용
- **보안**: JWT 인증, 입력 검증, 레이트 리미팅
- **모니터링**: 구조화된 로깅, 헬스체크, 통계 수집
- **컨테이너화**: Docker 기반 배포 지원

## 📁 프로젝트 구조

```
aidt-mcp/
├── src/
│   ├── main.py                 # 메인 FastAPI 애플리케이션
│   ├── config/                 # 설정 관리
│   │   ├── settings.py         # 환경별 설정
│   │   └── logging.py          # 로깅 설정
│   ├── shared/                 # 공통 유틸리티
│   │   ├── auth.py             # 인증/인가
│   │   ├── exceptions.py       # 커스텀 예외
│   │   ├── middleware.py       # 미들웨어
│   │   ├── models.py           # 공통 모델
│   │   └── utils.py            # 헬퍼 함수
│   └── mcps/                   # MCP 서비스들
│       ├── confluence/         # Confluence MCP
│       ├── jira/              # JIRA MCP
│       └── slack/             # Slack MCP
├── scripts/                    # 개발/배포 스크립트
├── tests/                      # 테스트 코드
├── docker-compose.yml          # 로컬 개발환경
├── Dockerfile                  # 컨테이너 이미지
└── pyproject.toml             # 프로젝트 설정
```

## 🔧 설치 및 설정

### 1. 요구사항

- Python 3.12+
- uv (패키지 관리자)

### 2. 환경 설정

```bash
# 저장소 클론
git clone <repository-url>
cd aidt-mcp

# uv 설치 (없는 경우)
pip install uv

# 의존성 설치
uv sync

# 환경변수 설정
cp .env.example .env
# .env 파일을 편집하여 실제 값 입력
```

### 3. 환경변수 설정

`.env` 파일에서 다음 설정을 구성하세요:

#### 기본 설정 (Calculator만 사용)
```bash
# 기본 애플리케이션 설정
SECRET_KEY=your-secret-key
ENVIRONMENT=development
DEBUG=true

# MCP 설정 - 계산기만 활성화
MCP_ENABLED_SERVICES=calculator
MCP_MOUNT_PATH=/mcp

# CORS 설정 (개발환경용)
CORS_ORIGINS=["*"]
```

#### 전체 서비스 설정
```bash
# 기본 설정
SECRET_KEY=your-secret-key
MCP_ENABLED_SERVICES=calculator,confluence,jira,slack

# Confluence 설정 (활성화 시 필요)
CONFLUENCE_BASE_URL=https://your-domain.atlassian.net
CONFLUENCE_EMAIL=your-email@domain.com
CONFLUENCE_API_TOKEN=your-api-token

# JIRA 설정 (활성화 시 필요)
JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@domain.com
JIRA_API_TOKEN=your-api-token

# Slack 설정 (활성화 시 필요)
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_SIGNING_SECRET=your-signing-secret
```

**참고**: Calculator 서비스는 외부 API 토큰이 필요하지 않으므로 기본 설정만으로 즉시 사용할 수 있습니다.

## 🏃 실행 방법

### 개발 환경

```bash
# 개발 서버 시작
python scripts/start_dev.py

# 또는 직접 실행
uv run uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
```

### Docker 환경

```bash
# 개발용 (docker-compose)
docker-compose up --build

# 프로덕션용 (Docker)
docker build -t aidt-mcp .
docker run -p 8000:8000 --env-file .env aidt-mcp
```

## 🔌 MCP 클라이언트 연결

### 서버 정보
- **MCP 서버 URL**: `http://127.0.0.1:8000/mcp`
- **서버 상태**: `http://127.0.0.1:8000/health`
- **API 문서**: `http://127.0.0.1:8000/docs`

### 지원되는 클라이언트

#### 1. Claude Desktop (권장)
`claude_desktop_config.json` 파일에 추가:

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

**설정 파일 위치:**
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

#### 2. Cursor IDE
MCP Extension 설정에서:

```json
{
  "aidt-mcp": {
    "url": "http://127.0.0.1:8000/mcp"
  }
}
```

**중요**: Cursor에서는 `command` 방식이 아닌 `url` 방식을 사용해야 합니다.

#### 3. Windsurf
MCP 설정에서:

```json
{
  "aidt-mcp": {
    "url": "http://127.0.0.1:8000/mcp"
  }
}
```

#### 4. Claude Code CLI
```bash
# MCP 서버 추가
claude-code mcp add aidt-mcp http://127.0.0.1:8000/mcp

# 연결 확인
claude-code mcp list

# 사용 예시
claude-code chat "Calculate 15 * 8 + 32"
```

### 연결 확인 방법

1. **서버 시작 확인**:
```bash
curl http://127.0.0.1:8000/health
```

2. **MCP Inspector로 테스트**:
```bash
npx @modelcontextprotocol/inspector http://127.0.0.1:8000/mcp
```

3. **클라이언트에서 연결 상태 확인**:
   - Claude Desktop: 새 대화에서 🔌 아이콘 확인
   - Cursor: MCP 탭에서 서버 상태 확인

### 문제 해결

**연결 실패 시 체크리스트:**
1. ✅ 서버가 실행 중인지 확인
2. ✅ 포트 8000이 사용 가능한지 확인
3. ✅ 환경변수 설정이 올바른지 확인
4. ✅ 클라이언트 설정에서 올바른 URL 사용 확인
5. ✅ 방화벽이 로컬 연결을 차단하지 않는지 확인

**일반적인 오류:**
- `404 Not Found`: 잘못된 URL (올바른 URL: `/mcp`)
- `406 Not Acceptable`: 클라이언트 헤더 문제 (MCP 클라이언트 사용 권장)
- `Connection refused`: 서버가 실행되지 않음

## 🌐 API 엔드포인트

### 기본 엔드포인트

- `GET /` - 서비스 정보
- `GET /health` - 헬스체크
- `GET /mcp` - MCP 서버 엔드포인트 (FastAPI MCP에서 자동 생성)

### 일반 API 엔드포인트

#### Confluence API
- `GET /confluence/search` - CQL 검색
- `GET /confluence/page` - 페이지 조회
- `GET /confluence/space` - 스페이스 조회
- `GET /confluence/health` - 서비스 상태

#### JIRA API
- `GET /jira/search` - JQL 검색
- `GET /jira/issue` - 이슈 조회
- `GET /jira/project` - 프로젝트 조회
- `GET /jira/health` - 서비스 상태

#### Slack API
- `GET /slack/channel/info` - 채널 정보
- `GET /slack/channel/history` - 메시지 히스토리
- `POST /slack/message/send` - 메시지 전송
- `GET /slack/user/info` - 사용자 정보
- `GET /slack/health` - 서비스 상태

#### Calculator API (항상 활성화)
- `POST /calculator/calculate` - 기본 수학 연산 (덧셈, 뺄셈, 곱셈, 나눗셈, 거듭제곱, 나머지)
- `POST /calculator/sqrt` - 제곱근 계산
- `POST /calculator/expression` - 복합 수식 계산
- `GET /calculator/history` - 계산 기록 조회
- `GET /calculator/stats` - 사용 통계 조회
- `DELETE /calculator/history` - 계산 기록 삭제

### MCP 툴 엔드포인트

FastAPI MCP가 자동으로 `/mcp` 경로에 MCP 프로토콜 호환 엔드포인트를 생성합니다.

#### 사용 가능한 MCP 툴들

각 FastAPI 엔드포인트는 `operation_id`를 기반으로 MCP 툴로 자동 변환됩니다:

**Calculator 툴 (기본 활성화):**
- `calculator_basic_calculation` - 두 숫자로 기본적인 수학 연산
- `calculator_square_root` - 숫자의 제곱근 계산
- `calculator_evaluate_expression` - 수학 수식 계산
- `calculator_get_history` - 최근 계산 기록 조회
- `calculator_get_stats` - 계산기 사용 통계 조회
- `calculator_clear_history` - 계산 기록 삭제

**Confluence 툴 (활성화 시):**
- `confluence_search_content` - CQL 검색
- `confluence_get_page` - 페이지 조회
- `confluence_get_space` - 스페이스 조회

**JIRA 툴 (활성화 시):**
- `jira_search_issues` - JQL 검색
- `jira_get_issue` - 이슈 조회
- `jira_get_project` - 프로젝트 조회

**Slack 툴 (활성화 시):**
- `slack_get_channel_info` - 채널 정보 조회
- `slack_get_channel_history` - 메시지 히스토리
- `slack_send_message` - 메시지 전송
- `slack_get_user_info` - 사용자 정보 조회

#### MCP 프로토콜 엔드포인트

클라이언트가 직접 사용하는 저수준 엔드포인트들:
- **초기화**: `POST /mcp` (세션 시작)
- **툴 목록**: MCP 메시지 `tools/list`
- **툴 실행**: MCP 메시지 `tools/call`
- **서버 정보**: MCP 메시지 `initialize`

**사용 예시:**
```bash
# MCP Inspector로 툴 목록 확인
npx @modelcontextprotocol/inspector http://127.0.0.1:8000/mcp

# Claude Desktop에서
"Calculate 15 * 8 + 32"
"What's the square root of 144?"
"Search Confluence for 'API documentation'"
"Create a JIRA issue for bug fix"
```

## 🔍 헬스체크

```bash
# 헬스체크 실행
python scripts/health_check.py

# JSON 형식으로 출력
python scripts/health_check.py --json

# 다른 URL 체크
python scripts/health_check.py --url http://localhost:8001
```

## 🧪 테스트

```bash
# 모든 테스트 실행
uv run pytest

# 특정 테스트 실행
uv run pytest tests/test_confluence.py

# 커버리지 포함
uv run pytest --cov=src
```

## 🛠 개발

### 새로운 MCP 서비스 추가

1. `src/mcps/` 하위에 새 디렉터리 생성
2. 다음 파일들 구현:
   - `models.py` - Pydantic 모델
   - `config.py` - 서비스 설정
   - `client.py` - API 클라이언트
   - `router.py` - FastAPI 라우터

3. `src/config/settings.py`에 설정 추가
4. `src/main.py`에 라우터 등록

### 코드 품질

```bash
# 코드 포맷팅
uv run black src/
uv run isort src/

# 린팅
uv run ruff src/

# 타입 체크
uv run mypy src/
```

## 🔐 보안 고려사항

- 모든 API 토큰과 시크릿은 환경변수로 관리
- 입력값 검증 및 정제 (XSS, 인젝션 방지)
- 레이트 리미팅 적용
- CORS 설정 적절히 구성
- 프로덕션에서는 HTTPS 사용 필수

## 📊 모니터링

### 로깅

- 구조화된 JSON 로깅
- 요청/응답 자동 로깅
- 오류 상세 추적
- 성능 메트릭 수집

### 헬스체크

- 서비스별 독립적인 헬스체크
- 응답 시간 측정
- 외부 서비스 연결 상태 확인

### 통계 수집

- 요청 성공/실패 횟수
- 평균 응답 시간
- 서비스별 사용량 통계

## 🚀 배포

### Docker 배포

```bash
# 이미지 빌드
docker build -t aidt-mcp:latest .

# 컨테이너 실행
docker run -d \
  --name aidt-mcp \
  -p 8000:8000 \
  --env-file .env \
  aidt-mcp:latest
```

### Kubernetes 배포

```yaml
# k8s/deployment.yaml 예시
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aidt-mcp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: aidt-mcp
  template:
    metadata:
      labels:
        app: aidt-mcp
    spec:
      containers:
      - name: aidt-mcp
        image: aidt-mcp:latest
        ports:
        - containerPort: 8000
        envFrom:
        - secretRef:
            name: aidt-mcp-secrets
```

## 📚 상세 문서

### 사용자 가이드
- **[MCP 클라이언트 연결 가이드](./docs/MCP_CLIENT_SETUP.md)**: Claude Desktop, Cursor, Windsurf 등 MCP 클라이언트 연결 방법
- **[Calculator 서비스 가이드](./docs/README_CALCULATOR.md)**: 계산기 서비스 전용 사용법과 테스트 결과
- **[MCP 도구 상세 가이드](./docs/MCP_TOOLS.md)**: 모든 MCP 도구들의 상세한 사용법과 예시

### 개발자 가이드
- **[개발 환경 설정](./CLAUDE.md)**: 전체 AIDT 프로젝트 아키텍처 및 개발 가이드
- **[API 문서](http://127.0.0.1:8000/docs)**: Swagger UI (서버 실행 후 접속)
- **[테스트 가이드](./tests/)**: 테스트 실행 방법 및 테스트 스크립트

### 빠른 참조
```bash
# 서버 시작
python scripts/start_dev.py

# 상태 확인
curl http://127.0.0.1:8000/health

# 테스트 실행
python tests/test_calculator.py

# 문서 접속
open http://127.0.0.1:8000/docs
```

## 🤝 기여하기

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Update documentation
6. Run linting and tests: `uv run black src/ && uv run pytest`
7. Create a pull request

## 📄 라이선스

MIT License

## 🔗 관련 링크

### 공식 문서
- [FastAPI MCP 공식 문서](https://fastapi-mcp.tadata.com/)
- [Model Context Protocol 사양](https://modelcontextprotocol.io/)
- [MCP Inspector](https://github.com/modelcontextprotocol/inspector)

### AIDT 프로젝트
- [AIDT 프로젝트 메인](https://github.com/your-org/aidt)
- [개발 가이드](./CLAUDE.md)

### 외부 API
- [Confluence Cloud API](https://developer.atlassian.com/cloud/confluence/rest/v2/)
- [JIRA Cloud API](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)
- [Slack Web API](https://api.slack.com/web)

---

**🎯 핵심 요약**: FastAPI MCP를 기반으로 한 확장 가능한 멀티서비스 플랫폼으로, Calculator, Confluence, JIRA, Slack 통합을 통해 AI 클라이언트에서 직접 사용할 수 있는 16개의 MCP 도구를 제공합니다.
