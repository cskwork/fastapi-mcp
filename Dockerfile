# Python 3.12 기반 이미지 사용
FROM python:3.12-slim

# 작업 디렉터리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 도구 설치
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# uv 설치 (Python 패키지 관리자)
RUN pip install uv

# 프로젝트 파일 복사
COPY pyproject.toml uv.lock* ./

# 의존성 설치
RUN uv sync --frozen

# 소스 코드 복사
COPY src/ ./src/
COPY scripts/ ./scripts/

# 환경 변수 설정
ENV PYTHONPATH="/app/src"
ENV PATH="/app/.venv/bin:$PATH"

# 헬스체크 설정
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# 포트 노출
EXPOSE 8000

# 애플리케이션 실행
CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]