#!/bin/bash

# スクリプトの説明
echo "政治家フィード バックエンド リンターとフォーマッター"
echo "=================================================="
echo ""

# 引数の処理
TARGET=${1:-"app tests"}
CHECK_ONLY=false

if [ "$2" == "--check" ]; then
    CHECK_ONLY=true
fi

# ヘルプメッセージ
if [ "$1" == "-h" ] || [ "$1" == "--help" ]; then
    echo "使用方法: ./scripts/lint.sh [ターゲットディレクトリ] [オプション]"
    echo ""
    echo "ターゲットディレクトリ: リンターとフォーマッターを実行するディレクトリ（デフォルト: 'app tests'）"
    echo "オプション:"
    echo "  --check    コードを変更せずにチェックのみ実行"
    echo ""
    echo "例:"
    echo "  ./scripts/lint.sh                     # app と tests ディレクトリに対してリンターとフォーマッターを実行"
    echo "  ./scripts/lint.sh app                 # app ディレクトリのみに対して実行"
    echo "  ./scripts/lint.sh app/api --check     # app/api ディレクトリに対してチェックのみ実行"
    exit 0
fi

echo "ターゲット: $TARGET"
if [ "$CHECK_ONLY" = true ]; then
    echo "モード: チェックのみ（コードは変更されません）"
else
    echo "モード: 自動修正（コードが変更されます）"
fi
echo ""

# isort の実行
echo "isort を実行中..."
if [ "$CHECK_ONLY" = true ]; then
    docker exec political-feed-api isort --check $TARGET
else
    docker exec political-feed-api isort $TARGET
fi
ISORT_EXIT=$?
echo ""

# black の実行
echo "black を実行中..."
if [ "$CHECK_ONLY" = true ]; then
    docker exec political-feed-api black --check $TARGET
else
    docker exec political-feed-api black $TARGET
fi
BLACK_EXIT=$?
echo ""

# flake8 の実行
echo "flake8 を実行中..."
docker exec political-feed-api flake8 $TARGET
FLAKE8_EXIT=$?
echo ""

# 結果の表示
echo "結果サマリー:"
echo "============="
if [ $ISORT_EXIT -eq 0 ]; then
    echo "✅ isort: 問題なし"
else
    echo "❌ isort: 問題あり"
fi

if [ $BLACK_EXIT -eq 0 ]; then
    echo "✅ black: 問題なし"
else
    echo "❌ black: 問題あり"
fi

if [ $FLAKE8_EXIT -eq 0 ]; then
    echo "✅ flake8: 問題なし"
else
    echo "❌ flake8: 問題あり"
fi
echo ""

# 終了コードの設定
if [ $ISORT_EXIT -eq 0 ] && [ $BLACK_EXIT -eq 0 ] && [ $FLAKE8_EXIT -eq 0 ]; then
    echo "🎉 すべてのチェックが成功しました！"
    exit 0
else
    echo "⚠️ 一部のチェックが失敗しました。詳細は上記のログを確認してください。"
    exit 1
fi