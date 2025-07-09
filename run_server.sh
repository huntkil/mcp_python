#!/bin/bash

# MCP Server 실행 스크립트
# 환경 변수 로드 및 서버 실행

# 스크립트 디렉토리로 이동
cd "$(dirname "$0")"

# 환경 변수 파일 로드
if [ -f "config.env" ]; then
    echo "📁 환경 변수 파일 로드 중..."
    # 공백이 포함된 경로를 올바르게 처리
    while IFS= read -r line; do
        # 주석과 빈 줄 제외
        if [[ ! "$line" =~ ^[[:space:]]*# ]] && [[ -n "$line" ]]; then
            export "$line"
        fi
    done < config.env
    echo "✅ 환경 변수 로드 완료"
else
    echo "⚠️  config.env 파일을 찾을 수 없습니다. 기본 설정을 사용합니다."
fi

# Obsidian 볼트 경로 확인
if [ -n "$OBSIDIAN_VAULT_PATH" ]; then
    echo "🔗 Obsidian 볼트 경로: $OBSIDIAN_VAULT_PATH"
    
    # 볼트 경로가 존재하는지 확인
    if [ ! -d "$OBSIDIAN_VAULT_PATH" ]; then
        echo "❌ Obsidian 볼트 경로가 존재하지 않습니다: $OBSIDIAN_VAULT_PATH"
        echo "📝 볼트를 생성하시겠습니까? (y/n)"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            mkdir -p "$OBSIDIAN_VAULT_PATH"
            echo "✅ 볼트 생성 완료: $OBSIDIAN_VAULT_PATH"
        else
            echo "❌ 볼트 경로를 수정해주세요."
            exit 1
        fi
    fi
else
    echo "⚠️  OBSIDIAN_VAULT_PATH가 설정되지 않았습니다."
fi

# 기본 경로 설정
if [ -z "$MARKDOWN_MCP_BASE_PATH" ]; then
    export MARKDOWN_MCP_BASE_PATH="$(pwd)"
fi

echo "📂 기본 경로: $MARKDOWN_MCP_BASE_PATH"
echo "🚀 MCP 서버 시작 중..."

# 서버 실행
python3 -m src.server 