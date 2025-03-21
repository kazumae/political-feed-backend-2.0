"""
テスト用の設定をオーバーライドするモジュール
"""
import os
import sys
from typing import Any, List, Union

from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings


class TestSettings(BaseSettings):
    """テスト用の設定クラス"""
    # プロジェクト情報
    PROJECT_NAME: str = "政治家フィードAPI (テスト環境)"
    PROJECT_DESCRIPTION: str = "政治家の発言をキュレーションし、有権者に分かりやすい形で提供するAPIサービス"
    PROJECT_VERSION: str = "0.1.0"
    
    # API設定
    API_V1_STR: str = "/api/v1"
    
    # セキュリティ設定
    SECRET_KEY: str = "testsecretkey"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS設定
    CORS_ORIGINS: List[AnyHttpUrl] = []
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(
        cls, v: Union[str, List[str]]
    ) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # データベース設定 - SQLiteを使用
    DATABASE_URL: Any = "sqlite:///./test.db"
    
    # Redis設定
    REDIS_URL: str = "memory://"
    
    # MinIO設定
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_SECURE: bool = False
    MINIO_BUCKET_NAME: str = "political-feed-test"
    
    # 環境設定
    ENVIRONMENT: str = "testing"
    
    class Config:
        case_sensitive = True


# テスト設定のインスタンスを作成
settings = TestSettings()

# app.core.config をオーバーライドする
# これにより、app.core.config.settings を参照するコードは
# このモジュールの settings を参照するようになる
sys.modules['app.core.config'] = sys.modules[__name__]