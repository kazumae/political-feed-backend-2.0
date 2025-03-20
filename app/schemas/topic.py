from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# 共通プロパティ
class TopicBase(BaseModel):
    """
    トピックの基本情報
    """
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    importance: Optional[int] = None
    icon_url: Optional[str] = None
    color_code: Optional[str] = None
    status: Optional[str] = None


# 作成時に必要なプロパティ
class TopicCreate(TopicBase):
    """
    トピック作成時のスキーマ
    """
    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=100)
    category: str = Field(...)
    status: str = Field("active")


# 更新時に必要なプロパティ
class TopicUpdate(TopicBase):
    """
    トピック更新時のスキーマ
    """
    pass


# トピック関連のスキーマ
class TopicRelation(BaseModel):
    """
    トピック関連情報のスキーマ
    """
    id: str
    name: str
    slug: str
    relation_type: str
    strength: int

    class Config:
        from_attributes = True


# DBから取得したデータを返すためのスキーマ
class Topic(TopicBase):
    """
    トピック情報のレスポンススキーマ
    """
    id: str
    name: str
    slug: str
    category: str
    importance: int
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# 詳細情報を含むトピックスキーマ
class TopicWithDetails(Topic):
    """
    詳細情報を含むトピック情報のレスポンススキーマ
    """
    related_topics: List[TopicRelation] = []
    is_following: Optional[bool] = False