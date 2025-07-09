# 🐍 Ruff 린트 설정 가이드

Python 코드 품질 관리를 위한 **Ruff** 설정 및 사용법을 안내합니다.

## 📋 Ruff란?

Ruff는 **매우 빠르고 강력한 Python 린터**입니다.
- ⚡ **빠른 속도**: Rust로 작성되어 매우 빠름
- 🔧 **자동 수정**: `--fix` 옵션으로 자동 수정 가능
- 📦 **통합 도구**: flake8, pylint, black, isort 등을 대체
- 🎯 **맞춤 설정**: 프로젝트에 맞는 세밀한 설정 가능

## 🚀 설치 및 설정

### 1. 설치
```bash
# 가상환경 활성화
source .venv/bin/activate

# ruff 설치
pip install ruff
```

### 2. 설정 파일
`pyproject.toml`에 ruff 설정이 포함되어 있습니다:
```toml
[tool.ruff]
# 린트 규칙 선택
select = ["E", "F", "I", "W", "B", "C4", "UP", "N", "ARG", "SIM", "TCH", "Q", "RUF"]
ignore = [
    "E501",  # line too long, handled by black
    "B008",  # do not perform function calls in argument defaults
    "C901",  # too complex
]

# 자동 수정 설정
fixable = ["ALL"]
unfixable = []

# 코드 스타일
line-length = 88
indent-width = 4
target-version = "py38"
```

## 🎯 사용법

### 기본 린트 검사
```bash
# 전체 src/ 디렉토리 검사
ruff check src/

# 특정 파일 검사
ruff check src/server.py

# 자동 수정 가능한 오류 수정
ruff check --fix src/
```

### 코드 포맷팅
```bash
# 코드 포맷팅
ruff format src/

# 포맷팅 검사 (수정하지 않고 확인만)
ruff format --check src/
```

### 통합 명령어
```bash
# 린트 + 포맷팅 한 번에
ruff check src/ && ruff format src/

# 모든 검사 통과 확인
ruff check src/ && echo "✅ Lint passed!" && ruff format --check src/ && echo "✅ Format passed!"
```

## 🔧 IDE 연동

### VSCode/Cursor
1. **Python 확장** 설치
2. **Ruff 확장** 설치 (선택사항)
3. 설정에서 기본 린터를 ruff로 설정

```json
// settings.json
{
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "ruff"
}
```

### 자동 저장 시 린트
```json
{
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll": true
  }
}
```

## 📊 린트 규칙 설명

### 주요 규칙 카테고리
- **E**: pycodestyle 오류 (PEP 8)
- **F**: Pyflakes (사용하지 않는 import, 변수 등)
- **I**: isort (import 정렬)
- **W**: pycodestyle 경고
- **B**: flake8-bugbear (버그 가능성)
- **C4**: flake8-comprehensions (리스트 컴프리헨션)
- **UP**: pyupgrade (Python 버전 업그레이드)
- **N**: pep8-naming (네이밍 컨벤션)
- **ARG**: flake8-unused-arguments (사용하지 않는 인수)
- **SIM**: flake8-simplify (단순화 가능한 코드)
- **TCH**: flake8-type-checking (타입 체킹)
- **Q**: flake8-quotes (따옴표 스타일)
- **RUF**: ruff 전용 규칙

### 무시하는 규칙
- **E501**: 줄 길이 제한 (black이 처리)
- **B008**: 함수 호출을 기본값으로 사용
- **C901**: 복잡도가 너무 높은 함수

## 🛠️ 고급 설정

### 특정 파일/폴더 제외
```toml
[tool.ruff]
exclude = [
    ".venv",
    "node_modules",
    "build",
    "dist"
]
```

### 프로젝트별 규칙 설정
```toml
[tool.ruff.lint]
# 특정 규칙만 활성화
select = ["E", "F", "I"]

# 특정 규칙 무시
ignore = ["E501", "F401"]
```

### Import 정렬 설정
```toml
[tool.ruff.lint.isort]
known-first-party = ["src"]
force-sort-within-sections = true
```

## 🔍 문제 해결

### 일반적인 오류
1. **Import 오류**: `ruff check --fix`로 자동 수정
2. **포맷팅 오류**: `ruff format`으로 자동 정렬
3. **복잡도 오류**: 함수를 더 작은 단위로 분리

### 설정 문제
1. **pyproject.toml 확인**: 설정 파일 문법 오류 확인
2. **버전 호환성**: Python 버전과 ruff 버전 확인
3. **경로 문제**: exclude 설정 확인

## 📚 추가 리소스

- [Ruff 공식 문서](https://docs.astral.sh/ruff/)
- [Ruff GitHub](https://github.com/astral-sh/ruff)
- [Python 코드 스타일 가이드](https://peps.python.org/pep-0008/)

## 🎯 권장 워크플로우

1. **개발 중**: IDE에서 실시간 린트 확인
2. **커밋 전**: `ruff check --fix src/` 실행
3. **CI/CD**: `ruff check src/ && ruff format --check src/` 검사
4. **정기적**: 전체 프로젝트 린트 검사 및 정리

---

**Ruff를 사용하면 Python 코드 품질을 쉽고 빠르게 관리할 수 있습니다!** 🚀 