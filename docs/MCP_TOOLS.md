# AIDT MCP Tools Documentation

AIDT MCP Server에서 제공하는 모든 MCP 도구들의 상세한 사용법과 예시를 제공합니다.

## 📋 도구 개요

AIDT MCP Server는 4개의 주요 서비스에서 총 16개의 MCP 도구를 제공합니다:

| 서비스 | 도구 수 | 상태 | 필요 설정 |
|--------|---------|------|-----------|
| **Calculator** | 6개 | ✅ 항상 활성화 | 없음 |
| **Confluence** | 3개 | ⚙️ 설정 시 활성화 | API 토큰 |
| **JIRA** | 3개 | ⚙️ 설정 시 활성화 | API 토큰 |
| **Slack** | 4개 | ⚙️ 설정 시 활성화 | 봇 토큰 |

## 🧮 Calculator 도구들 (항상 사용 가능)

### 1. calculator_basic_calculation
**기본 수학 연산 수행**

#### 지원 연산
- `add`: 덧셈
- `subtract`: 뺄셈  
- `multiply`: 곱셈
- `divide`: 나눗셈
- `power`: 거듭제곱
- `modulo`: 나머지 연산

#### 사용 예시
```
사용자: "Calculate 15 multiplied by 8"
AI: calculator_basic_calculation(a=15, b=8, operation="multiply")
결과: 120

사용자: "What's 100 divided by 7?"
AI: calculator_basic_calculation(a=100, b=7, operation="divide")
결과: 14.285714285714286

사용자: "2 to the power of 10"
AI: calculator_basic_calculation(a=2, b=10, operation="power")
결과: 1024
```

#### 매개변수
- `a` (float): 첫 번째 숫자
- `b` (float): 두 번째 숫자
- `operation` (string): 연산 종류

#### 제한사항
- 0으로 나누기 불가
- 결과값 최대 크기: 1e15
- 정밀도: 15자리

### 2. calculator_square_root
**제곱근 계산**

#### 사용 예시
```
사용자: "What's the square root of 144?"
AI: calculator_square_root(number=144)
결과: 12.0

사용자: "Square root of 2"
AI: calculator_square_root(number=2)
결과: 1.4142135623730951
```

#### 매개변수
- `number` (float): 제곱근을 구할 숫자

#### 제한사항
- 음수 입력 불가

### 3. calculator_evaluate_expression
**복합 수식 계산**

#### 사용 예시
```
사용자: "Calculate (10 + 5) * 3 - 8"
AI: calculator_evaluate_expression(expression="(10 + 5) * 3 - 8")
결과: 37.0

사용자: "What's 2 + 3 * 4?"
AI: calculator_evaluate_expression(expression="2 + 3 * 4")
결과: 14.0
```

#### 매개변수
- `expression` (string): 계산할 수식

#### 지원 연산자
- `+`, `-`, `*`, `/`: 기본 연산
- `(`, `)`: 괄호
- 공백: 무시됨

#### 제한사항
- 허용된 문자만 사용 가능
- 복잡한 함수 사용 불가

### 4. calculator_get_history
**계산 기록 조회**

#### 사용 예시
```
사용자: "Show my calculation history"
AI: calculator_get_history(limit=10)
결과: [
  {
    "operation": "multiply",
    "input_values": [15, 8],
    "result": 120,
    "timestamp": "2025-08-18T02:27:04"
  },
  ...
]
```

#### 매개변수
- `limit` (int, 선택): 조회할 기록 수 (기본값: 10, 최대: 100)

### 5. calculator_get_stats
**계산기 사용 통계**

#### 사용 예시
```
사용자: "What are my calculator usage stats?"
AI: calculator_get_stats()
결과: {
  "total_calculations": 25,
  "successful_calculations": 23,
  "failed_calculations": 2,
  "most_used_operation": "multiply",
  "average_calculation_time": 1.2
}
```

### 6. calculator_clear_history
**계산 기록 삭제**

#### 사용 예시
```
사용자: "Clear my calculation history"
AI: calculator_clear_history()
결과: {"message": "계산 기록이 삭제되었습니다"}
```

## 📄 Confluence 도구들 (API 토큰 필요)

### 1. confluence_search_content
**CQL을 사용한 Confluence 콘텐츠 검색**

#### 사용 예시
```
사용자: "Search Confluence for 'API documentation'"
AI: confluence_search_content(cql="text ~ 'API documentation'", limit=10)

사용자: "Find pages in the DEV space updated this week"
AI: confluence_search_content(cql="space = DEV AND lastModified >= startOfWeek()")
```

#### 매개변수
- `cql` (string): Confluence Query Language 쿼리
- `limit` (int, 선택): 최대 결과 수 (기본값: 25)
- `expand` (string, 선택): 확장할 필드

#### CQL 예시
- `text ~ "keyword"`: 텍스트 검색
- `space = "SPACE_KEY"`: 특정 스페이스 검색
- `type = page`: 페이지만 검색
- `lastModified >= startOfWeek()`: 최근 수정된 콘텐츠

### 2. confluence_get_page
**페이지 ID로 특정 페이지 조회**

#### 사용 예시
```
사용자: "Get Confluence page with ID 12345"
AI: confluence_get_page(page_id="12345")
```

#### 매개변수
- `page_id` (string): 페이지 ID
- `expand` (string, 선택): 확장할 필드

### 3. confluence_get_space
**스페이스 정보 조회**

#### 사용 예시
```
사용자: "Show me information about the DEV space in Confluence"
AI: confluence_get_space(space_key="DEV")
```

#### 매개변수
- `space_key` (string): 스페이스 키
- `expand` (string, 선택): 확장할 필드

## 🎫 JIRA 도구들 (API 토큰 필요)

### 1. jira_search_issues
**JQL을 사용한 JIRA 이슈 검색**

#### 사용 예시
```
사용자: "Find my assigned JIRA issues"
AI: jira_search_issues(jql="assignee = currentUser() AND status != Done")

사용자: "Show bugs created this week"
AI: jira_search_issues(jql="type = Bug AND created >= startOfWeek()")
```

#### 매개변수
- `jql` (string): JIRA Query Language 쿼리
- `max_results` (int, 선택): 최대 결과 수 (기본값: 50)
- `fields` (array, 선택): 포함할 필드 목록

#### JQL 예시
- `assignee = currentUser()`: 내가 담당자인 이슈
- `status = "In Progress"`: 진행 중인 이슈
- `project = PROJ`: 특정 프로젝트 이슈
- `created >= -1w`: 지난 주에 생성된 이슈

### 2. jira_get_issue
**이슈 키로 특정 이슈 조회**

#### 사용 예시
```
사용자: "Get details for JIRA issue PROJ-123"
AI: jira_get_issue(issue_key="PROJ-123")
```

#### 매개변수
- `issue_key` (string): 이슈 키 (예: PROJ-123)
- `fields` (array, 선택): 포함할 필드 목록

### 3. jira_get_project
**프로젝트 정보 조회**

#### 사용 예시
```
사용자: "Show me details about the AIDT project in JIRA"
AI: jira_get_project(project_key="AIDT")
```

#### 매개변수
- `project_key` (string): 프로젝트 키
- `expand` (array, 선택): 확장할 필드

## 💬 Slack 도구들 (봇 토큰 필요)

### 1. slack_get_channel_info
**채널 정보 조회**

#### 사용 예시
```
사용자: "Get information about the #general channel"
AI: slack_get_channel_info(channel="#general")
```

#### 매개변수
- `channel` (string): 채널 ID 또는 이름

### 2. slack_get_channel_history
**채널 메시지 히스토리 조회**

#### 사용 예시
```
사용자: "Show me recent messages from #dev-team"
AI: slack_get_channel_history(channel="#dev-team", limit=10)
```

#### 매개변수
- `channel` (string): 채널 ID 또는 이름
- `limit` (int, 선택): 메시지 수 (기본값: 10)
- `oldest` (string, 선택): 시작 타임스탬프
- `latest` (string, 선택): 종료 타임스탬프

### 3. slack_send_message
**채널에 메시지 전송**

#### 사용 예시
```
사용자: "Send a message 'Hello team!' to #general"
AI: slack_send_message(channel="#general", text="Hello team!")
```

#### 매개변수
- `channel` (string): 채널 ID 또는 이름
- `text` (string): 메시지 내용
- `thread_ts` (string, 선택): 스레드 타임스탬프

### 4. slack_get_user_info
**사용자 정보 조회**

#### 사용 예시
```
사용자: "Get information about user john.doe"
AI: slack_get_user_info(user="john.doe")
```

#### 매개변수
- `user` (string): 사용자 ID 또는 이메일

## 🔧 도구 사용 패턴

### 일반적인 사용 시나리오

#### 1. 수학 계산 + 문서화
```
사용자: "Calculate the project budget (1500 * 12 + 5000) and document it in Confluence"
AI: 
1. calculator_evaluate_expression("1500 * 12 + 5000") → 23000
2. confluence_search_content("budget") → 기존 예산 페이지 찾기
3. 결과를 정리하여 사용자에게 제공
```

#### 2. 이슈 추적 + 계산
```
사용자: "How many bugs are assigned to me and what's 20% of that number?"
AI:
1. jira_search_issues("assignee = currentUser() AND type = Bug") → 15개 이슈
2. calculator_basic_calculation(a=15, b=0.2, operation="multiply") → 3
3. "15개 버그가 할당되어 있고, 20%는 3개입니다"
```

#### 3. 팀 커뮤니케이션 + 통계
```
사용자: "Get my calculation stats and share a summary in #dev-team"
AI:
1. calculator_get_stats() → 통계 조회
2. slack_send_message(channel="#dev-team", text="오늘 25번의 계산을 수행했습니다")
```

### 복합 워크플로우 예시

#### 프로젝트 대시보드 생성
```
사용자: "Create a project dashboard with current metrics"
AI:
1. jira_search_issues("project = AIDT AND status != Done") → 진행 중 이슈
2. confluence_search_content("dashboard") → 기존 대시보드 찾기
3. calculator_basic_calculation(...) → 완료율 계산
4. 종합적인 대시보드 정보 제공
```

## 📊 도구 성능 및 제한사항

### 성능 지표
- **평균 응답시간**: 1-5ms (Calculator) / 100-500ms (외부 API)
- **동시 요청**: 최대 10개 클라이언트
- **처리량**: 초당 100회 요청

### 일반적인 제한사항
- **Calculator**: 수치 크기 제한 (1e15), 정밀도 제한 (15자리)
- **Confluence/JIRA**: API 레이트 리미팅, 권한 제한
- **Slack**: 메시지 길이 제한, 채널 권한 제한

### 오류 처리
모든 도구는 표준화된 오류 응답을 제공:
```json
{
  "success": false,
  "message": "오류 설명",
  "error_type": "ErrorType",
  "details": "상세 정보"
}
```

## 🔗 관련 문서

- [MCP 클라이언트 설정 가이드](./MCP_CLIENT_SETUP.md)
- [Calculator 전용 가이드](./README_CALCULATOR.md)
- [메인 프로젝트 문서](../README.md)
- [개발자 가이드](../CLAUDE.md)

**💡 팁**: MCP 도구들은 자연어 명령으로 쉽게 호출할 수 있으며, AI가 자동으로 적절한 매개변수를 전달합니다. 복잡한 워크플로우도 여러 도구를 조합하여 한 번에 처리할 수 있습니다.