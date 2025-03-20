from typing import Any, Dict, List, Optional, Union

from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from sqlalchemy.orm import Session


def get_user(db: Session, id: str) -> Optional[User]:
    """
    IDでユーザーを取得する
    
    Args:
        db: データベースセッション
        id: ユーザーID
        
    Returns:
        ユーザーオブジェクト、存在しない場合はNone
    """
    return db.query(User).filter(User.id == id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    メールアドレスでユーザーを取得する
    
    Args:
        db: データベースセッション
        email: メールアドレス
        
    Returns:
        ユーザーオブジェクト、存在しない場合はNone
    """
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """
    ユーザー名でユーザーを取得する
    
    Args:
        db: データベースセッション
        username: ユーザー名
        
    Returns:
        ユーザーオブジェクト、存在しない場合はNone
    """
    return db.query(User).filter(User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """
    ユーザー一覧を取得する
    
    Args:
        db: データベースセッション
        skip: スキップ数
        limit: 取得上限
        
    Returns:
        ユーザーオブジェクトのリスト
    """
    return db.query(User).offset(skip).limit(limit).all()


def create_user(db: Session, obj_in: UserCreate) -> User:
    """
    新規ユーザーを作成する
    
    Args:
        db: データベースセッション
        obj_in: ユーザー作成スキーマ
        
    Returns:
        作成されたユーザーオブジェクト
    """
    db_obj = User(
        email=obj_in.email,
        username=obj_in.username,
        password_hash=get_password_hash(obj_in.password),
        role="user",
        status="active",
        email_verified=False,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_user(
    db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
) -> User:
    """
    ユーザー情報を更新する
    
    Args:
        db: データベースセッション
        db_obj: 更新対象のユーザーオブジェクト
        obj_in: 更新データ（UserUpdateオブジェクトまたは辞書）
        
    Returns:
        更新されたユーザーオブジェクト
    """
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.model_dump(exclude_unset=True)
    
    if update_data.get("password"):
        hashed_password = get_password_hash(update_data["password"])
        del update_data["password"]
        update_data["password_hash"] = hashed_password
    
    for field in update_data:
        if field in update_data:
            setattr(db_obj, field, update_data[field])
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def authenticate_user(
    db: Session, *, email: str, password: str
) -> Optional[User]:
    """
    メールアドレスとパスワードでユーザーを認証する
    
    Args:
        db: データベースセッション
        email: メールアドレス
        password: パスワード
        
    Returns:
        認証成功時はユーザーオブジェクト、失敗時はNone
    """
    user = get_user_by_email(db, email=email)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user