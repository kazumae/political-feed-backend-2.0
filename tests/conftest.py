"""
テスト用の設定ファイル
"""
import pytest
from app.core.config import settings
from app.core.security import get_password_hash
from app.main import app
from app.models.user import User
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from tests.db_session import Base, TestSessionLocal, engine


@pytest.fixture
def client():
    """
    テスト用のクライアントを作成
    """
    with TestClient(app) as c:
        yield c


@pytest.fixture
def auth_token(client: TestClient, db: Session):
    """
    認証トークンを取得するフィクスチャ
    """
    # テストユーザーの作成
    user = User(
        email="test_auth@example.com",
        username="test_auth_user",
        password_hash=get_password_hash("password123"),
        role="user",
        status="active",
        email_verified=True
    )
    db.add(user)
    db.commit()
    
    # ログインリクエスト
    login_data = {
        "username": "test_auth@example.com",
        "password": "password123"
    }
    response = client.post(f"{settings.API_V1_STR}/auth/login", data=login_data)
    
    # トークンを取得
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def auth_client(client: TestClient, auth_token):
    """
    認証済みのクライアントを提供するフィクスチャ
    """
    def _auth_client(url, **kwargs):
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {auth_token}"
        return client.request(url=url, headers=headers, **kwargs)
    
    return _auth_client


@pytest.fixture(scope="function")
def db() -> Session:
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
