"""
ヘルスチェックAPI
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health_check():
    """
    APIのヘルスチェック
    """
    return {"status": "ok"}


@router.get("/version")
def get_version():
    """
    APIのバージョン取得
    """
    return {"version": "0.1.0"}