@echo off
REM MCP Python 서버 자동 설치 스크립트
REM Windows 환경용

echo 🚀 MCP Python 서버 설치를 시작합니다...
echo ==================================

REM Python 버전 확인
echo 📋 Python 버전 확인 중...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python이 설치되지 않았습니다.
    echo    Python 3.8 이상을 설치해주세요.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python %PYTHON_VERSION% 발견

REM 가상환경 생성
echo 📦 가상환경 생성 중...
if not exist ".venv" (
    python -m venv .venv
    echo ✅ 가상환경 생성 완료
) else (
    echo ⚠️  가상환경이 이미 존재합니다.
)

REM 가상환경 활성화
echo 🔧 가상환경 활성화 중...
call .venv\Scripts\activate.bat

REM 의존성 설치
echo 📚 의존성 설치 중...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM 설정 파일 확인
echo ⚙️  설정 파일 확인 중...
if not exist "config.env" (
    echo ⚠️  config.env 파일이 없습니다.
    echo    config.env.example을 참고하여 설정 파일을 생성해주세요.
) else (
    echo ✅ config.env 파일 발견
)

REM 설치 완료
echo.
echo 🎉 설치가 완료되었습니다!
echo ==================================
echo.
echo 📋 다음 단계:
echo 1. config.env 파일에서 경로 설정
echo 2. run_server.bat로 서버 실행
echo 3. IDE 설정 (선택사항)
echo.
echo 📖 자세한 사용법은 '사용방법.md'를 참고하세요.
echo.
pause 