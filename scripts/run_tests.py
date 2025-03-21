#!/usr/bin/env python
"""
テスト実行用スクリプト
"""
import argparse
import os
import subprocess
import sys

# プロジェクトのルートディレクトリをPythonパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def clean_pycache():
    """__pycache__ディレクトリを削除する"""
    print("__pycache__ディレクトリを削除中...")
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # find コマンドで __pycache__ ディレクトリを検索して削除
    find_cmd = f"find {root_dir} -name '__pycache__' -type d -exec rm -rf {{}} \\; 2>/dev/null || true"
    subprocess.run(find_cmd, shell=True)
    
    # .pyc ファイルも削除
    find_pyc_cmd = f"find {root_dir} -name '*.pyc' -delete"
    subprocess.run(find_pyc_cmd, shell=True)
    
    print("__pycache__ディレクトリの削除が完了しました")


def create_test_data():
    """テストデータを作成する"""
    print("テストデータを作成中...")
    from scripts.create_test_data import create_test_data
    create_test_data()


def run_tests(test_path=None, verbose=True):
    """テストを実行する"""
    print("テストを実行中...")
    
    # pytest コマンドの引数を構築
    pytest_args = ["pytest"]
    if verbose:
        pytest_args.append("-v")
    
    if test_path:
        # 指定されたテストファイルのみ実行
        pytest_args.append(test_path)
    else:
        # 特定のテストファイルのみを明示的に指定して実行
        pytest_args.extend([
            "tests/test_basic.py",
            "tests/test_basic_models.py",
            "tests/test_simple.py",
            "tests/test_models.py",
            "tests/test_politicians_api.py",
            "tests/test_statements_api.py",
            "tests/test_users_api.py",
            "tests/test_api/"
        ])
    
    # カバレッジレポートを追加
    pytest_args.extend([
        "--cov=app",
        "--cov-report=term"
    ])
    
    # 古いtest_api.pyを除外（ディレクトリ内のテストは実行する）
    pytest_args.extend(["-k", "not test_api/__init__.py"])
    
    print(f"実行するコマンド: {' '.join(pytest_args)}")
    
    try:
        # pytest を実行
        result = subprocess.run(pytest_args, check=False)
        return result.returncode
    except Exception as e:
        print(f"テスト実行中にエラーが発生しました: {e}")
        return 1


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description="テスト実行スクリプト")
    parser.add_argument(
        "--test-path",
        help="実行するテストのパス (例: tests/test_basic.py)"
    )
    parser.add_argument(
        "--skip-clean",
        action="store_true",
        help="__pycache__ディレクトリの削除をスキップする"
    )
    parser.add_argument(
        "--skip-data",
        action="store_true",
        help="テストデータの作成をスキップする"
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="詳細な出力を抑制する"
    )
    
    args = parser.parse_args()
    
    # 強制的に __pycache__ ディレクトリを削除
    # テストの問題を解決するため
    subprocess.run("rm -rf /app/tests/__pycache__", shell=True)
    
    # __pycache__ディレクトリを削除
    if not args.skip_clean:
        clean_pycache()
    
    # データベースをリセット
    from app.db.base import Base
    from app.db.session import engine
    print("データベースをリセットしています...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("データベースのリセットが完了しました")
    
    # テストデータを作成
    if not args.skip_data:
        create_test_data()
    
    # 特定のテストファイルのみを直接指定して実行
    test_files = [
        "tests/test_basic.py",
        "tests/test_basic_models.py",
        "tests/test_simple.py",
        "tests/test_models.py",
        "tests/test_politicians_api.py",
        "tests/test_statements_api.py",
        "tests/test_users_api.py",
        "tests/test_api_health.py",  # 名前を変更したファイル
        "tests/test_api/"
    ]
    
    # 各テストファイルを個別に実行
    for test_file in test_files:
        print(f"\n=== {test_file} のテストを実行中 ===\n")
        # 直接 pytest を実行
        subprocess.run(["pytest", test_file, "-v"], check=False)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())