@echo off
REM MCP Server 실행 스크립트 (Windows)
REM 환경 변수 로드 및 서버 실행

REM 스크립트 디렉토리로 이동
cd /d "%~dp0"

REM 환경 변수 파일 로드
if exist "config.env" (
    echo 📁 환경 변수 파일 로드 중...
    for /f "tokens=1,* delims==" %%a in (config.env) do (
        if not "%%a"=="" if not "%%a:~0,1%"=="#" (
            set "%%a=%%b"
        )
    )
    echo ✅ 환경 변수 로드 완료
) else (
    echo ⚠️  config.env 파일을 찾을 수 없습니다. 기본 설정을 사용합니다.
)

REM Obsidian 볼트 경로 확인
if defined OBSIDIAN_VAULT_PATH (
    echo 🔗 Obsidian 볼트 경로: %OBSIDIAN_VAULT_PATH%
    
    REM 볼트 경로가 존재하는지 확인
    if not exist "%OBSIDIAN_VAULT_PATH%" (
        echo ❌ Obsidian 볼트 경로가 존재하지 않습니다: %OBSIDIAN_VAULT_PATH%
        echo 📝 볼트를 생성하시겠습니까? (y/n)
        set /p response=
        if /i "%response%"=="y" (
            mkdir "%OBSIDIAN_VAULT_PATH%"
            echo ✅ 볼트 생성 완료: %OBSIDIAN_VAULT_PATH%
        ) else (
            echo ❌ 볼트 경로를 수정해주세요.
            pause
            exit /b 1
        )
    )
) else (
    echo ⚠️  OBSIDIAN_VAULT_PATH가 설정되지 않았습니다.
)

REM 기본 경로 설정
if not defined MARKDOWN_MCP_BASE_PATH (
    set "MARKDOWN_MCP_BASE_PATH=%CD%"
)

echo 📂 기본 경로: %MARKDOWN_MCP_BASE_PATH%
echo 🚀 MCP 서버 시작 중...

REM 가상환경 활성화 및 서버 실행
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
    python -m src.server
) else (
    echo ❌ 가상환경을 찾을 수 없습니다. 먼저 가상환경을 생성해주세요.
    echo python -m venv .venv
    pause
    exit /b 1
) 