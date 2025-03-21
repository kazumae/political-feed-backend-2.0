from datetime import datetime, timedelta

import pytest
from app.core.config import settings
from app.core.security import create_access_token, get_password_hash
from app.models.party import Party
from app.models.politician import Politician
from app.models.statement import Statement, StatementTopic
from app.models.topic import Topic
from app.models.user import User
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


@pytest.fixture
def test_party(db: Session):
    """
    テスト用の政党を作成するフィクスチャ
    """
    party = Party(
        name="テスト政党",
        short_name="テスト",
        status="active",
        description="テスト用の政党です"
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
        name="テスト太郎",
        name_kana="テストタロウ",
        current_party_id=test_party.id,
        role="代表",
        status="active",
        profile_summary="テスト用の政治家プロフィールです"
    )
    db.add(politician)
    db.commit()
    db.refresh(politician)
    return politician


@pytest.fixture
def test_topic(db: Session):
    """
    テスト用のトピックを作成するフィクスチャ
    """
    topic = Topic(
        name="テストトピック",
        slug="test-topic",
        category="economy",
        status="active",
        description="テスト用のトピックです"
    )
    db.add(topic)
    db.commit()
    db.refresh(topic)
    return topic


@pytest.fixture
def test_statement(db: Session, test_politician, test_topic):
    """
    テスト用の発言を作成するフィクスチャ
    """
    statement = Statement(
        politician_id=test_politician.id,
        title="テスト発言",
        content="これはテスト用の発言内容です。",
        source="テスト会見",
        statement_date=datetime.utcnow() - timedelta(days=1),
        status="published",
        importance=80
    )
    db.add(statement)
    db.commit()
    
    # 発言とトピックの関連付け
    statement_topic = StatementTopic(
        statement_id=statement.id,
        topic_id=test_topic.id,
        relevance=75
    )
    db.add(statement_topic)
    db.commit()
    
    db.refresh(statement)
    return statement


@pytest.fixture
def test_user_token(db: Session):
    """
    テスト用のユーザーとトークンを作成するフィクスチャ
    """
    user = User(
        email="testuser@example.com",
        username="testuser",
        password_hash=get_password_hash("password123"),
        role="user",
        status="active",
        email_verified=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # アクセストークンの作成
    access_token = create_access_token(
        data={"sub": user.id}
    )
    
    return {"user": user, "token": access_token}


def test_get_statements(client: TestClient, test_statement):
    """
    発言一覧取得のテスト
    """
    response = client.get(f"{settings.API_V1_STR}/statements/")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    
    # テスト用発言が含まれているか確認
    statement_ids = [s["id"] for s in data]
    assert test_statement.id in statement_ids


def test_get_statement_by_id(client: TestClient, test_statement):
    """
    発言詳細取得のテスト
    """
    response = client.get(f"{settings.API_V1_STR}/statements/{test_statement.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_statement.id
    assert data["title"] == test_statement.title
    assert data["content"] == test_statement.content
    assert "politician" in data
    assert "topics" in data
    assert len(data["topics"]) >= 1


def test_get_statement_not_found(client: TestClient):
    """
    存在しない発言IDでの取得失敗テスト
    """
    non_existent_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"{settings.API_V1_STR}/statements/{non_existent_id}")
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_filter_statements_by_politician(client: TestClient, test_statement, test_politician):
    """
    政治家IDによる発言フィルタリングのテスト
    """
    response = client.get(
        f"{settings.API_V1_STR}/statements/",
        params={"politician_id": test_politician.id}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    
    # すべての発言が指定した政治家のものであることを確認
    for statement in data:
        assert statement["politician"]["id"] == test_politician.id


def test_filter_statements_by_topic(client: TestClient, test_statement, test_topic):
    """
    トピックIDによる発言フィルタリングのテスト
    """
    response = client.get(
        f"{settings.API_V1_STR}/statements/",
        params={"topic_id": test_topic.id}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    
    # テスト用発言が含まれているか確認
    statement_ids = [s["id"] for s in data]
    assert test_statement.id in statement_ids


def test_search_statements(client: TestClient, test_statement):
    """
    発言検索のテスト
    """
    # 発言内容の一部で検索
    search_term = test_statement.content[:10]  # 内容の最初の10文字
    response = client.get(
        f"{settings.API_V1_STR}/statements/",
        params={"search": search_term}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    
    # 検索結果にテスト用発言が含まれているか確認
    statement_ids = [s["id"] for s in data]
    assert test_statement.id in statement_ids


def test_like_statement(client: TestClient, test_statement, test_user_token):
    """
    発言へのいいね追加テスト
    """
    headers = {"Authorization": f"Bearer {test_user_token['token']}"}
    response = client.post(
        f"{settings.API_V1_STR}/statements/{test_statement.id}/like",
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "success" in data and data["success"] is True
    
    # いいねが追加されたか確認
    response = client.get(f"{settings.API_V1_STR}/statements/{test_statement.id}")
    statement_data = response.json()
    assert statement_data["likes_count"] >= 1


def test_unlike_statement(client: TestClient, test_statement, test_user_token):
    """
    発言へのいいね解除テスト
    """
    headers = {"Authorization": f"Bearer {test_user_token['token']}"}
    
    # まずいいねを追加
    client.post(
        f"{settings.API_V1_STR}/statements/{test_statement.id}/like",
        headers=headers
    )
    
    # いいねを解除
    response = client.delete(
        f"{settings.API_V1_STR}/statements/{test_statement.id}/like",
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "success" in data and data["success"] is True