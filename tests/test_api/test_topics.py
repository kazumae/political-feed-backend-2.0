import pytest
from app.core.config import settings
from app.core.security import create_access_token, get_password_hash
from app.models.topic import Topic, TopicRelation
from app.models.user import User
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


@pytest.fixture
def test_topics(db: Session):
    """
    テスト用のトピックを複数作成するフィクスチャ
    """
    topics = [
        Topic(
            name="経済政策",
            slug="economy-policy",
            category="economy",
            status="active",
            description="経済に関する政策トピック",
            importance=90
        ),
        Topic(
            name="外交安全保障",
            slug="foreign-security",
            category="foreign_policy",
            status="active",
            description="外交と安全保障に関するトピック",
            importance=85
        ),
        Topic(
            name="社会保障",
            slug="social-welfare",
            category="social_welfare",
            status="active",
            description="社会保障に関するトピック",
            importance=80
        )
    ]
    
    for topic in topics:
        db.add(topic)
    
    db.commit()
    
    # トピック間の関連を作成
    topic_relation = TopicRelation(
        parent_topic_id=topics[0].id,
        child_topic_id=topics[2].id,
        relation_type="related",
        strength=70
    )
    db.add(topic_relation)
    db.commit()
    
    return topics


@pytest.fixture
def test_user_token(db: Session):
    """
    テスト用のユーザーとトークンを作成するフィクスチャ
    """
    user = User(
        email="topicuser@example.com",
        username="topicuser",
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


def test_get_topics(client: TestClient, test_topics):
    """
    トピック一覧取得のテスト
    """
    response = client.get(f"{settings.API_V1_STR}/topics/")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= len(test_topics)
    
    # テスト用トピックが含まれているか確認
    topic_names = [t["name"] for t in data]
    for topic in test_topics:
        assert topic.name in topic_names


def test_get_topic_by_id(client: TestClient, test_topics):
    """
    トピック詳細取得のテスト
    """
    test_topic = test_topics[0]
    response = client.get(f"{settings.API_V1_STR}/topics/{test_topic.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_topic.id
    assert data["name"] == test_topic.name
    assert data["slug"] == test_topic.slug
    assert data["category"] == test_topic.category


def test_get_topic_not_found(client: TestClient):
    """
    存在しないトピックIDでの取得失敗テスト
    """
    non_existent_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"{settings.API_V1_STR}/topics/{non_existent_id}")
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_filter_topics_by_category(client: TestClient, test_topics):
    """
    カテゴリによるトピックフィルタリングのテスト
    """
    category = "economy"
    response = client.get(
        f"{settings.API_V1_STR}/topics/",
        params={"category": category}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    
    # すべてのトピックが指定したカテゴリであることを確認
    for topic in data:
        assert topic["category"] == category


def test_filter_topics_by_status(client: TestClient, test_topics):
    """
    ステータスによるトピックフィルタリングのテスト
    """
    status = "active"
    response = client.get(
        f"{settings.API_V1_STR}/topics/",
        params={"status": status}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= len(test_topics)
    
    # すべてのトピックがアクティブステータスであることを確認
    for topic in data:
        assert topic["status"] == status


def test_search_topics(client: TestClient, test_topics):
    """
    トピック検索のテスト
    """
    # 名前の一部で検索
    search_term = "経済"
    response = client.get(
        f"{settings.API_V1_STR}/topics/",
        params={"search": search_term}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    
    # 検索結果に該当するトピックが含まれているか確認
    found = False
    for topic in data:
        if search_term in topic["name"]:
            found = True
            break
    assert found


def test_get_topic_relations(client: TestClient, test_topics):
    """
    トピック関連の取得テスト
    """
    test_topic = test_topics[0]
    response = client.get(f"{settings.API_V1_STR}/topics/{test_topic.id}/relations")
    
    assert response.status_code == 200
    data = response.json()
    assert "related_topics" in data
    assert isinstance(data["related_topics"], list)
    assert len(data["related_topics"]) >= 1


def test_follow_topic(client: TestClient, test_topics, test_user_token):
    """
    トピックフォローのテスト
    """
    test_topic = test_topics[0]
    headers = {"Authorization": f"Bearer {test_user_token['token']}"}
    
    response = client.post(
        f"{settings.API_V1_STR}/topics/{test_topic.id}/follow",
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "success" in data and data["success"] is True


def test_unfollow_topic(client: TestClient, test_topics, test_user_token):
    """
    トピックフォロー解除のテスト
    """
    test_topic = test_topics[0]
    headers = {"Authorization": f"Bearer {test_user_token['token']}"}
    
    # まずフォローする
    client.post(
        f"{settings.API_V1_STR}/topics/{test_topic.id}/follow",
        headers=headers
    )
    
    # フォロー解除
    response = client.delete(
        f"{settings.API_V1_STR}/topics/{test_topic.id}/follow",
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "success" in data and data["success"] is True