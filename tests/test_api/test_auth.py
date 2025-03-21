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
    # データベースをクリア
    db.query(User).delete()
    db.commit()
    
    # テストユーザーの作成
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
    
    # ログインリクエスト
    login_data = {
        "username": "test@example.com",
        "password": "password123"
    }
    response = client.post(f"{settings.API_V1_STR}/auth/login", data=login_data)
    
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
    # データベースをクリア
    db.query(User).delete()
    db.commit()
    
    # テストユーザーの作成
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
    # データベースをクリア
    db.query(User).delete()
    db.commit()
    
    # 非アクティブなテストユーザーの作成
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
    # データベースをクリア
    db.query(User).delete()
    db.commit()
    
    # テストユーザーの作成
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