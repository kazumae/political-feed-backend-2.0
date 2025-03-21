"""
発言APIのテスト
"""
import pytest
from app.models.statement import Statement
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def test_get_statements(client: TestClient, db: Session):
    """
    発言一覧取得APIのテスト
    """
    # APIリクエスト
    response = client.get("/api/v1/statements/")
    
    # レスポンスの検証
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert isinstance(data["items"], list)
    assert len(data["items"]) > 0
    
    # 最初の発言の構造を検証
    statement = data["items"][0]
    assert "id" in statement
    assert "content" in statement
    assert "politician" in statement
    assert "statement_date" in statement


def test_get_statement_by_id(client: TestClient, db: Session):
    """
    発言詳細取得APIのテスト
    """
    # テスト用の発言を取得
    statement = db.query(Statement).first()
    assert statement is not None
    
    # APIリクエスト
    response = client.get(f"/api/v1/statements/{statement.id}")
    
    # レスポンスの検証
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == statement.id
    assert data["content"] == statement.content
    assert "politician" in data
    assert "topics" in data


def test_get_statement_not_found(client: TestClient):
    """
    存在しない発言の取得テスト
    """
    # 存在しないIDでAPIリクエスト
    response = client.get("/api/v1/statements/00000000-0000-0000-0000-000000000000")
    
    # レスポンスの検証
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_get_statement_comments(client: TestClient, db: Session):
    """
    発言のコメント一覧取得APIのテスト
    """
    # テスト用の発言を取得
    statement = db.query(Statement).first()
    assert statement is not None
    
    # APIリクエスト
    response = client.get(f"/api/v1/statements/{statement.id}/comments")
    
    # レスポンスの検証
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert isinstance(data["items"], list)
    
    # コメントがある場合は内容を検証
    if len(data["items"]) > 0:
        comment = data["items"][0]
        assert "id" in comment
        assert "content" in comment
        assert "user" in comment
        assert "created_at" in comment


def test_search_statements(client: TestClient):
    """
    発言検索APIのテスト
    """
    # 検索クエリ
    search_query = "経済"  # テストデータに含まれる可能性が高いキーワード
    
    # APIリクエスト
    response = client.get(f"/api/v1/statements/search?q={search_query}")
    
    # レスポンスの検証
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert isinstance(data["items"], list)
    
    # 検索結果がある場合は内容を検証
    if len(data["items"]) > 0:
        for statement in data["items"]:
            assert search_query in statement["content"]


def test_filter_statements_by_topic(client: TestClient, db: Session):
    """
    トピックによる発言フィルタリングのテスト
    """
    # 最初の発言を取得し、そのトピックIDを使用
    statement = db.query(Statement).first()
    assert statement is not None
    
    # 発言に関連するトピックがあるか確認
    if statement.topics:
        topic_id = statement.topics[0].id
        
        # APIリクエスト
        response = client.get(f"/api/v1/statements/?topic_id={topic_id}")
        
        # レスポンスの検証
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert isinstance(data["items"], list)
        
        # 結果がある場合は、すべての発言が指定したトピックに関連していることを確認
        if len(data["items"]) > 0:
            for item in data["items"]:
                topic_ids = [topic["id"] for topic in item["topics"]]
                assert topic_id in topic_ids


def test_filter_statements_by_date_range(client: TestClient):
    """
    日付範囲による発言フィルタリングのテスト
    """
    # 日付範囲
    start_date = "2023-01-01"
    end_date = "2025-12-31"
    
    # APIリクエスト
    response = client.get(
        f"/api/v1/statements/?start_date={start_date}&end_date={end_date}"
    )
    
    # レスポンスの検証
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert isinstance(data["items"], list)
    
    # 結果がある場合は、すべての発言が指定した日付範囲内であることを確認
    if len(data["items"]) > 0:
        for item in data["items"]:
            statement_date = item["statement_date"].split("T")[0]  # 日付部分のみ抽出
            assert start_date <= statement_date <= end_date