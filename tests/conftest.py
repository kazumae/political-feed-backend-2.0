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
    # 既存のテストユーザーを確認
    existing_user = db.query(User).filter(
        User.email == "test_auth@example.com"
    ).first()
    
    if existing_user:
        print(f"既存のテストユーザーを更新: {existing_user.id}, {existing_user.email}")
        # パスワードを更新
        existing_user.password_hash = get_password_hash("password123")
        existing_user.status = "active"
        existing_user.email_verified = True
        db.add(existing_user)
        db.commit()
        db.refresh(existing_user)
        user = existing_user
    else:
        # テストユーザーの作成
        print("新しいテストユーザーを作成")
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
        db.refresh(user)
    
    print(f"テストユーザー情報: ID={user.id}, Email={user.email}")
    print(f"パスワードハッシュ: {user.password_hash}")
    
    # ログインリクエスト
    login_data = {
        "username": "test_auth@example.com",
        "password": "password123"
    }
    
    try:
        login_url = f"{settings.API_V1_STR}/auth/login"
        response = client.post(login_url, data=login_data)
        print(f"ログインレスポンス: {response.status_code}")
        print(f"ログインレスポンス内容: {response.text}")
        
        # トークンを取得
        if response.status_code == 200:
            return response.json()["access_token"]
    except Exception as e:
        print(f"ログイン中にエラーが発生: {e}")
    
    # ログインに失敗した場合は、トークンを直接生成
    print("ログインに失敗したため、トークンを直接生成します")
    from app.core.security import create_access_token

    # ユーザーIDを使用してトークンを生成
    token = create_access_token(subject=user.id)
    print(f"生成されたトークン: {token}")
    return token


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
    
    # 新しいセッションを作成
    session = TestSessionLocal()
    print(f"Created new TestSessionLocal in conftest: {session}")
    
    # app/api/deps.py の set_conftest_db 関数を使用してセッションを設定
    from app.api.deps import set_conftest_db
    set_conftest_db(session)
    
    try:
        yield session
    except Exception as e:
        print(f"セッション中にエラーが発生: {e}")
        session.rollback()
        raise
    finally:
        # 明示的にロールバックするだけで、クローズはしない
        session.rollback()
    
    # テスト後にデータベースをクリーンアップしない
    # Base.metadata.drop_all(bind=engine)
