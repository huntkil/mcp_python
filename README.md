# Markdown MCP Server

Cursor AI IDE에서 사용할 수 있는 Markdown 문서 관리 MCP (Model Context Protocol) 서버입니다.

## 개요

이 프로젝트는 Cursor AI IDE에서 Markdown 문서의 CRUD 작업을 효율적으로 수행할 수 있도록 하는 MCP 서버를 제공합니다. 문서 생성, 읽기, 수정, 삭제뿐만 아니라 검색, 메타데이터 관리 등 고급 기능을 지원합니다.

## 주요 기능

### 기본 CRUD 작업
- **문서 생성**: 새로운 Markdown 파일 생성
- **문서 읽기**: 기존 Markdown 파일 내용 읽기
- **문서 수정**: 기존 파일 내용 수정 또는 추가
- **문서 삭제**: Markdown 파일 삭제

### 고급 기능
- **문서 목록 조회**: 디렉토리 내 Markdown 파일 목록 조회
- **내용 검색**: 파일 내용에서 키워드 검색
- **메타데이터 관리**: YAML frontmatter 관리 (추가, 수정, 삭제)

## 기술 스택

- **언어**: Python 3.9+
- **프레임워크**: MCP Python SDK
- **문서 형식**: Markdown (.md, .markdown)
- **의존성**: `mcp`, `pyyaml`, `pathlib2`, `typing-extensions`

## 설치

### 1. 저장소 클론
```bash
git clone <repository-url>
cd markdown-mcp-server
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 개발 모드 설치 (선택사항)
```bash
pip install -e .
```

## 사용법

### Cursor AI IDE 설정

Cursor AI IDE의 설정 파일에 MCP 서버를 추가하세요:

```json
{
  "mcp": {
    "servers": {
      "markdown-manager": {
        "command": "python",
        "args": ["-m", "src.server"],
        "cwd": "/path/to/markdown-mcp-server"
      }
    }
  }
}
```

### 환경 변수

- `MARKDOWN_MCP_BASE_PATH`: 파일 작업의 기본 디렉토리 (기본값: 현재 디렉토리)

## API 참조

### 1. read_markdown
Markdown 파일을 읽어서 내용을 반환합니다.

**매개변수:**
- `file_path` (string): 읽을 파일의 경로
- `encoding` (optional, string): 파일 인코딩 (기본값: "utf-8")

**반환값:**
```json
{
  "success": true,
  "content": "파일 내용",
  "content_without_frontmatter": "frontmatter 제외한 내용",
  "frontmatter": {"title": "제목", "author": "작성자"},
  "file_info": {"name": "파일명", "size": 1024, ...},
  "encoding": "utf-8"
}
```

### 2. create_markdown
새로운 Markdown 파일을 생성합니다.

**매개변수:**
- `file_path` (string): 생성할 파일의 경로
- `content` (string): 파일 내용
- `overwrite` (optional, boolean): 기존 파일 덮어쓰기 여부 (기본값: false)

**반환값:**
```json
{
  "success": true,
  "message": "File created successfully: file.md",
  "file_path": "/full/path/to/file.md",
  "file_info": {"name": "file.md", "size": 1024, ...}
}
```

### 3. update_markdown
기존 Markdown 파일의 내용을 수정합니다.

**매개변수:**
- `file_path` (string): 수정할 파일의 경로
- `content` (string): 새로운 내용
- `append` (optional, boolean): 내용 추가 여부 (기본값: false)

**반환값:**
```json
{
  "success": true,
  "message": "File updated successfully: file.md",
  "file_path": "/full/path/to/file.md",
  "file_info": {"name": "file.md", "size": 1024, ...}
}
```

### 4. delete_markdown
지정된 Markdown 파일을 삭제합니다.

**매개변수:**
- `file_path` (string): 삭제할 파일의 경로
- `confirm` (optional, boolean): 삭제 확인 (기본값: false)

**반환값:**
```json
{
  "success": true,
  "message": "File deleted successfully: file.md"
}
```

### 5. list_markdown_files
지정된 디렉토리의 Markdown 파일 목록을 반환합니다.

**매개변수:**
- `directory` (optional, string): 검색할 디렉토리 경로 (기본값: ".")
- `recursive` (optional, boolean): 하위 디렉토리 포함 여부 (기본값: false)
- `pattern` (optional, string): 파일 패턴 (기본값: "*.md")

**반환값:**
```json
{
  "success": true,
  "files": [
    {
      "name": "file1.md",
      "size": 1024,
      "modified": 1234567890,
      "relative_path": "file1.md"
    }
  ],
  "count": 1,
  "directory": "."
}
```

### 6. search_markdown
Markdown 파일 내용에서 키워드를 검색합니다.

**매개변수:**
- `directory` (string): 검색할 디렉토리
- `query` (string): 검색 키워드
- `case_sensitive` (optional, boolean): 대소문자 구분 여부 (기본값: false)

**반환값:**
```json
{
  "success": true,
  "results": [
    {
      "file_path": "file1.md",
      "matches": [
        {"line_number": 5, "line_content": "This line contains the keyword"}
      ],
      "match_count": 1
    }
  ],
  "total_files_searched": 10,
  "files_with_matches": 1,
  "query": "keyword",
  "case_sensitive": false
}
```

### 7. manage_frontmatter
Markdown 파일의 YAML frontmatter를 관리합니다.

**매개변수:**
- `file_path` (string): 대상 파일 경로
- `action` (string): 작업 유형 ("get", "set", "update", "remove")
- `metadata` (optional, object): 메타데이터 정보 (set/update 작업 시 필요)

**반환값 (get 작업):**
```json
{
  "success": true,
  "frontmatter": {"title": "제목", "author": "작성자"},
  "has_frontmatter": true
}
```

**반환값 (기타 작업):**
```json
{
  "success": true,
  "message": "Frontmatter set completed successfully",
  "file_path": "/full/path/to/file.md",
  "action": "set"
}
```

## 사용 예시

### Cursor AI IDE에서 사용

1. **새로운 프로젝트 문서 생성**
   ```
   "새로운 프로젝트 문서를 생성해주세요. 파일명: project-overview.md"
   ```

2. **키워드로 문서 검색**
   ```
   "'API 문서' 키워드가 포함된 모든 마크다운 파일을 찾아주세요"
   ```

3. **기존 문서에 내용 추가**
   ```
   "README.md 파일에 설치 가이드 섹션을 추가해주세요"
   ```

4. **메타데이터 관리**
   ```
   "project.md 파일의 frontmatter에 버전 정보를 추가해주세요"
   ```

## 개발

### 프로젝트 구조
```
markdown-mcp-server/
├── src/
│   ├── __init__.py
│   ├── server.py              # MCP 서버 메인 로직
│   ├── markdown_manager.py    # Markdown 문서 관리 클래스
│   └── utils.py              # 유틸리티 함수
├── tests/
│   ├── __init__.py
│   ├── test_server.py
│   └── test_markdown_manager.py
├── requirements.txt
├── setup.py
└── README.md
```

### 테스트 실행
```bash
# 단위 테스트 실행
python -m unittest tests.test_markdown_manager

# 통합 테스트 실행
python -m unittest tests.test_server

# 모든 테스트 실행
python -m unittest discover tests
```

### 서버 실행
```bash
# 직접 실행
python -m src.server

# 환경 변수와 함께 실행
MARKDOWN_MCP_BASE_PATH=/path/to/docs python -m src.server
```

## 보안 고려사항

- **경로 검증**: 모든 파일 경로는 path traversal 공격을 방지하기 위해 검증됩니다.
- **권한 확인**: 파일 시스템 접근 권한을 확인합니다.
- **입력 검증**: 모든 사용자 입력은 검증됩니다.
- **안전한 파일 처리**: 파일 크기 제한 및 인코딩 문제를 처리합니다.

## 에러 처리

모든 API 호출은 일관된 에러 응답 형식을 반환합니다:

```json
{
  "error": "에러 메시지 설명"
}
```

일반적인 에러 상황:
- 파일이 존재하지 않는 경우
- 권한이 없는 경우
- 잘못된 파일 경로
- 인코딩 오류
- 디렉토리가 존재하지 않는 경우

## 로깅

서버는 구조화된 로깅을 제공합니다:
- INFO: 일반적인 작업 로그
- WARNING: 경고 상황
- ERROR: 오류 상황

로그 레벨은 환경 변수 `LOG_LEVEL`로 설정할 수 있습니다.

## 기여하기

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 지원

문제가 발생하거나 질문이 있으시면 GitHub Issues를 통해 문의해 주세요.

## 변경 이력

### v0.1.0
- 초기 버전 릴리스
- 기본 CRUD 기능 구현
- 검색 및 메타데이터 관리 기능 추가
- MCP 서버 통합
- 테스트 코드 작성 