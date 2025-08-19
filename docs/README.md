# AIDT MCP Documentation Index

AIDT FastAPI MCP 멀티서버 플랫폼의 상세 문서 모음입니다.

## 📋 문서 목록

### 🚀 시작하기
- **[MCP 클라이언트 연결 가이드](./MCP_CLIENT_SETUP.md)**
  - Claude Desktop, Cursor, Windsurf 등 다양한 MCP 클라이언트 연결 방법
  - 클라이언트별 설정 가이드 및 문제 해결
  - 연결 확인 및 테스트 방법

### 🧮 Calculator 서비스
- **[Calculator 서비스 가이드](./README_CALCULATOR.md)**
  - Calculator 서비스 전용 사용법
  - 상세한 테스트 결과 및 성능 지표
  - 기능별 사용 예시

### 🔧 MCP 도구 참조
- **[MCP 도구 상세 가이드](./MCP_TOOLS.md)**
  - 모든 16개 MCP 도구의 상세한 사용법
  - 서비스별 도구 분류 (Calculator, Confluence, JIRA, Slack)
  - 복합 워크플로우 예시

## 🎯 빠른 네비게이션

### 처음 사용하시는 분
1. [메인 README](../README.md) - 프로젝트 개요
2. [클라이언트 연결 가이드](./MCP_CLIENT_SETUP.md) - 클라이언트 설정
3. [Calculator 가이드](./README_CALCULATOR.md) - 기본 기능 테스트

### 개발자
1. [개발 환경 가이드](../CLAUDE.md) - 전체 AIDT 아키텍처
2. [MCP 도구 참조](./MCP_TOOLS.md) - 모든 도구 상세 정보
3. [테스트 가이드](../tests/) - 테스트 실행 방법

### 특정 서비스 사용자
- **Calculator만 사용**: [Calculator 가이드](./README_CALCULATOR.md)
- **Confluence 연동**: [MCP 도구 가이드 - Confluence 섹션](./MCP_TOOLS.md#-confluence-도구들-api-토큰-필요)
- **JIRA 연동**: [MCP 도구 가이드 - JIRA 섹션](./MCP_TOOLS.md#-jira-도구들-api-토큰-필요)
- **Slack 연동**: [MCP 도구 가이드 - Slack 섹션](./MCP_TOOLS.md#-slack-도구들-봇-토큰-필요)

## 🔍 문제 해결

### 연결 문제
- [클라이언트 연결 문제 해결](./MCP_CLIENT_SETUP.md#-문제-해결)
- [일반적인 오류 및 해결방법](./MCP_CLIENT_SETUP.md#일반적인-오류-및-해결방법)

### 기능 문제
- [Calculator 테스트](./README_CALCULATOR.md#-테스트-및-검증)
- [서비스별 제한사항](./MCP_TOOLS.md#-도구-성능-및-제한사항)

## 📚 외부 참조

### 공식 문서
- [FastAPI MCP 공식 문서](https://fastapi-mcp.tadata.com/)
- [Model Context Protocol 사양](https://modelcontextprotocol.io/)
- [MCP Inspector](https://github.com/modelcontextprotocol/inspector)

### 외부 API 문서
- [Confluence Cloud API](https://developer.atlassian.com/cloud/confluence/rest/v2/)
- [JIRA Cloud API](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)
- [Slack Web API](https://api.slack.com/web)

## 🚀 빠른 시작 체크리스트

### 기본 설정 (5분)
- [ ] 서버 시작: `python scripts/start_dev.py`
- [ ] 상태 확인: `curl http://127.0.0.1:8000/health`
- [ ] 클라이언트 설정 (Claude Desktop 또는 Cursor)
- [ ] 기본 테스트: "Calculate 15 * 8"

### 고급 설정 (15분)
- [ ] 외부 서비스 API 토큰 설정 (.env 파일)
- [ ] 모든 서비스 활성화
- [ ] 전체 기능 테스트: `python tests/test_simple.py`
- [ ] MCP Inspector로 도구 확인

---

**💡 도움이 필요하신가요?** 각 문서의 문제 해결 섹션을 먼저 확인해보시고, 그래도 해결되지 않으면 이슈를 등록해주세요.