@echo off
REM Anki 플래시카드 생성기 실행 스크립트

echo === Anki 플래시카드 생성기 설치 및 실행 ===

REM Python 버전 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python이 설치되어 있지 않습니다.
    pause
    exit /b 1
)

REM 가상환경 생성 (없는 경우)
if not exist ".venv" (
    echo 가상환경 생성 중...
    python -m venv .venv
)

REM 가상환경 활성화
echo 가상환경 활성화 중...
call .venv\Scripts\activate

REM 의존성 설치
echo 의존성 설치 중...
pip install -r requirements.txt

REM .env 파일 확인
if not exist ".env" (
    echo .env 파일이 없습니다. .env.example을 복사합니다...
    copy .env.example .env
    echo 주의: .env 파일에 API 키를 설정해주세요!
)

REM 필요한 디렉토리 생성
if not exist "SOURCE_DOCUMENTS" mkdir SOURCE_DOCUMENTS
if not exist "output" mkdir output
if not exist "logs" mkdir logs

REM 메인 애플리케이션 실행
echo 애플리케이션 실행 중...
python -m src.main

REM 가상환경 비활성화
deactivate

pause 