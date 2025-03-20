from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# 共通プロパティ
class UserBase(BaseModel):
    """
    ユーザーの基本情報
    """
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    is_active: Optional[bool] = True


# 作成時に必要なプロパティ
class UserCreate(UserBase):
    """
    ユーザー作成時のスキーマ
    """
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)


# 更新時に必要なプロパティ
class UserUpdate(UserBase):
    """
    ユーザー更新時のスキーマ
    """
    password: Optional[str] = Field(None, min_length=8)
    profile_image: Optional[str] = None


# パスワード変更時に必要なプロパティ
class UserPasswordUpdate(BaseModel):
    """
    パスワード変更時のスキーマ
    """
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8)


# アカウント削除時に必要なプロパティ
class UserDelete(BaseModel):
    """
    アカウント削除時のスキーマ
    """
    password: str = Field(..., min_length=1)


# DBから取得したデータを返すためのスキーマ
class User(UserBase):
    """
    ユーザー情報のレスポンススキーマ
    """
    id: str
    email: EmailStr
    username: str
    role: str
    status: str
    email_verified: bool
    profile_image: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None
    
    class Config:
        """
        Pydanticの設定クラス
        """
        from_attributes = True