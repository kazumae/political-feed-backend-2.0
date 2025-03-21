#!/bin/bash
# __pycache__ディレクトリを削除するスクリプト

# スクリプトのディレクトリを取得
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR/.."

# Dockerコンテナ内の__pycache__ディレクトリを削除
docker-compose -f docker-compose.test.yml run --rm api_test sh -c "find /app -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true"

echo "__pycache__ディレクトリを削除しました"