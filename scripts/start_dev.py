#!/usr/bin/env python3
"""개발 서버 시작 스크립트"""

import os
import sys
import subprocess
from pathlib import Path


def setup_environment():
    """개발 환경 설정"""
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # .env 파일 확인
    env_file = project_root / ".env"
    env_example = project_root / ".env.example"
    
    if not env_file.exists():
        print("⚠️  .env 파일이 없습니다.")
        if env_example.exists():
            print(f"📝 {env_example}을 참고하여 .env 파일을 생성하세요.")
        sys.exit(1)
    
    # Python 경로 설정
    src_path = project_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    print(f"🏠 프로젝트 루트: {project_root}")
    print(f"📁 Python 경로에 추가: {src_path}")


def check_dependencies():
    """의존성 확인"""
    print("📦 의존성 확인 중...")
    
    try:
        # uv 설치 확인
        subprocess.run(["uv", "--version"], check=True, capture_output=True)
        print("✅ uv 설치됨")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ uv가 설치되지 않았습니다. 'pip install uv'로 설치하세요.")
        sys.exit(1)
    
    # 의존성 동기화
    print("🔄 의존성 동기화 중...")
    try:
        subprocess.run(["uv", "sync"], check=True)
        print("✅ 의존성 동기화 완료")
    except subprocess.CalledProcessError:
        print("❌ 의존성 동기화 실패")
        sys.exit(1)


def start_server():
    """개발 서버 시작"""
    print("🚀 개발 서버 시작 중...")
    
    # uvicorn으로 서버 시작
    try:
        subprocess.run([
            "uv", "run", "uvicorn",
            "src.main:app",
            "--host", "127.0.0.1",
            "--port", "8000",
            "--reload",
            "--log-level", "info"
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 서버가 중지되었습니다.")
    except subprocess.CalledProcessError as e:
        print(f"❌ 서버 시작 실패: {e}")
        sys.exit(1)


def main():
    """메인 함수"""
    print("🔧 AIDT MCP 개발 서버 시작")
    print("=" * 50)
    
    setup_environment()
    check_dependencies()
    start_server()


if __name__ == "__main__":
    main()