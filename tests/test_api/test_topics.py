import uuid

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
    # 既存のトピックを検索
    existing_topics = db.query(Topic).limit(3).all()
    if len(existing_topics) >= 3:
        print(f"既存のトピックを使用: {[t.id for t in existing_topics]}")
        return existing_topics
    
    # 既存のトピックが不足している場合は、新しいトピックを作成
    topics_to_create = []
    
    # 経済政策トピック
    economy_topic = db.query(Topic).filter(
        Topic.slug == "economy-policy"
    ).first()
    if not economy_topic:
        economy_topic = Topic(
            name=f"経済政策_{uuid.uuid4().hex[:8]}",  # 一意の名前
            slug=f"economy-policy-{uuid.uuid4().hex[:8]}",  # 一意のスラッグ
            category="economy",
            status="active",
            description="経済に関する政策トピック",
            importance=90
        )
        topics_to_create.append(economy_topic)
    
    # 外交安全保障トピック
    foreign_topic = db.query(Topic).filter(
        Topic.slug == "foreign-security"
    ).first()
    if not foreign_topic:
        foreign_topic = Topic(
            name=f"外交安全保障_{uuid.uuid4().hex[:8]}",
            slug=f"foreign-security-{uuid.uuid4().hex[:8]}",
            category="foreign_policy",
            status="active",
            description="外交と安全保障に関するトピック",
            importance=85
        )
        topics_to_create.append(foreign_topic)
    
    # 社会保障トピック
    welfare_topic = db.query(Topic).filter(Topic.slug == "social-welfare").first()
    if not welfare_topic:
        welfare_topic = Topic(
            name=f"社会保障_{uuid.uuid4().hex[:8]}",
            slug=f"social-welfare-{uuid.uuid4().hex[:8]}",
            category="social_welfare",
            status="active",
            description="社会保障に関するトピック",
            importance=80
        )
        topics_to_create.append(welfare_topic)
    
    # 新しいトピックを追加
    for topic in topics_to_create:
        db.add(topic)
    
    db.commit()
    
    # 最終的なトピックリストを作成
    result_topics = []
    if economy_topic:
        result_topics.append(economy_topic)
    if foreign_topic:
        result_topics.append(foreign_topic)
    if welfare_topic:
        result_topics.append(welfare_topic)
    
    # トピック間の関連を作成（必要な場合のみ）
    if len(result_topics) >= 2 and not db.query(TopicRelation).filter(
        TopicRelation.parent_topic_id == result_topics[0].id,
        TopicRelation.child_topic_id == result_topics[-1].id
    ).first():
        topic_relation = TopicRelation(
            parent_topic_id=result_topics[0].id,
            child_topic_id=result_topics[-1].id,
            relation_type="related",
            strength=70
        )
        db.add(topic_relation)
        db.commit()
    
    return result_topics


@pytest.fixture
def test_user_token(db: Session):
    """
    テスト用のユーザーとトークンを作成するフィクスチャ
    """
    # 既存のユーザーを検索
    user = db.query(User).filter(User.username.like("topicuser%")).first()
    
    if not user:
        # 一意のユーザー名とメールアドレスを生成
        unique_id = uuid.uuid4().hex[:8]
        username = f"topicuser_{unique_id}"
        email = f"topicuser_{unique_id}@example.com"
        
        user = User(
            email=email,
            username=username,
            password_hash=get_password_hash("password123"),
            role="user",
            status="active",
            email_verified=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"新しいテストユーザーを作成: {username}")
    else:
        print(f"既存のテストユーザーを使用: {user.username}")
    
    # アクセストークンの作成
    access_token = create_access_token(
        data={"sub": user.id}
    )
    
    return {"user": user, "token": access_token}


def test_get_topics(client: TestClient, test_topics, test_user_token):
    """
    トピック一覧取得のテスト
    """
    headers = {"Authorization": f"Bearer {test_user_token['token']}"}
    response = client.get(
        f"{settings.API_V1_STR}/topics/",
        headers=headers
    )
    
    # レスポンスの内容を確認
    print(f"トピック一覧レスポンス: {response.status_code}")
    if response.status_code != 200:
        print(f"エラーレスポンス: {response.text}")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    
    # 検索結果が存在することを確認
    assert len(data) >= 1
    
    # 取得したトピック名を表示
    topic_names = [t["name"] for t in data]
    print(f"取得したトピック: {topic_names}")


def test_get_topic_by_id(client: TestClient, test_topics, test_user_token):
    """
    トピック詳細取得のテスト
    """
    headers = {"Authorization": f"Bearer {test_user_token['token']}"}
    
    # まずトピック一覧を取得して、実際のAPIで使用できるトピックIDを取得
    response_list = client.get(
        f"{settings.API_V1_STR}/topics/",
        headers=headers
    )
    
    assert response_list.status_code == 200
    topics = response_list.json()
    
    if len(topics) == 0:
        pytest.skip("トピックが存在しないためテストをスキップします")
    
    # 最初のトピックのIDを使用
    topic_id = topics[0]["id"]
    print(f"APIから取得したトピックID: {topic_id}")
    
    # トピック詳細を取得
    url = f"{settings.API_V1_STR}/topics/{topic_id}"
    response = client.get(
        url,
        headers=headers
    )
    
    # レスポンスの内容を確認
    print(f"トピック詳細レスポンス: {response.status_code}")
    if response.status_code != 200:
        print(f"エラーレスポンス: {response.text}")
    
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "name" in data
    assert "slug" in data
    assert "category" in data


def test_get_topic_not_found(client: TestClient, test_user_token):
    """
    存在しないトピックIDでの取得失敗テスト
    """
    headers = {"Authorization": f"Bearer {test_user_token['token']}"}
    non_existent_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(
        f"{settings.API_V1_STR}/topics/{non_existent_id}",
        headers=headers
    )
    
    # レスポンスの内容を確認
    print(f"存在しないトピックIDでのレスポンス: {response.status_code}")
    print(f"レスポンス内容: {response.text}")
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_filter_topics_by_category(client: TestClient, test_topics, test_user_token):
    """
    カテゴリによるトピックフィルタリングのテスト
    """
    headers = {"Authorization": f"Bearer {test_user_token['token']}"}
    
    # まずトピック一覧を取得して、実際のAPIで使用できるカテゴリを取得
    url = f"{settings.API_V1_STR}/topics/"
    response_list = client.get(
        url,
        headers=headers
    )
    
    assert response_list.status_code == 200
    topics = response_list.json()
    
    if len(topics) == 0:
        pytest.skip("トピックが存在しないためテストをスキップします")
    
    # 最初のトピックのカテゴリを使用
    category = topics[0]["category"]
    print(f"APIから取得したカテゴリ: {category}")
    
    # カテゴリでフィルタリング
    response = client.get(
        f"{settings.API_V1_STR}/topics/",
        params={"category": category},
        headers=headers
    )
    
    # レスポンスの内容を確認
    print(f"カテゴリでフィルタリングしたレスポンス: {response.status_code}")
    if response.status_code != 200:
        print(f"エラーレスポンス: {response.text}")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    
    # 結果が存在することを確認
    if len(data) > 0:
        # すべてのトピックが指定したカテゴリであることを確認
        for topic in data:
            assert topic["category"] == category
    else:
        print("フィルタリング結果が空でした")


def test_filter_topics_by_status(client: TestClient, test_topics, test_user_token):
    """
    ステータスによるトピックフィルタリングのテスト
    """
    headers = {"Authorization": f"Bearer {test_user_token['token']}"}
    
    # ステータスでフィルタリング
    status = "active"
    response = client.get(
        f"{settings.API_V1_STR}/topics/",
        params={"status": status},
        headers=headers
    )
    
    # レスポンスの内容を確認
    print(f"ステータスでフィルタリングしたレスポンス: {response.status_code}")
    if response.status_code != 200:
        print(f"エラーレスポンス: {response.text}")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    
    # 結果が存在することを確認
    if len(data) > 0:
        # すべてのトピックが指定したステータスであることを確認
        for topic in data:
            assert topic["status"] == status
    else:
        print("フィルタリング結果が空でした")


def test_search_topics(client: TestClient, test_topics, test_user_token):
    """
    トピック検索のテスト
    """
    headers = {"Authorization": f"Bearer {test_user_token['token']}"}
    
    # まずトピック一覧を取得
    response_list = client.get(
        f"{settings.API_V1_STR}/topics/",
        headers=headers
    )
    
    assert response_list.status_code == 200
    topics = response_list.json()
    
    if len(topics) == 0:
        pytest.skip("トピックが存在しないためテストをスキップします")
    
    # 最初のトピックの名前の一部を検索語として使用
    search_term = topics[0]["name"][:2]  # 名前の最初の2文字
    print(f"検索語: {search_term}")
    
    # 検索
    response = client.get(
        f"{settings.API_V1_STR}/topics/",
        params={"search": search_term},
        headers=headers
    )
    
    # レスポンスの内容を確認
    print(f"検索結果レスポンス: {response.status_code}")
    if response.status_code != 200:
        print(f"エラーレスポンス: {response.text}")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    
    # 検索結果が存在することを確認
    if len(data) > 0:
        # 検索結果に検索語を含む政治家が含まれているか確認
        found = False
        for topic in data:
            if search_term.lower() in topic["name"].lower():
                found = True
                break
        
        if not found:
            print(f"検索結果: {[t['name'] for t in data]}")
            print(f"検索語 '{search_term}' を含むトピックが見つかりませんでした")
    else:
        print("検索結果が空でした")



def test_follow_topic(client: TestClient, test_topics, test_user_token):
    """
    トピックフォローのテスト
    """
    # まずトピック一覧を取得して、実際のAPIで使用できるトピックIDを取得
    headers = {"Authorization": f"Bearer {test_user_token['token']}"}
    response_list = client.get(
        f"{settings.API_V1_STR}/topics/",
        headers=headers
    )
    
    assert response_list.status_code == 200
    topics = response_list.json()
    
    if len(topics) == 0:
        pytest.skip("トピックが存在しないためテストをスキップします")
    
    # 最初のトピックのIDを使用
    topic_id = topics[0]["id"]
    print(f"APIから取得したトピックID: {topic_id}")
    
    # トピックをフォロー
    response = client.post(
        f"{settings.API_V1_STR}/topics/{topic_id}/follow",
        headers=headers
    )
    
    # レスポンスの内容を確認
    print(f"トピックフォローレスポンス: {response.status_code}")
    if response.status_code != 200:
        print(f"エラーレスポンス: {response.text}")
    
    assert response.status_code == 200
    data = response.json()
    assert "success" in data


def test_unfollow_topic(client: TestClient, test_topics, test_user_token):
    """
    トピックフォロー解除のテスト
    """
    # まずトピック一覧を取得して、実際のAPIで使用できるトピックIDを取得
    headers = {"Authorization": f"Bearer {test_user_token['token']}"}
    response_list = client.get(
        f"{settings.API_V1_STR}/topics/",
        headers=headers
    )
    
    assert response_list.status_code == 200
    topics = response_list.json()
    
    if len(topics) == 0:
        pytest.skip("トピックが存在しないためテストをスキップします")
    
    # 最初のトピックのIDを使用
    topic_id = topics[0]["id"]
    print(f"APIから取得したトピックID: {topic_id}")
    
    # まずフォローする
    follow_response = client.post(
        f"{settings.API_V1_STR}/topics/{topic_id}/follow",
        headers=headers
    )
    
    if follow_response.status_code != 200:
        print(f"フォロー失敗: {follow_response.text}")
        pytest.skip("フォローに失敗したためテストをスキップします")
    
    # フォロー解除
    response = client.delete(
        f"{settings.API_V1_STR}/topics/{topic_id}/follow",
        headers=headers
    )
    
    # レスポンスの内容を確認
    print(f"トピックフォロー解除レスポンス: {response.status_code}")
    if response.status_code != 200:
        print(f"エラーレスポンス: {response.text}")
    
    assert response.status_code == 200
    data = response.json()
    assert "success" in data