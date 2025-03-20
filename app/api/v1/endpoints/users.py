from typing import Any, List

from app.api.deps import get_current_active_superuser, get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import User as UserSchema
from app.schemas.user import UserCreate, UserUpdate
from app.services.user import (
    create_user,
    get_user,
    get_user_by_email,
    get_users,
    update_user,
)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/me", response_model=UserSchema)
def read_user_me(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    現在のユーザー情報を取得する
    """
    return current_user


@router.put("/me", response_model=UserSchema)
def update_user_me(
    *,
    db: Session = Depends(get_db),
    user_in: UserUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    現在のユーザー情報を更新する
    """
    user = update_user(db, db_obj=current_user, obj_in=user_in)
    return user


@router.get("", response_model=List[UserSchema])
def read_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    ユーザー一覧を取得する（管理者のみ）
    """
    users = get_users(db, skip=skip, limit=limit)
    return users


@router.post("", response_model=UserSchema)
def create_user_admin(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    新規ユーザーを作成する（管理者のみ）
    """
    user = get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="このメールアドレスは既に登録されています",
        )
    user = create_user(db, obj_in=user_in)
    return user


@router.get("/{user_id}", response_model=UserSchema)
def read_user_by_id(
    user_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    特定のユーザー情報を取得する
    """
    user = get_user(db, id=user_id)
    if user == current_user:
        return user
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="このアクションを実行する権限がありません",
        )
    return user


@router.put("/{user_id}", response_model=UserSchema)
def update_user_admin(
    *,
    db: Session = Depends(get_db),
    user_id: str,
    user_in: UserUpdate,
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    ユーザー情報を更新する（管理者のみ）
    """
    user = get_user(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ユーザーが見つかりません",
        )
    user = update_user(db, db_obj=user, obj_in=user_in)
    return user