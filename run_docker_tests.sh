#!/bin/bash
# Docker環境でテストを実行するスクリプト

# スクリプトのディレクトリを取得
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# テスト用ディレクトリの作成
mkdir -p test-reports

# テスト用のコンテナをビルド
echo "テスト用のコンテナをビルドしています..."
docker-compose -f docker-compose.test.yml build

# テスト用のコンテナを起動してテストを実行
echo "テストを実行しています..."
docker-compose -f docker-compose.test.yml up --abort-on-container-exit

# 終了コードの取得
EXIT_CODE=$?

# テスト結果の表示
if [ $EXIT_CODE -eq 0 ]; then
  echo "すべてのテストが成功しました！"
  echo "カバレッジレポートは test-reports/htmlcov ディレクトリにあります"
else
  echo "テスト実行中にエラーが発生しました。終了コード: $EXIT_CODE"
fi

# テスト用のコンテナを停止
docker-compose -f docker-compose.test.yml down

exit $EXIT_CODE