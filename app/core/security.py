from datetime import datetime, timedelta
from typing import Any, Optional, Union

from app.core.config import settings
from jose import jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(
    subject: Union[str, Any] = None, expires_delta: Optional[timedelta] = None, data: dict = None
) -> str:
    """
    アクセストークンを生成する
    
    Args:
        subject: トークンのサブジェクト（通常はユーザーID）
        expires_delta: トークンの有効期限
        data: トークンに含めるデータ（下位互換性のため）
        
    Returns:
        生成されたJWTトークン
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    # dataパラメータが提供された場合は、それを使用
    if data and "sub" in data:
        subject = data["sub"]
    
    to_encode = {"exp": expire, "sub": str(subject), "type": "access"}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(
    subject: Union[str, Any] = None, expires_delta: Optional[timedelta] = None, data: dict = None
) -> str:
    """
    リフレッシュトークンを生成する
    
    Args:
        subject: トークンのサブジェクト（通常はユーザーID）
        expires_delta: トークンの有効期限
        data: トークンに含めるデータ（下位互換性のため）
        
    Returns:
        生成されたJWTトークン
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
    
    # dataパラメータが提供された場合は、それを使用
    if data and "sub" in data:
        subject = data["sub"]
        
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    平文パスワードとハッシュ化されたパスワードを検証する
    
    Args:
        plain_password: 平文パスワード
        hashed_password: ハッシュ化されたパスワード
        
    Returns:
        パスワードが一致する場合はTrue、それ以外はFalse
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    パスワードをハッシュ化する
    
    Args:
        password: 平文パスワード
        
    Returns:
        ハッシュ化されたパスワード
    """
    return pwd_context.hash(password)