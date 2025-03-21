"""
政治家APIのテスト
"""
import pytest
from app.core.config import settings
from app.core.security import get_password_hash
from app.models.politician import Politician
from app.models.user import User
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def get_auth_token(client: TestClient, db: Session) -> str:
    """テスト用の認証トークンを取得する"""
    # テストユーザーの作成
    user = User(
        email="test_api@example.com",
        username="test_api_user",
        password_hash=get_password_hash("password123"),
        role="user",
        status="active",
        email_verified=True
    )
    db.add(user)
    db.commit()
    
    # ログインリクエスト
    login_data = {
        "username": "test_api@example.com",
        "password": "password123"
    }
    response = client.post(f"{settings.API_V1_STR}/auth/login", data=login_data)
    
    # トークンを取得
    assert response.status_code == 200
    return response.json()["access_token"]


def test_get_politicians(client: TestClient, db: Session):
    """
    政治家一覧取得APIのテスト
    """
    # 認証トークンを取得
    token = get_auth_token(client, db)
    headers = {"Authorization": f"Bearer {token}"}
    
    # APIリクエスト
    response = client.get("/api/v1/politicians/", headers=headers)
    
    # レスポンスの検証
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert isinstance(data["items"], list)
    assert len(data["items"]) > 0
    
    # 最初の政治家の構造を検証
    politician = data["items"][0]
    assert "id" in politician
    assert "name" in politician
    assert "party" in politician
    assert "role" in politician


def test_get_politician_by_id(client: TestClient, db: Session):
    """
    政治家詳細取得APIのテスト
    """
    # 認証トークンを取得
    token = get_auth_token(client, db)
    headers = {"Authorization": f"Bearer {token}"}
    
    # テスト用の政治家を取得
    politician = db.query(Politician).first()
    assert politician is not None
    
    # APIリクエスト
    response = client.get(f"/api/v1/politicians/{politician.id}", headers=headers)
    
    # レスポンスの検証
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == politician.id
    assert data["name"] == politician.name
    assert "party" in data
    assert "statements" in data


def test_get_politician_not_found(client: TestClient, db: Session):
    """
    存在しない政治家の取得テスト
    """
    # 認証トークンを取得
    token = get_auth_token(client, db)
    headers = {"Authorization": f"Bearer {token}"}
    
    # 存在しないIDでAPIリクエスト
    response = client.get(
        "/api/v1/politicians/00000000-0000-0000-0000-000000000000",
        headers=headers
    )
    
    # レスポンスの検証
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_get_politician_statements(client: TestClient, db: Session):
    """
    政治家の発言一覧取得APIのテスト
    """
    # 認証トークンを取得
    token = get_auth_token(client, db)
    headers = {"Authorization": f"Bearer {token}"}
    
    # テスト用の政治家を取得
    politician = db.query(Politician).first()
    assert politician is not None
    
    # APIリクエスト
    response = client.get(
        f"/api/v1/politicians/{politician.id}/statements",
        headers=headers
    )
    
    # レスポンスの検証
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert isinstance(data["items"], list)
    
    # 発言がある場合は内容を検証
    if len(data["items"]) > 0:
        statement = data["items"][0]
        assert "id" in statement
        assert "content" in statement
        assert "statement_date" in statement
        assert statement["politician_id"] == politician.id


def test_search_politicians(client: TestClient, db: Session):
    """
    政治家検索APIのテスト
    """
    # 認証トークンを取得
    token = get_auth_token(client, db)
    headers = {"Authorization": f"Bearer {token}"}
    
    # 検索クエリ
    search_query = "山田"  # テストデータに含まれる名前の一部
    
    # APIリクエスト
    response = client.get(
        f"/api/v1/politicians/search?q={search_query}",
        headers=headers
    )
    
    # レスポンスの検証
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert isinstance(data["items"], list)
    
    # 検索結果がある場合は内容を検証
    if len(data["items"]) > 0:
        for politician in data["items"]:
            assert search_query in politician["name"]


def test_filter_politicians_by_party(client: TestClient, db: Session):
    """
    政党による政治家フィルタリングのテスト
    """
    # 認証トークンを取得
    token = get_auth_token(client, db)
    headers = {"Authorization": f"Bearer {token}"}
    
    # テスト用の政治家を取得して、その政党IDを使用
    politician = db.query(Politician).first()
    assert politician is not None
    assert politician.current_party_id is not None
    
    # APIリクエスト
    response = client.get(
        f"/api/v1/politicians/?party_id={politician.current_party_id}",
        headers=headers
    )
    
    # レスポンスの検証
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert isinstance(data["items"], list)
    assert len(data["items"]) > 0
    
    # すべての政治家が指定した政党に所属していることを確認
    for item in data["items"]:
        assert item["party"]["id"] == politician.current_party_id