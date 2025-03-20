from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# 共通プロパティ
class CommentBase(BaseModel):
    """
    コメントの基本情報
    """
    content: Optional[str] = None
    parent_id: Optional[str] = None


# 作成時に必要なプロパティ
class CommentCreate(CommentBase):
    """
    コメント作成時のスキーマ
    """
    content: str = Field(..., min_length=1, max_length=1000)


# 更新時に必要なプロパティ
class CommentUpdate(CommentBase):
    """
    コメント更新時のスキーマ
    """
    content: str = Field(..., min_length=1, max_length=1000)


# ユーザー情報のスキーマ
class CommentUser(BaseModel):
    """
    コメントユーザー情報のスキーマ
    """
    id: str
    username: str
    profile_image: Optional[str] = None

    class Config:
        from_attributes = True


# DBから取得したデータを返すためのスキーマ
class Comment(CommentBase):
    """
    コメント情報のレスポンススキーマ
    """
    id: str
    user_id: str
    statement_id: str
    content: str
    status: str
    likes_count: int = 0
    replies_count: int = 0
    created_at: datetime
    updated_at: datetime
    user: CommentUser
    is_liked: Optional[bool] = False
    is_own: Optional[bool] = False
    
    class Config:
        from_attributes = True


# コメント一覧のレスポンススキーマ
class CommentList(BaseModel):
    """
    コメント一覧のレスポンススキーマ
    """
    total: int
    comments: List[Comment]