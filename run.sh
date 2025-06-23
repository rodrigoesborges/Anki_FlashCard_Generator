#!/bin/bash
# Anki 플래시카드 생성기 실행 스크립트

echo "=== Anki 플래시카드 생성기 설치 및 실행 ==="

# Python 버전 확인
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3이 설치되어 있지 않습니다."
    exit 1
fi

# 가상환경 생성 (없는 경우)
if [ ! -d ".venv" ]; then
    echo "가상환경 생성 중..."
    python3 -m venv .venv
fi

# 가상환경 활성화
echo "가상환경 활성화 중..."
source .venv/bin/activate

# 의존성 설치
echo "의존성 설치 중..."
pip install -r requirements.txt

# .env 파일 확인
if [ ! -f ".env" ]; then
    echo ".env 파일이 없습니다. .env.example을 복사합니다..."
    cp .env.example .env
    echo "주의: .env 파일에 API 키를 설정해주세요!"
fi

# 필요한 디렉토리 생성
mkdir -p SOURCE_DOCUMENTS output logs

# 메인 애플리케이션 실행
echo "애플리케이션 실행 중..."
python -m src.main

# 가상환경 비활성화
deactivate 