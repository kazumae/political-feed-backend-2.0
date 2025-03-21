"""
ユーザー関連APIのテスト
"""
# pytest is used by the test runner
import pytest  # noqa: F401
from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from app.models.user import User
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def test_update_user_me(client: TestClient, db: Session):
    """
    ユーザープロフィール更新APIのテスト (USR-001)
    """
    # セッションをリフレッシュ
    db.rollback()
    
    # 新しいユーザーを作成
    import uuid
    test_email = f"test_update_me_{uuid.uuid4().hex[:8]}@example.com"
    test_username = f"test_update_me_{uuid.uuid4().hex[:8]}"
    
    user = User(
        email=test_email,
        username=test_username,
        password_hash=get_password_hash("password123"),
        role="user",
        status="active",
        email_verified=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    print(f"テスト用ユーザー: {user.id}, {user.email}, {user.username}")
    
    # 更新データ（ユニークな名前を生成）
    import uuid
    unique_suffix = str(uuid.uuid4())[:8]
    update_data = {
        "username": f"updated_user_{unique_suffix}",
        "profile_image": "https://example.com/profile.jpg"
    }
    
    # ユーザー用のトークンを生成
    from app.core.security import create_access_token
    token = create_access_token(subject=user.id)
    print(f"生成されたトークン: {token}")
    
    # APIリクエスト
    headers = {"Authorization": f"Bearer {token}"}
    response = client.put(
        f"{settings.API_V1_STR}/users/me",
        json=update_data,
        headers=headers
    )
    
    # レスポンスの検証
    print(f"更新レスポンス: {response.status_code}")
    print(f"レスポンス内容: {response.text}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == update_data["username"]
    assert data["profile_image"] == update_data["profile_image"]
    
    # データベースが更新されたことを確認
    # db.refresh(user)だけでは更新が反映されないため、再取得する
    updated_user = db.query(User).filter(User.id == user.id).first()
    print(f"更新後のユーザー: {updated_user.id}, {updated_user.email}, {updated_user.username}")
    assert updated_user.username == update_data["username"]
    assert updated_user.profile_image == update_data["profile_image"]


def test_update_user_password(client: TestClient, db: Session):
    """
    ユーザーパスワード変更APIのテスト (USR-002)
    """
    # セッションをリフレッシュ
    db.rollback()
    
    # 新しいユーザーを作成
    import uuid
    test_email = f"test_update_pwd_{uuid.uuid4().hex[:8]}@example.com"
    test_username = f"test_update_pwd_{uuid.uuid4().hex[:8]}"
    
    user = User(
        email=test_email,
        username=test_username,
        password_hash=get_password_hash("password123"),
        role="user",
        status="active",
        email_verified=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    print(f"テスト用ユーザー: {user.id}, {user.email}, {user.username}")
    
    # 現在のパスワードハッシュを保存
    original_password_hash = user.password_hash
    
    # パスワード変更データ
    password_data = {
        "current_password": "password123",
        "new_password": "newpassword123"
    }
    
    # ユーザー用のトークンを生成
    from app.core.security import create_access_token
    token = create_access_token(subject=user.id)
    print(f"生成されたトークン: {token}")
    
    # APIリクエスト
    headers = {"Authorization": f"Bearer {token}"}
    response = client.put(
        f"{settings.API_V1_STR}/users/password",
        json=password_data,
        headers=headers
    )
    
    # レスポンスの検証
    print(f"パスワード変更レスポンス: {response.status_code}")
    print(f"レスポンス内容: {response.text}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    
    # データベースが更新されたことを確認
    # db.refresh(user)だけでは更新が反映されないため、再取得する
    updated_user = db.query(User).filter(User.id == user.id).first()
    print(f"更新後のユーザー: {updated_user.id}, {updated_user.email}, {updated_user.username}")
    assert updated_user.password_hash != original_password_hash
    assert verify_password(
        password_data["new_password"],
        updated_user.password_hash
    )
    
    # パスワードを元に戻す（他のテストに影響しないように）
    user.password_hash = get_password_hash("password123")
    db.add(user)
    db.commit()


def test_update_user_password_wrong_current(
    client: TestClient, db: Session
):
    """
    間違った現在のパスワードでのパスワード変更失敗テスト (USR-003)
    """
    # セッションをリフレッシュ
    db.rollback()
    
    # 新しいユーザーを作成
    import uuid
    test_email = f"test_wrong_pwd_{uuid.uuid4().hex[:8]}@example.com"
    test_username = f"test_wrong_pwd_{uuid.uuid4().hex[:8]}"
    
    user = User(
        email=test_email,
        username=test_username,
        password_hash=get_password_hash("password123"),
        role="user",
        status="active",
        email_verified=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    print(f"テスト用ユーザー: {user.id}, {user.email}, {user.username}")
    
    # 現在のパスワードハッシュを保存
    original_password_hash = user.password_hash
    
    # パスワード変更データ（間違った現在のパスワード）
    password_data = {
        "current_password": "wrongpassword",
        "new_password": "newpassword123"
    }
    
    # ユーザー用のトークンを生成
    from app.core.security import create_access_token
    token = create_access_token(subject=user.id)
    print(f"生成されたトークン: {token}")
    
    # APIリクエスト
    headers = {"Authorization": f"Bearer {token}"}
    response = client.put(
        f"{settings.API_V1_STR}/users/password",
        json=password_data,
        headers=headers
    )
    
    # レスポンスの検証（エラーになることを確認）
    print(f"パスワード変更失敗レスポンス: {response.status_code}")
    print(f"レスポンス内容: {response.text}")
    
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "現在のパスワードが正しくありません" in data["detail"]
    
    # データベースが更新されていないことを確認
    # db.refresh(user)だけでは更新が反映されないため、再取得する
    updated_user = db.query(User).filter(User.id == user.id).first()
    print(f"更新後のユーザー: {updated_user.id}, {updated_user.email}, {updated_user.username}")
    assert updated_user.password_hash == original_password_hash


def test_delete_user_me(client: TestClient, db: Session):
    """
    ユーザーアカウント削除APIのテスト (USR-004)
    """
    # セッションをリフレッシュ
    db.rollback()
    
    # テスト用のユーザーを作成（既存のユーザーを削除すると他のテストに影響するため）
    import uuid
    test_email = f"test_delete_{uuid.uuid4().hex[:8]}@example.com"
    test_username = f"test_delete_{uuid.uuid4().hex[:8]}"
    
    test_delete_user = User(
        email=test_email,
        username=test_username,
        password_hash=get_password_hash("password123"),
        role="user",
        status="active",
        email_verified=True
    )
    db.add(test_delete_user)
    db.commit()
    db.refresh(test_delete_user)
    user_id = test_delete_user.id
    user_email = test_delete_user.email
    print(f"削除テスト用ユーザー: {user_id}, {user_email}")
    
    # 削除用のトークンを取得
    login_data = {
        "username": test_email,
        "password": "password123"
    }
    login_response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data=login_data
    )
    assert login_response.status_code == 200
    delete_token = login_response.json()["access_token"]
    
    # 削除リクエスト
    headers = {"Authorization": f"Bearer {delete_token}"}
    delete_data = {
        "password": "password123"
    }
    response = client.delete(
        f"{settings.API_V1_STR}/users/me",
        json=delete_data,
        headers=headers
    )
    
    # レスポンスの検証
    print(f"削除レスポンス: {response.status_code}")
    print(f"レスポンス内容: {response.text}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    
    # データベースから削除されたことを確認
    # 削除されたユーザーを再取得
    deleted_user = db.query(User).filter(
        User.id == test_delete_user.id
    ).first()
    print(f"削除後のユーザー検索結果: {deleted_user}")
    assert deleted_user is None


def test_delete_user_me_wrong_password(
    client: TestClient, db: Session
):
    """
    間違ったパスワードでのアカウント削除失敗テスト (USR-005)
    """
    # セッションをリフレッシュ
    db.rollback()
    
    # テスト用のユーザーを作成
    import uuid
    test_email = f"test_wrong_del_{uuid.uuid4().hex[:8]}@example.com"
    test_username = f"test_wrong_del_{uuid.uuid4().hex[:8]}"
    
    test_wrong_delete_user = User(
        email=test_email,
        username=test_username,
        password_hash=get_password_hash("password123"),
        role="user",
        status="active",
        email_verified=True
    )
    db.add(test_wrong_delete_user)
    db.commit()
    db.refresh(test_wrong_delete_user)
    user_id = test_wrong_delete_user.id
    user_email = test_wrong_delete_user.email
    print(f"削除失敗テスト用ユーザー: {user_id}, {user_email}")
    
    # 削除用のトークンを取得
    login_data = {
        "username": test_email,
        "password": "password123"
    }
    login_response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data=login_data
    )
    assert login_response.status_code == 200
    wrong_delete_token = login_response.json()["access_token"]
    
    # 削除リクエスト（間違ったパスワード）
    headers = {"Authorization": f"Bearer {wrong_delete_token}"}
    delete_data = {
        "password": "wrongpassword"
    }
    response = client.delete(
        f"{settings.API_V1_STR}/users/me",
        json=delete_data,
        headers=headers
    )
    
    # レスポンスの検証（エラーになることを確認）
    print(f"削除失敗レスポンス: {response.status_code}")
    print(f"レスポンス内容: {response.text}")
    
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "パスワードが正しくありません" in data["detail"]
    
    # データベースから削除されていないことを確認
    # ユーザーを再取得
    not_deleted_user = db.query(User).filter(
        User.id == test_wrong_delete_user.id
    ).first()
    print(f"削除失敗後のユーザー検索結果: {not_deleted_user}")
    assert not_deleted_user is not None
    
    # テスト後にユーザーを削除（クリーンアップ）
    db.delete(not_deleted_user)
    db.commit()