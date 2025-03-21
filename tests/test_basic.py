import os
import sys

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# テスト用の設定
os.environ["TESTING"] = "True"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

# プロジェクトのルートディレクトリをPythonパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# SQLiteエンジンの作成
engine = create_engine(
    "sqlite:///./test.db", 
    connect_args={"check_same_thread": False}  # SQLite用の設定
)

# セッションファクトリの作成
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def test_database_connection():
    """
    データベース接続のテスト
    """
    # セッションを作成
    db = TestSessionLocal()
    
    try:
        # 接続テスト（単純なクエリを実行）
        result = db.execute(text("SELECT 1")).scalar()
        assert result == 1
    finally:
        db.close()


def test_environment():
    """
    環境変数のテスト
    """
    assert os.environ.get("TESTING") == "True"
    assert os.environ.get("DATABASE_URL") == "sqlite:///./test.db"


if __name__ == "__main__":
    pytest.main(["-v", __file__])