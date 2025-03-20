from typing import Optional

from pydantic import BaseModel


class Token(BaseModel):
    """
    アクセストークンスキーマ
    """
    access_token: str
    refresh_token: str
    token_type: str


class RefreshToken(BaseModel):
    """
    リフレッシュトークンスキーマ
    """
    refresh_token: str


class TokenPayload(BaseModel):
    """
    トークンペイロードスキーマ
    """
    sub: Optional[str] = None
    exp: Optional[int] = None