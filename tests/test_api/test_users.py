"""
ユーザー関連APIのテスト
"""
import pytest
from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from app.models.user import User
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def test_update_user_me(client: TestClient, db: Session, auth_token):
    """
    ユーザープロフィール更新APIのテスト (USR-002)
    """
    # テスト用のユーザーを取得
    user = db.query(User).filter(User.email == "test_auth@example.com").first()
    assert user is not None
    
    # 更新データ
    update_data = {
        "username": f"{user.username}_updated",
        "profile_image": "https://example.com/profile.jpg"
    }
    
    # APIリクエスト
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.put(f"{settings.API_V1_STR}/users/me", json=update_data, headers=headers)
    
    # レスポンスの検証
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == update_data["username"]
    assert data["profile_image"] == update_data["profile_image"]
    
    # データベースが更新されたことを確認
    updated_user = db.query(User).filter(User.id == user.id).first()
    assert updated_user.username == update_data["username"]
    assert updated_user.profile_image == update_data["profile_image"]


def test_update_user_password(client: TestClient, db: Session, auth_token):
    """
    ユーザーパスワード変更APIのテスト (USR-003)
    """
    # テスト用のユーザーを取得
    user = db.query(User).filter(User.email == "test_auth@example.com").first()
    assert user is not None
    
    # パスワード変更データ
    password_data = {
        "current_password": "password123",
        "new_password": "newpassword123"
    }
    
    # APIリクエスト
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.put(f"{settings.API_V1_STR}/users/password", json=password_data, headers=headers)
    
    # レスポンスの検証
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    
    # データベースが更新されたことを確認
    updated_user = db.query(User).filter(User.id == user.id).first()
    assert verify_password(password_data["new_password"], updated_user.password_hash)


def test_update_user_password_wrong_current(client: TestClient, db: Session, auth_token):
    """
    間違った現在のパスワードでのパスワード変更失敗テスト
    """
    # パスワード変更データ（間違った現在のパスワード）
    password_data = {
        "current_password": "wrongpassword",
        "new_password": "newpassword123"
    }
    
    # APIリクエスト
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.put(f"{settings.API_V1_STR}/users/password", json=password_data, headers=headers)
    
    # レスポンスの検証（エラーになることを確認）
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data


def test_delete_user_me(client: TestClient, db: Session):
    """
    ユーザーアカウント削除APIのテスト (USR-004)
    """
    # 削除用のテストユーザーを作成
    test_user = User(
        username="delete_test_me",
        email="delete_test_me@example.com",
        password_hash=get_password_hash("password123"),
        role="user",
        status="active",
        email_verified=True
    )
    db.add(test_user)
    db.commit()
    db.refresh(test_user)
    
    # ログインしてトークンを取得
    login_data = {
        "username": "delete_test_me@example.com",
        "password": "password123"
    }
    login_response = client.post(f"{settings.API_V1_STR}/auth/login", data=login_data)
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    
    # 削除リクエスト
    headers = {"Authorization": f"Bearer {token}"}
    delete_data = {
        "password": "password123"
    }
    response = client.delete(f"{settings.API_V1_STR}/users/me", json=delete_data, headers=headers)
    
    # レスポンスの検証
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    
    # データベースから削除されたことを確認
    deleted_user = db.query(User).filter(User.id == test_user.id).first()
    assert deleted_user is None


def test_delete_user_me_wrong_password(client: TestClient, db: Session, auth_token):
    """
    間違ったパスワードでのアカウント削除失敗テスト
    """
    # 削除リクエスト（間違ったパスワード）
    headers = {"Authorization": f"Bearer {auth_token}"}
    delete_data = {
        "password": "wrongpassword"
    }
    response = client.delete(f"{settings.API_V1_STR}/users/me", json=delete_data, headers=headers)
    
    # レスポンスの検証（エラーになることを確認）
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data