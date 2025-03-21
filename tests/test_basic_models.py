"""
基本的なモデルテスト
"""
import os
import sys
import uuid
from datetime import datetime

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# プロジェクトのルートディレクトリをPythonパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 環境変数を設定
os.environ["TESTING"] = "True"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

# アプリケーションのモデルをインポート
from app.db.base import Base  # noqa: E402
from app.models.party import Party  # noqa: E402
from app.models.user import User  # noqa: E402

# SQLiteエンジンの作成
engine = create_engine(
    "sqlite:///./test.db",
    connect_args={"check_same_thread": False}  # SQLite用の設定
)

# セッションファクトリの作成
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """
    テスト用のデータベースセッションを提供するフィクスチャ
    """
    # テスト用のデータベースを初期化
    Base.metadata.create_all(bind=engine)
    
    # セッションを作成
    session = TestSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
    
    # テスト後にデータベースをクリーンアップ
    Base.metadata.drop_all(bind=engine)


def test_user_model(db_session):
    """
    ユーザーモデルのテスト
    """
    # テスト用のユーザーを作成
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password",
        role="user",
        status="active",
        email_verified=1
    )
    
    # データベースに追加
    db_session.add(user)
    db_session.commit()
    
    # データベースから取得
    db_user = db_session.query(User).filter(User.username == "testuser").first()
    
    # 検証
    assert db_user is not None
    assert db_user.id == user_id
    assert db_user.username == "testuser"
    assert db_user.email == "test@example.com"
    assert db_user.role == "user"
    assert db_user.status == "active"
    assert db_user.email_verified == 1


def test_party_model(db_session):
    """
    政党モデルのテスト
    """
    # テスト用の政党を作成
    party_id = str(uuid.uuid4())
    party = Party(
        id=party_id,
        name="テスト政党",
        short_name="テスト",
        status="active",
        founded_date=datetime(2020, 1, 1),
        description="テスト用の政党です"
    )
    
    # データベースに追加
    db_session.add(party)
    db_session.commit()
    
    # データベースから取得
    db_party = db_session.query(Party).filter(Party.name == "テスト政党").first()
    
    # 検証
    assert db_party is not None
    assert db_party.id == party_id
    assert db_party.name == "テスト政党"
    assert db_party.short_name == "テスト"
    assert db_party.status == "active"
    assert db_party.founded_date == datetime(2020, 1, 1)
    assert db_party.description == "テスト用の政党です"


if __name__ == "__main__":
    pytest.main(["-v", __file__])