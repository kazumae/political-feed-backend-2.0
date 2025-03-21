#!/bin/bash
# テスト実行用のスクリプト

# スクリプトのディレクトリを取得
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# 引数の解析
SPECIFIC_TEST=""
VERBOSE=""

while [[ $# -gt 0 ]]; do
  case $1 in
    -v|--verbose)
      VERBOSE="-v"
      shift
      ;;
    --test=*)
      SPECIFIC_TEST="${1#*=}"
      shift
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: $0 [--verbose|-v] [--test=path/to/test]"
      exit 1
      ;;
  esac
done

# テスト用ディレクトリの作成
mkdir -p test-reports

# テスト用のコンテナをビルド
echo "テスト用のコンテナをビルドしています..."
docker-compose -f docker-compose.test.yml build

# テスト用のコンテナを起動
echo "テスト用のコンテナを起動しています..."

# コマンドの構築
if [ -n "$SPECIFIC_TEST" ]; then
  # 特定のテストを実行
  CMD="python -m tests.create_test_data && pytest $VERBOSE --cov=app --cov-report=term --cov-report=html:./test-reports/htmlcov $SPECIFIC_TEST"
else
  # すべてのテストを実行
  CMD="python -m tests.create_test_data && pytest $VERBOSE --cov=app --cov-report=term --cov-report=html:./test-reports/htmlcov tests/"
fi

# テスト実行
docker-compose -f docker-compose.test.yml run --rm api_test sh -c "$CMD"

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