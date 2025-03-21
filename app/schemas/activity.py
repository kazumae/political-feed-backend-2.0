from datetime import datetime
from typing import List, Optional

from app.schemas.comment import Comment
from app.schemas.politician import Politician
from app.schemas.statement import Statement
from app.schemas.topic import Topic
from pydantic import BaseModel


class UserActivity(BaseModel):
    """
    ユーザーアクティビティ
    """
    id: str
    user_id: str
    activity_type: str
    target_type: str
    target_id: str
    metadata: Optional[dict] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ViewHistory(BaseModel):
    """
    閲覧履歴
    """
    statement_id: str
    statement_excerpt: str
    politician_name: str
    viewed_at: datetime


class Notification(BaseModel):
    """
    通知
    """
    id: str
    type: str
    content: str
    read: bool
    created_at: datetime
    actor_id: Optional[str] = None
    target_type: Optional[str] = None
    target_id: Optional[str] = None
    metadata: Optional[dict] = None


class UserFollowingPoliticians(BaseModel):
    """
    ユーザーがフォローしている政治家一覧
    """
    total: int
    politicians: List[Politician] = []


class UserFollowingTopics(BaseModel):
    """
    ユーザーがフォローしているトピック一覧
    """
    total: int
    topics: List[Topic] = []


class UserLikedStatements(BaseModel):
    """
    ユーザーがいいねした発言一覧
    """
    total: int
    statements: List[Statement] = []


class UserComments(BaseModel):
    """
    ユーザーが投稿したコメント一覧
    """
    total: int
    comments: List[Comment] = []


class UserViewHistory(BaseModel):
    """
    ユーザーの閲覧履歴
    """
    total: int
    history: List[ViewHistory] = []


class UserNotifications(BaseModel):
    """
    ユーザーの通知一覧
    """
    total: int
    notifications: List[Notification] = []
    unread_count: int = 0