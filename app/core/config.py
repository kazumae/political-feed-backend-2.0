import os
import secrets
from typing import Any, List, Optional, Union

from pydantic import AnyHttpUrl, MySQLDsn, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # プロジェクト情報
    PROJECT_NAME: str = "政治家フィードAPI"
    PROJECT_DESCRIPTION: str = "政治家の発言をキュレーションし、有権者に分かりやすい形で提供するAPIサービス"
    PROJECT_VERSION: str = "0.1.0"
    
    # API設定
    API_V1_STR: str = "/api/v1"
    
    # セキュリティ設定
    SECRET_KEY: str = secrets.token_urlsafe(32)
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
    
    # データベース設定
    DATABASE_URL: Optional[MySQLDsn] = None
    
    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str]) -> Any:
        if isinstance(v, str):
            return v
        return MySQLDsn.build(
            scheme="mysql+pymysql",
            username=os.getenv("MYSQL_USER", "political_user"),
            password=os.getenv("MYSQL_PASSWORD", "political_password"),
            host=os.getenv("MYSQL_HOST", "db"),
            port=os.getenv("MYSQL_PORT", "3306"),
            path=f"/{os.getenv('MYSQL_DATABASE', 'political_feed_db')}",
        )
    
    # Redis設定
    REDIS_URL: str = "redis://redis:6379/0"
    
    # MinIO設定
    MINIO_ENDPOINT: str = "minio:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_SECURE: bool = False
    MINIO_BUCKET_NAME: str = "political-feed"
    
    # 環境設定
    ENVIRONMENT: str = "development"
    
    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()