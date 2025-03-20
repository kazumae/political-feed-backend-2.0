from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.schemas.token import TokenPayload
from app.services.user import get_user
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

# OAuth2のトークン取得エンドポイント
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    """
    現在のユーザーを取得する
    
    Args:
        db: データベースセッション
        token: JWTトークン
        
    Returns:
        現在のユーザーオブジェクト
        
    Raises:
        HTTPException: トークンが無効な場合
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="認証情報が無効です",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = get_user(db, id=token_data.sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ユーザーが見つかりません",
        )
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    現在のアクティブなユーザーを取得する
    
    Args:
        current_user: 現在のユーザーオブジェクト
        
    Returns:
        現在のアクティブなユーザーオブジェクト
        
    Raises:
        HTTPException: ユーザーが非アクティブな場合
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="アカウントが無効です",
        )
    return current_user


def get_current_active_superuser(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    現在のアクティブな管理者ユーザーを取得する
    
    Args:
        current_user: 現在のユーザーオブジェクト
        
    Returns:
        現在のアクティブな管理者ユーザーオブジェクト
        
    Raises:
        HTTPException: ユーザーが管理者でない場合
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="管理者権限が必要です",
        )
    return current_user