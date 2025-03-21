"""
ユーザーAPIのテスト
"""
import pytest
from app.models.user import User
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def test_get_users(client: TestClient, db: Session):
    """
    ユーザー一覧取得APIのテスト
    """
    # APIリクエスト
    response = client.get("/api/v1/users/")
    
    # レスポンスの検証
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert isinstance(data["items"], list)
    assert len(data["items"]) > 0
    
    # 最初のユーザーの構造を検証
    user = data["items"][0]
    assert "id" in user
    assert "username" in user
    assert "email" in user
    assert "role" in user


def test_get_user_by_id(client: TestClient, db: Session):
    """
    ユーザー詳細取得APIのテスト
    """
    # テスト用のユーザーを取得
    user = db.query(User).filter(User.role == "user").first()
    assert user is not None
    
    # APIリクエスト
    response = client.get(f"/api/v1/users/{user.id}")
    
    # レスポンスの検証
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user.id
    assert data["username"] == user.username
    assert data["email"] == user.email
    assert data["role"] == user.role


def test_get_user_not_found(client: TestClient):
    """
    存在しないユーザーの取得テスト
    """
    # 存在しないIDでAPIリクエスト
    response = client.get("/api/v1/users/00000000-0000-0000-0000-000000000000")
    
    # レスポンスの検証
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_create_user(client: TestClient, db: Session):
    """
    ユーザー作成APIのテスト
    """
    # 作成するユーザーデータ
    user_data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpassword",
        "role": "user"
    }
    
    # APIリクエスト
    response = client.post("/api/v1/users/", json=user_data)
    
    # レスポンスの検証
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert data["role"] == user_data["role"]
    assert "id" in data
    
    # データベースに保存されたことを確認
    created_user = db.query(User).filter(User.email == user_data["email"]).first()
    assert created_user is not None
    assert created_user.username == user_data["username"]
    assert created_user.email == user_data["email"]
    assert created_user.role == user_data["role"]


def test_update_user(client: TestClient, db: Session):
    """
    ユーザー更新APIのテスト
    """
    # テスト用のユーザーを取得
    user = db.query(User).filter(User.role == "user").first()
    assert user is not None
    
    # 更新データ
    update_data = {
        "username": f"{user.username}_updated",
        "email": user.email,  # メールアドレスは変更しない
    }
    
    # APIリクエスト
    response = client.put(f"/api/v1/users/{user.id}", json=update_data)
    
    # レスポンスの検証
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user.id
    assert data["username"] == update_data["username"]
    assert data["email"] == update_data["email"]
    
    # データベースが更新されたことを確認
    updated_user = db.query(User).filter(User.id == user.id).first()
    assert updated_user.username == update_data["username"]


def test_delete_user(client: TestClient, db: Session):
    """
    ユーザー削除APIのテスト
    """
    # 削除用のテストユーザーを作成
    test_user = User(
        username="delete_test",
        email="delete_test@example.com",
        password_hash="hashed_password",
        role="user",
        status="active",
        email_verified=True
    )
    db.add(test_user)
    db.commit()
    db.refresh(test_user)
    
    # APIリクエスト
    response = client.delete(f"/api/v1/users/{test_user.id}")
    
    # レスポンスの検証
    assert response.status_code == 200
    
    # データベースから削除されたことを確認
    deleted_user = db.query(User).filter(User.id == test_user.id).first()
    assert deleted_user is None