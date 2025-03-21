"""
テスト用の設定をオーバーライドするモジュール
"""
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, ConfigDict, PostgresDsn, field_validator
from pydantic_settings import BaseSettings


class TestSettings(BaseSettings):
    """
    テスト用の設定クラス
    """
    model_config = ConfigDict(case_sensitive=True)

    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "testsecretkey"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # SQLiteのURLを許可する
    DATABASE_URL: str = "sqlite:///./test.db"
    
    # その他の設定
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    PROJECT_NAME: str = "Political Feed API (Test)"
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)


# テスト用の設定インスタンスを作成
test_settings = TestSettings()