"""
テスト用のデータベースセッションを提供するモジュール
"""
import os
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# プロジェクトのルートディレクトリをPythonパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# テスト用の設定
os.environ["TESTING"] = "True"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

# アプリケーションのモデルをインポート
from app.db.base import Base  # noqa: E402

# SQLiteエンジンの作成
engine = create_engine(
    "sqlite:///./test.db",
    connect_args={"check_same_thread": False}  # SQLite用の設定
)

# セッションファクトリの作成
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)