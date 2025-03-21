#!/bin/bash
# 直接テストを実行するスクリプト

# スクリプトのディレクトリを取得
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# 環境変数を設定
export TESTING=True
export DATABASE_URL=sqlite:///./test.db

# テスト用ディレクトリの作成
mkdir -p test-reports

# テストを実行
python -m tests.run_direct_test

# 終了コードの取得
EXIT_CODE=$?

# テスト結果の表示
if [ $EXIT_CODE -eq 0 ]; then
  echo "すべてのテストが成功しました！"
else
  echo "テスト実行中にエラーが発生しました。終了コード: $EXIT_CODE"
fi

exit $EXIT_CODE