from datetime import timedelta
from typing import Any

from app.api.deps import get_current_user, get_db
from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token
from app.models.user import User
from app.schemas.token import RefreshToken, Token, TokenPayload
from app.schemas.user import UserCreate
from app.services.user import (
    authenticate_user,
    create_user,
    get_user,
    get_user_by_email,
)
from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from pydantic import EmailStr
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/login", response_model=Token)
def login_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2互換のトークンログインを取得する
    """
    user = authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="メールアドレスまたはパスワードが正しくありません",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 非アクティブユーザーのチェック
    if user.status == "inactive":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="アカウントが無効です",
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    return {
        "access_token": create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "refresh_token": create_refresh_token(
            user.id, expires_delta=refresh_token_expires
        ),
        "token_type": "bearer",
    }


@router.post("/register", response_model=Token)
def register_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
) -> Any:
    """
    新規ユーザーを登録する
    """
    # メールアドレスの重複チェック
    existing_user = get_user_by_email(db, email=user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="このメールアドレスは既に登録されています",
        )
    
    user = create_user(db, obj_in=user_in)
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    return {
        "access_token": create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "refresh_token": create_refresh_token(
            user.id, expires_delta=refresh_token_expires
        ),
        "token_type": "bearer",
    }


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    ログアウト処理
    
    注: JWTはステートレスなため、サーバー側でのトークン無効化は行わない
    クライアント側でトークンを破棄する責任がある
    """
    return {"success": True}


@router.post("/refresh", response_model=Token)
def refresh_token(
    db: Session = Depends(get_db),
    refresh_token: RefreshToken = Body(...),
) -> Any:
    """
    リフレッシュトークンを使用して新しいアクセストークンを取得する
    """
    try:
        payload = jwt.decode(
            refresh_token.refresh_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (jwt.JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="無効なリフレッシュトークンです",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = get_user(db, id=token_data.sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ユーザーが見つかりません",
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    return {
        "access_token": create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "refresh_token": create_refresh_token(
            user.id, expires_delta=refresh_token_expires
        ),
        "token_type": "bearer",
    }


@router.post("/password/reset", status_code=status.HTTP_200_OK)
def reset_password_request(
    email: EmailStr = Body(..., embed=True),
    db: Session = Depends(get_db),
) -> Any:
    """
    パスワードリセットリクエスト
    
    メールアドレスに対してパスワードリセット用のリンクを送信する
    """
    user = get_user_by_email(db, email=email)
    if not user:
        # ユーザーが存在しない場合でも成功レスポンスを返す（セキュリティ上の理由）
        return {
            "success": True,
            "message": "パスワードリセット用のメールを送信しました（実際には送信されていません）"
        }
    
    # TODO: 実際のメール送信処理を実装
    # パスワードリセット用のトークンを生成し、メールで送信する
    
    return {
        "success": True,
        "message": "パスワードリセット用のメールを送信しました（実際には送信されていません）"
    }


@router.post("/password/confirm", status_code=status.HTTP_200_OK)
def reset_password_confirm(
    token: str = Body(...),
    new_password: str = Body(...),
    db: Session = Depends(get_db),
) -> Any:
    """
    パスワードリセット確認
    
    トークンを検証し、新しいパスワードを設定する
    """
    # TODO: トークンの検証とパスワード変更処理を実装
    # 現在はモック実装
    
    return {"success": True}


@router.get("/email/verify", status_code=status.HTTP_200_OK)
def verify_email(
    token: str,
    db: Session = Depends(get_db),
) -> Any:
    """
    メールアドレス確認
    
    トークンを検証し、メールアドレスを確認済みにする
    """
    # TODO: トークンの検証とメール確認処理を実装
    # 現在はモック実装
    
    return {"success": True}