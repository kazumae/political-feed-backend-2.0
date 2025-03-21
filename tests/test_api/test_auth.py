import pytest
from app.core.config import settings
from app.core.security import get_password_hash
from app.models.user import User
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def test_login_success(client: TestClient, db: Session):
    """
    正常なログインのテスト
    """
    # 既存のユーザーを検索
    user = db.query(User).filter(User.email == "test@example.com").first()
    
    # ユーザーが存在しない場合は作成
    if not user:
        user = User(
            email="test@example.com",
            username="testuser",
            password_hash=get_password_hash("password123"),
            role="user",
            status="active",
            email_verified=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    # 既存のユーザーが存在する場合はアクティブに更新
    else:
        user.status = "active"
        db.commit()
        db.refresh(user)
    
    # ログインリクエストの前に、データベースの状態を確認
    print(f"User in database: {db.query(User).filter(User.email == 'test@example.com').first()}")
    
    # 認証サービスを直接呼び出してテスト
    from app.services.user import authenticate_user
    authenticated_user = authenticate_user(db, email="test@example.com", password="password123")
    print(f"Authenticated user: {authenticated_user}")
    
    # 認証が成功したことを確認
    assert authenticated_user is not None
    assert authenticated_user.email == "test@example.com"
    
    # ログインリクエスト
    # OAuth2PasswordRequestFormに合わせたフォームデータとして送信
    # FastAPIのOAuth2PasswordRequestFormはフォームデータを期待する
    login_data = {
        "username": "test@example.com",
        "password": "password123"
    }
    
    # フォームデータとして送信（application/x-www-form-urlencoded）
    # Content-Typeヘッダーを明示的に設定
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    # デバッグ用にレスポンスの詳細を出力
    print(f"Login response status: {response.status_code}")
    print(f"Login response body: {response.text}")
    
    # デバッグ出力を追加
    print(f"Login response headers: {response.headers}")
    print(f"Login response cookies: {response.cookies}")
    
    # 認証サービスは正常に動作しているが、APIリクエストが失敗する場合は
    # エラーの詳細を確認する
    if authenticated_user is not None and response.status_code != 200:
        print("認証サービスは正常に動作していますが、APIリクエストが失敗しています。")
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        # スキップせずにエラーを表示する
        # import pytest
        # pytest.skip("認証サービスは正常に動作していますが、APIリクエストが失敗しています。テスト環境の問題と判断し、テストをスキップします。")
    
    # レスポンスの検証
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client: TestClient, db: Session):
    """
    無効な認証情報でのログイン失敗テスト
    """
    # 既存のユーザーを検索
    user = db.query(User).filter(User.email == "test2@example.com").first()
    
    # ユーザーが存在しない場合は作成
    if not user:
        user = User(
            email="test2@example.com",
            username="testuser2",
            password_hash=get_password_hash("password123"),
            role="user",
            status="active",
            email_verified=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    # 既存のユーザーが存在する場合はアクティブに更新
    else:
        user.status = "active"
        db.commit()
        db.refresh(user)
    
    # 間違ったパスワードでログイン
    login_data = {
        "username": "test2@example.com",
        "password": "wrongpassword"
    }
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data=login_data
    )
    
    # レスポンスの検証
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data


def test_login_inactive_user(client: TestClient, db: Session):
    """
    非アクティブユーザーのログイン失敗テスト
    """
    # 既存のユーザーを検索
    user = db.query(User).filter(User.email == "inactive@example.com").first()
    
    # ユーザーが存在しない場合は作成
    if not user:
        user = User(
            email="inactive@example.com",
            username="inactiveuser",
            password_hash=get_password_hash("password123"),
            role="user",
            status="inactive",
            email_verified=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    # 既存のユーザーが存在する場合は非アクティブに更新
    else:
        user.status = "inactive"
        db.commit()
        db.refresh(user)
    
    # ログインリクエスト
    login_data = {
        "username": "inactive@example.com",
        "password": "password123"
    }
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data=login_data
    )
    
    # レスポンスの検証
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data


def test_get_current_user(client: TestClient, db: Session):
    """
    現在のユーザー情報取得テスト
    """
    # 既存のユーザーを検索
    user = db.query(User).filter(User.email == "current@example.com").first()
    
    # ユーザーが存在しない場合は作成
    if not user:
        user = User(
            email="current@example.com",
            username="currentuser",
            password_hash=get_password_hash("password123"),
            role="user",
            status="active",
            email_verified=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    # 既存のユーザーが存在する場合はアクティブに更新
    else:
        user.status = "active"
        db.commit()
        db.refresh(user)
    
    # ログインしてトークンを取得
    login_data = {
        "username": "current@example.com",
        "password": "password123"
    }
    login_response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data=login_data
    )
    
    # レスポンスの検証
    assert login_response.status_code == 200
    login_data = login_response.json()
    assert "access_token" in login_data
    token = login_data["access_token"]
    
    # 現在のユーザー情報を取得
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get(
        f"{settings.API_V1_STR}/users/me",
        headers=headers
    )
    
    # レスポンスの検証
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "current@example.com"
    assert data["username"] == "currentuser"
    assert "password" not in data