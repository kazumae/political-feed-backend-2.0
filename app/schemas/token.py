from typing import Optional

from pydantic import BaseModel


class Token(BaseModel):
    """
    アクセストークンスキーマ
    """
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    """
    トークンペイロードスキーマ
    """
    sub: Optional[str] = None