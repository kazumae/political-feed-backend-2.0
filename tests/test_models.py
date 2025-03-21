import os
import sys
from datetime import datetime

import pytest
from sqlalchemy.orm import Session

# プロジェクトのルートディレクトリをPythonパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 環境変数を設定
os.environ["TESTING"] = "True"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from app.models.party import Party
from app.models.politician import Politician

# モデルのインポート
from app.models.user import User

# テスト用のデータベースセッションをインポート
from tests.db_session import Base, TestSessionLocal, engine


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
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password",
        role="user",
        status="active",
        email_verified=True
    )
    
    # データベースに追加
    db_session.add(user)
    db_session.commit()
    
    # データベースから取得
    db_user = db_session.query(User).filter(User.username == "testuser").first()
    
    # 検証
    assert db_user is not None
    assert db_user.username == "testuser"
    assert db_user.email == "test@example.com"
    assert db_user.role == "user"
    assert db_user.status == "active"
    assert db_user.email_verified is True


def test_party_model(db_session):
    """
    政党モデルのテスト
    """
    # テスト用の政党を作成
    party = Party(
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
    assert db_party.name == "テスト政党"
    assert db_party.short_name == "テスト"
    assert db_party.status == "active"
    assert db_party.founded_date == datetime(2020, 1, 1)
    assert db_party.description == "テスト用の政党です"


def test_politician_model(db_session):
    """
    政治家モデルのテスト
    """
    # テスト用の政党を作成
    party = Party(
        name="テスト政党",
        short_name="テスト",
        status="active"
    )
    db_session.add(party)
    db_session.commit()
    
    # テスト用の政治家を作成
    politician = Politician(
        name="テスト太郎",
        name_kana="テストタロウ",
        current_party_id=party.id,
        role="代表",
        status="active",
        profile_summary="テスト用の政治家です"
    )
    
    # データベースに追加
    db_session.add(politician)
    db_session.commit()
    
    # データベースから取得
    db_politician = db_session.query(Politician).filter(Politician.name == "テスト太郎").first()
    
    # 検証
    assert db_politician is not None
    assert db_politician.name == "テスト太郎"
    assert db_politician.name_kana == "テストタロウ"
    assert db_politician.current_party_id == party.id
    assert db_politician.role == "代表"
    assert db_politician.status == "active"
    assert db_politician.profile_summary == "テスト用の政治家です"


if __name__ == "__main__":
    pytest.main(["-v", __file__])