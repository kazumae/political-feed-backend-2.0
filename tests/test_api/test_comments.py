from datetime import datetime, timedelta

import pytest
from app.core.config import settings
from app.core.security import create_access_token, get_password_hash
from app.models.comment import Comment
from app.models.party import Party
from app.models.politician import Politician
from app.models.statement import Statement
from app.models.user import User
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


@pytest.fixture
def test_party(db: Session):
    """
    テスト用の政党を作成するフィクスチャ
    """
    party = Party(
        name="コメントテスト政党",
        short_name="コメテス",
        status="active",
        description="コメントテスト用の政党です"
    )
    db.add(party)
    db.commit()
    db.refresh(party)
    return party


@pytest.fixture
def test_politician(db: Session, test_party):
    """
    テスト用の政治家を作成するフィクスチャ
    """
    politician = Politician(
        name="コメント太郎",
        name_kana="コメントタロウ",
        current_party_id=test_party.id,
        role="代表",
        status="active",
        profile_summary="コメントテスト用の政治家プロフィールです"
    )
    db.add(politician)
    db.commit()
    db.refresh(politician)
    return politician


@pytest.fixture
def test_statement(db: Session, test_politician):
    """
    テスト用の発言を作成するフィクスチャ
    """
    statement = Statement(
        politician_id=test_politician.id,
        title="コメントテスト発言",
        content="これはコメントテスト用の発言内容です。",
        source="テスト会見",
        statement_date=datetime.utcnow() - timedelta(days=1),
        status="published",
        importance=80
    )
    db.add(statement)
    db.commit()
    db.refresh(statement)
    return statement


@pytest.fixture
def test_users(db: Session):
    """
    テスト用のユーザーを複数作成するフィクスチャ
    """
    users = [
        User(
            email="commentuser1@example.com",
            username="commentuser1",
            password_hash=get_password_hash("password123"),
            role="user",
            status="active",
            email_verified=True
        ),
        User(
            email="commentuser2@example.com",
            username="commentuser2",
            password_hash=get_password_hash("password123"),
            role="user",
            status="active",
            email_verified=True
        )
    ]
    
    for user in users:
        db.add(user)
    
    db.commit()
    
    # トークンを作成
    tokens = []
    for user in users:
        db.refresh(user)
        token = create_access_token(data={"sub": user.id})
        tokens.append({"user": user, "token": token})
    
    return tokens


@pytest.fixture
def test_comment(db: Session, test_statement, test_users):
    """
    テスト用のコメントを作成するフィクスチャ
    """
    comment = Comment(
        user_id=test_users[0]["user"].id,
        statement_id=test_statement.id,
        content="これはテスト用のコメントです。",
        status="published"
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def test_get_statement_comments(client: TestClient, test_statement, test_comment):
    """
    発言に対するコメント一覧取得のテスト
    """
    response = client.get(
        f"{settings.API_V1_STR}/statements/{test_statement.id}/comments"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    
    # テストコメントが含まれているか確認
    comment_ids = [c["id"] for c in data]
    assert test_comment.id in comment_ids


def test_create_comment(client: TestClient, test_statement, test_users):
    """
    コメント作成のテスト
    """
    headers = {"Authorization": f"Bearer {test_users[0]['token']}"}
    comment_data = {
        "content": "これは新しいテストコメントです。"
    }
    
    response = client.post(
        f"{settings.API_V1_STR}/statements/{test_statement.id}/comments",
        headers=headers,
        json=comment_data
    )
    
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["content"] == comment_data["content"]
    assert data["user_id"] == test_users[0]["user"].id
    assert data["statement_id"] == test_statement.id


def test_create_comment_unauthorized(client: TestClient, test_statement):
    """
    未認証ユーザーによるコメント作成失敗テスト
    """
    comment_data = {
        "content": "これは認証なしのコメントです。"
    }
    
    response = client.post(
        f"{settings.API_V1_STR}/statements/{test_statement.id}/comments",
        json=comment_data
    )
    
    assert response.status_code == 401


def test_update_comment(client: TestClient, test_comment, test_users):
    """
    コメント更新のテスト
    """
    headers = {"Authorization": f"Bearer {test_users[0]['token']}"}
    update_data = {
        "content": "これは更新されたコメントです。"
    }
    
    response = client.put(
        f"{settings.API_V1_STR}/comments/{test_comment.id}",
        headers=headers,
        json=update_data
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_comment.id
    assert data["content"] == update_data["content"]


def test_update_comment_unauthorized(client: TestClient, test_comment):
    """
    未認証ユーザーによるコメント更新失敗テスト
    """
    update_data = {
        "content": "これは認証なしの更新です。"
    }
    
    response = client.put(
        f"{settings.API_V1_STR}/comments/{test_comment.id}",
        json=update_data
    )
    
    assert response.status_code == 401


def test_update_comment_wrong_user(client: TestClient, test_comment, test_users):
    """
    他ユーザーのコメント更新失敗テスト
    """
    # 別のユーザーのトークンを使用
    headers = {"Authorization": f"Bearer {test_users[1]['token']}"}
    update_data = {
        "content": "これは他人のコメントを更新しようとしています。"
    }
    
    response = client.put(
        f"{settings.API_V1_STR}/comments/{test_comment.id}",
        headers=headers,
        json=update_data
    )
    
    assert response.status_code == 403


def test_delete_comment(client: TestClient, test_comment, test_users):
    """
    コメント削除のテスト
    """
    headers = {"Authorization": f"Bearer {test_users[0]['token']}"}
    
    response = client.delete(
        f"{settings.API_V1_STR}/comments/{test_comment.id}",
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "success" in data and data["success"] is True
    
    # 削除されたことを確認
    response = client.get(
        f"{settings.API_V1_STR}/comments/{test_comment.id}"
    )
    assert response.status_code == 404


def test_delete_comment_unauthorized(client: TestClient, test_comment):
    """
    未認証ユーザーによるコメント削除失敗テスト
    """
    response = client.delete(
        f"{settings.API_V1_STR}/comments/{test_comment.id}"
    )
    
    assert response.status_code == 401


def test_delete_comment_wrong_user(client: TestClient, test_comment, test_users):
    """
    他ユーザーのコメント削除失敗テスト
    """
    # 別のユーザーのトークンを使用
    headers = {"Authorization": f"Bearer {test_users[1]['token']}"}
    
    response = client.delete(
        f"{settings.API_V1_STR}/comments/{test_comment.id}",
        headers=headers
    )
    
    assert response.status_code == 403


def test_create_reply_comment(client: TestClient, test_comment, test_statement, test_users):
    """
    返信コメント作成のテスト
    """
    headers = {"Authorization": f"Bearer {test_users[1]['token']}"}
    reply_data = {
        "content": "これは返信コメントです。",
        "parent_id": test_comment.id
    }
    
    response = client.post(
        f"{settings.API_V1_STR}/statements/{test_statement.id}/comments",
        headers=headers,
        json=reply_data
    )
    
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["content"] == reply_data["content"]
    assert data["parent_id"] == test_comment.id
    assert data["user_id"] == test_users[1]["user"].id


def test_get_comment_replies(client: TestClient, test_comment, test_statement, test_users):
    """
    コメント返信一覧取得のテスト
    """
    # 返信コメントを作成
    headers = {"Authorization": f"Bearer {test_users[1]['token']}"}
    reply_data = {
        "content": "これは返信一覧テスト用のコメントです。",
        "parent_id": test_comment.id
    }
    
    client.post(
        f"{settings.API_V1_STR}/statements/{test_statement.id}/comments",
        headers=headers,
        json=reply_data
    )
    
    # 返信一覧を取得
    response = client.get(
        f"{settings.API_V1_STR}/comments/{test_comment.id}/replies"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    
    # 返信コメントの内容を確認
    assert any(c["content"] == reply_data["content"] for c in data)