# 🚀 IDE 연동 가이드

다양한 IDE에서 MCP 서버를 연동하는 방법을 안내합니다.

## 📋 지원 IDE 목록

### ✅ 공식 MCP 지원 IDE
- **Cursor IDE** - 가장 완벽한 MCP 지원
- **VSCode** - MCP 확장 플러그인 필요
- **Neovim** - nvim-mcp 플러그인 필요

### ⚠️ 제한적 지원 IDE
- **JetBrains IDE** (IntelliJ, PyCharm 등) - 플러그인 개발 필요
- **Sublime Text** - 플러그인 개발 필요
- **Atom** - 플러그인 개발 필요

## 🔧 설정 방법

### 1. Cursor IDE (권장)
```json
// cursor-settings.json
{
  "mcp": {
    "servers": {
      "markdown-manager": {
        "command": "bash",
        "args": ["-c", "source .venv/bin/activate && python -m src.server"],
        "cwd": "/Users/gukho/Desktop/git/mcp_python"
      }
    }
  }
}
```

### 2. VSCode
```json
// .vscode/settings.json
{
  "mcp.servers": {
    "markdown-manager": {
      "command": "bash",
      "args": ["-c", "source .venv/bin/activate && python -m src.server"],
      "cwd": "/Users/gukho/Desktop/git/mcp_python"
    }
  }
}
```

### 3. Neovim
```lua
-- init.lua
local mcp_config = {
  servers = {
    ["markdown-manager"] = {
      command = "bash",
      args = {"-c", "source .venv/bin/activate && python -m src.server"},
      cwd = "/Users/gukho/Desktop/git/mcp_python"
    }
  }
}
require('mcp').setup(mcp_config)
```

### 4. Windows 환경
```json
// CMD 사용
{
  "mcp": {
    "servers": {
      "markdown-manager": {
        "command": "cmd",
        "args": ["/c", ".venv\\Scripts\\activate && python -m src.server"],
        "cwd": "C:\\Users\\username\\Desktop\\git\\mcp_python"
      }
    }
  }
}

// PowerShell 사용
{
  "mcp": {
    "servers": {
      "markdown-manager": {
        "command": "powershell",
        "args": ["-Command", ".venv\\Scripts\\Activate.ps1; python -m src.server"],
        "cwd": "C:\\Users\\username\\Desktop\\git\\mcp_python"
      }
    }
  }
}
```

## 🎯 사용 방법

### Cursor IDE
1. 설정 파일 적용 후 IDE 재시작
2. 명령창에서 자연어 명령 입력:
   - "README.md 파일을 읽어줘"
   - "새로운 프로젝트 문서를 생성해줘"
   - "My Card 볼트에서 AI 관련 노트 찾아줘"

### VSCode
1. MCP 확장 플러그인 설치
2. 설정 파일 적용
3. 명령 팔레트에서 MCP 명령 실행

### Neovim
1. nvim-mcp 플러그인 설치
2. 설정 파일 적용
3. `:MCPStart` 명령으로 서버 시작

## ⚠️ 주의사항

1. **가상환경 경로**: `.venv/bin/activate` (macOS/Linux) 또는 `.venv\Scripts\activate` (Windows)
2. **프로젝트 경로**: 실제 프로젝트 경로로 수정 필요
3. **의존성**: PyYAML 등 필요한 패키지가 가상환경에 설치되어 있어야 함
4. **권한**: 실행 권한이 있어야 함

## 🔍 문제 해결

### 서버가 실행되지 않는 경우
1. 가상환경 경로 확인
2. 프로젝트 경로 확인
3. 의존성 설치 확인: `pip install pyyaml`

### IDE에서 명령이 동작하지 않는 경우
1. IDE 재시작
2. MCP 서버 실행 상태 확인
3. 로그 확인

## 📚 추가 리소스

- [MCP 공식 문서](https://modelcontextprotocol.io/)
- [Cursor IDE MCP 가이드](https://cursor.sh/docs/mcp)
- [VSCode MCP 확장](https://marketplace.visualstudio.com/items?itemName=modelcontextprotocol.vscode-mcp) 