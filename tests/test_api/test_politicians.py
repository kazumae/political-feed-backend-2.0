import pytest
from app.core.config import settings
from app.models.party import Party
from app.models.politician import Politician, PoliticianDetail
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
    
    # 政治家詳細情報も作成
    politician_detail = PoliticianDetail(
        politician_id=politician.id,
        birth_place="東京都",
        website_url="https://example.com/test",
    )
    db.add(politician_detail)
    db.commit()
    
    db.refresh(politician)
    return politician


def test_get_politicians(client: TestClient, auth_token, test_politician):
    """
    政治家一覧取得のテスト
    """
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get(f"{settings.API_V1_STR}/politicians/", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    
    # テスト用政治家が含まれているか確認
    politician_ids = [p["id"] for p in data]
    assert test_politician.id in politician_ids


def test_get_politician_by_id(client: TestClient, auth_token, test_politician):
    """
    政治家詳細取得のテスト
    """
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get(
        f"{settings.API_V1_STR}/politicians/{test_politician.id}",
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_politician.id
    assert data["name"] == test_politician.name
    assert "party" in data
    assert "details" in data


def test_get_politician_not_found(client: TestClient, auth_token):
    """
    存在しない政治家IDでの取得失敗テスト
    """
    headers = {"Authorization": f"Bearer {auth_token}"}
    non_existent_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(
        f"{settings.API_V1_STR}/politicians/{non_existent_id}",
        headers=headers
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_filter_politicians_by_party(
    client: TestClient, auth_token, test_politician, test_party
):
    """
    政党IDによる政治家フィルタリングのテスト
    """
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get(
        f"{settings.API_V1_STR}/politicians/",
        params={"party_id": test_party.id},
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    
    # すべての政治家が指定した政党に所属しているか確認
    for politician in data:
        assert politician["party"]["id"] == test_party.id


def test_filter_politicians_by_status(client: TestClient, auth_token, test_politician):
    """
    ステータスによる政治家フィルタリングのテスト
    """
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get(
        f"{settings.API_V1_STR}/politicians/",
        params={"status": "active"},
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    
    # すべての政治家がアクティブステータスであることを確認
    for politician in data:
        assert politician["status"] == "active"


def test_search_politicians(client: TestClient, auth_token, test_politician):
    """
    政治家検索のテスト
    """
    headers = {"Authorization": f"Bearer {auth_token}"}
    # 名前の一部で検索
    search_term = test_politician.name[:3]  # 名前の最初の3文字
    response = client.get(
        f"{settings.API_V1_STR}/politicians/",
        params={"search": search_term},
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    
    # 検索結果にテスト用政治家が含まれているか確認
    politician_ids = [p["id"] for p in data]
    assert test_politician.id in politician_ids