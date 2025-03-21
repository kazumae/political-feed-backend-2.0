"""
APIの基本機能テスト
"""
import pytest
from fastapi.testclient import TestClient


def test_api_health(client):
    """
    APIのヘルスチェックテスト
    """
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_api_version(client):
    """
    APIのバージョン取得テスト
    """
    response = client.get("/api/v1/version")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data