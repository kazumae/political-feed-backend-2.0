#!/bin/bash
# Docker環境でテストを実行するスクリプト

# スクリプトのディレクトリを取得
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 現在のディレクトリをプロジェクトルートに変更
cd "$PROJECT_ROOT"

# 引数の解析
VERBOSE=""
TEST_PATH=""
SKIP_DATA=""

while [[ $# -gt 0 ]]; do
  case $1 in
    -v|--verbose)
      VERBOSE="-v"
      shift
      ;;
    --path=*)
      TEST_PATH="${1#*=}"
      shift
      ;;
    --skip-data)
      SKIP_DATA="--skip-data"
      shift
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# テスト用のDockerコンテナが起動しているか確認
if ! docker ps | grep -q political-feed-api; then
  echo "APIコンテナが起動していません。docker-compose upを実行してください。"
  exit 1
fi

# テスト依存関係のインストール
echo "テスト依存関係をインストールしています..."
docker exec political-feed-api pip install pytest pytest-cov pytest-asyncio

# テストデータの作成（スキップしない場合）
if [[ -z "$SKIP_DATA" ]]; then
  echo "テストデータを作成しています..."
  docker exec political-feed-api python /app/scripts/create_test_data.py
fi

# テストの実行
echo "テストを実行しています..."
if [[ -z "$TEST_PATH" ]]; then
  # 全テストを実行
  docker exec political-feed-api pytest $VERBOSE --cov=app --cov-report=term --cov-report=html /app/tests/
else
  # 指定されたテストを実行
  docker exec political-feed-api pytest $VERBOSE --cov=app --cov-report=term --cov-report=html "/app/$TEST_PATH"
fi

# 終了コードの取得
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
  echo "すべてのテストが成功しました！"
else
  echo "テスト実行中にエラーが発生しました。終了コード: $EXIT_CODE"
fi

exit $EXIT_CODE