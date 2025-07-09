# Markdown MCP Server with Obsidian Integration

Cursor AI IDE에서 사용할 수 있는 Markdown 문서 관리 및 Obsidian 볼트 관리 MCP (Model Context Protocol) 서버입니다.

## 개요

이 프로젝트는 Cursor AI IDE에서 Markdown 문서의 CRUD 작업과 Obsidian 볼트 관리를 효율적으로 수행할 수 있도록 하는 MCP 서버를 제공합니다. 문서 생성, 읽기, 수정, 삭제뿐만 아니라 검색, 메타데이터 관리, Obsidian 전용 기능 등 고급 기능을 지원합니다.

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

### Obsidian 전용 기능
- **볼트 정보 조회**: Obsidian 볼트의 전체 정보 및 통계
- **노트 관리**: Obsidian 노트의 CRUD 작업
- **태그 추출**: 볼트 내 모든 태그 추출 및 관리
- **내부 링크 관리**: 노트 간 링크 관계 추출
- **템플릿 시스템**: 노트 템플릿 생성 및 사용
- **고급 검색**: 컨텍스트를 포함한 노트 검색

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
- `OBSIDIAN_VAULT_PATH`: Obsidian 볼트 경로 (선택사항, 설정 시 Obsidian 기능 활성화)

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

## Obsidian API 참조

Obsidian 볼트가 설정된 경우 사용할 수 있는 추가 API들입니다.

### 1. obsidian_vault_info
Obsidian 볼트의 정보를 반환합니다.

**매개변수:** 없음

**반환값:**
```json
{
  "vault_path": "/path/to/vault",
  "total_notes": 150,
  "total_attachments": 25,
  "total_size_bytes": 1048576,
  "created_at": "2024-01-01T00:00:00",
  "last_modified": "2024-01-15T12:30:00"
}
```

### 2. obsidian_list_notes
Obsidian 볼트의 노트 목록을 반환합니다.

**매개변수:**
- `folder` (optional, string): 하위 폴더 경로 (기본값: "")
- `recursive` (optional, boolean): 재귀 검색 여부 (기본값: true)

**반환값:**
```json
[
  {
    "filename": "note1.md",
    "path": "note1.md",
    "folder": "",
    "size_bytes": 1024,
    "created_at": "2024-01-01T00:00:00",
    "modified_at": "2024-01-15T12:30:00",
    "frontmatter": {"title": "Note 1"},
    "has_content": true
  }
]
```

### 3. obsidian_read_note
Obsidian 노트를 읽습니다.

**매개변수:**
- `note_path` (string): 노트 경로 (볼트 루트 기준)

**반환값:**
```json
{
  "path": "note1.md",
  "filename": "note1.md",
  "content": "# Note 1\n\nContent...",
  "body": "# Note 1\n\nContent...",
  "frontmatter": {"title": "Note 1"},
  "size_bytes": 1024,
  "created_at": "2024-01-01T00:00:00",
  "modified_at": "2024-01-15T12:30:00"
}
```

### 4. obsidian_create_note
새로운 Obsidian 노트를 생성합니다.

**매개변수:**
- `note_path` (string): 노트 경로
- `content` (optional, string): 노트 내용 (기본값: "")
- `frontmatter` (optional, object): frontmatter 메타데이터

**반환값:**
```json
{
  "path": "new_note.md",
  "filename": "new_note.md",
  "content": "# New Note\n\nContent...",
  "body": "# New Note\n\nContent...",
  "frontmatter": {"title": "New Note"},
  "size_bytes": 512,
  "created_at": "2024-01-15T12:30:00",
  "modified_at": "2024-01-15T12:30:00"
}
```

### 5. obsidian_update_note
기존 Obsidian 노트를 수정합니다.

**매개변수:**
- `note_path` (string): 노트 경로
- `content` (optional, string): 새로운 내용
- `frontmatter` (optional, object): 새로운 frontmatter
- `append` (optional, boolean): 내용 추가 여부 (기본값: false)

**반환값:**
```json
{
  "path": "note1.md",
  "filename": "note1.md",
  "content": "# Updated Note\n\nUpdated content...",
  "body": "# Updated Note\n\nUpdated content...",
  "frontmatter": {"title": "Updated Note"},
  "size_bytes": 1024,
  "created_at": "2024-01-01T00:00:00",
  "modified_at": "2024-01-15T12:30:00"
}
```

### 6. obsidian_delete_note
Obsidian 노트를 삭제합니다.

**매개변수:**
- `note_path` (string): 삭제할 노트 경로

**반환값:**
```json
{
  "deleted": true,
  "path": "note1.md",
  "filename": "note1.md",
  "deleted_at": "2024-01-15T12:30:00"
}
```

### 7. obsidian_search_notes
Obsidian 노트에서 키워드를 검색합니다.

**매개변수:**
- `query` (string): 검색 키워드
- `folder` (optional, string): 검색할 폴더 (기본값: "")
- `case_sensitive` (optional, boolean): 대소문자 구분 (기본값: false)

**반환값:**
```json
[
  {
    "path": "note1.md",
    "filename": "note1.md",
    "folder": "",
    "matches": 2,
    "matching_lines": [
      {
        "line_number": 5,
        "context": ["Line 3", "Line 4", "Line 5", "Line 6", "Line 7"],
        "highlighted_line": "This line contains the keyword"
      }
    ],
    "size_bytes": 1024,
    "modified_at": "2024-01-15T12:30:00"
  }
]
```

### 8. obsidian_get_tags
볼트의 모든 태그를 추출합니다.

**매개변수:** 없음

**반환값:**
```json
{
  "tag1": ["note1.md", "note2.md"],
  "tag2": ["note1.md"],
  "project": ["project-notes.md"]
}
```

### 9. obsidian_get_links
볼트의 모든 내부 링크를 추출합니다.

**매개변수:** 없음

**반환값:**
```json
{
  "note1.md": ["note2.md", "note3.md"],
  "note2.md": ["note1.md"]
}
```

### 10. obsidian_create_template
템플릿을 생성합니다.

**매개변수:**
- `template_name` (string): 템플릿 이름
- `content` (string): 템플릿 내용
- `frontmatter` (optional, object): 템플릿 frontmatter

**반환값:**
```json
{
  "name": "meeting_template",
  "path": "templates/meeting_template.md",
  "content": "# {{title}}\n\n## 참석자\n{{attendees}}\n\n## 안건\n{{agenda}}",
  "created_at": "2024-01-15T12:30:00"
}
```

### 11. obsidian_list_templates
사용 가능한 템플릿 목록을 반환합니다.

**매개변수:** 없음

**반환값:**
```json
[
  {
    "name": "meeting_template",
    "path": "templates/meeting_template.md",
    "content": "# {{title}}\n\n## 참석자\n{{attendees}}",
    "body": "# {{title}}\n\n## 참석자\n{{attendees}}",
    "frontmatter": {"type": "template"},
    "size_bytes": 512,
    "created_at": "2024-01-15T12:30:00",
    "modified_at": "2024-01-15T12:30:00"
  }
]
```

### 12. obsidian_create_note_from_template
템플릿을 사용하여 노트를 생성합니다.

**매개변수:**
- `template_name` (string): 사용할 템플릿 이름
- `note_path` (string): 생성할 노트 경로
- `variables` (optional, object): 템플릿 변수

**반환값:**
```json
{
  "path": "meeting_notes.md",
  "filename": "meeting_notes.md",
  "content": "# 팀 미팅\n\n## 참석자\n김철수, 이영희\n\n## 안건\n프로젝트 진행상황",
  "body": "# 팀 미팅\n\n## 참석자\n김철수, 이영희\n\n## 안건\n프로젝트 진행상황",
  "frontmatter": {},
  "size_bytes": 1024,
  "created_at": "2024-01-15T12:30:00",
  "modified_at": "2024-01-15T12:30:00"
}
```

## 사용 예시

### Cursor AI IDE에서 사용

#### 기본 Markdown 기능

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

#### Obsidian 전용 기능

1. **Obsidian 볼트 정보 조회**
   ```
   "내 Obsidian 볼트의 정보를 알려주세요"
   ```

2. **노트 목록 조회**
   ```
   "Obsidian 볼트의 모든 노트 목록을 보여주세요"
   ```

3. **새로운 노트 생성**
   ```
   "새로운 미팅 노트를 생성해주세요. 파일명: meeting-2024-01-15.md"
   ```

4. **노트 내용 검색**
   ```
   "프로젝트 키워드가 포함된 모든 노트를 찾아주세요"
   ```

5. **태그 관리**
   ```
   "볼트의 모든 태그를 추출해주세요"
   ```

6. **템플릿 사용**
   ```
   "미팅 템플릿을 사용해서 새로운 노트를 만들어주세요"
   ```

7. **노트 링크 관계 확인**
   ```
   "노트 간의 링크 관계를 보여주세요"
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