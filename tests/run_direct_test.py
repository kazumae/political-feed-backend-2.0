"""
直接テストを実行するスクリプト
"""
import os
import sys

import pytest

# 環境変数を設定
os.environ["TESTING"] = "True"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

# プロジェクトのルートディレクトリをPythonパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# テストを実行
if __name__ == "__main__":
    # テスト対象のファイルを指定
    test_files = [
        "tests/test_basic.py",
        "tests/test_models.py"
    ]
    
    # pytestを実行
    exit_code = pytest.main(["-v"] + test_files)
    
    # 終了コードを返す
    sys.exit(exit_code)