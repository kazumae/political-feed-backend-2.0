from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# トピック情報のスキーマ
class StatementTopic(BaseModel):
    """
    発言に関連するトピック情報
    """
    id: str
    name: str
    slug: str
    category: str
    relevance: int = 50

    class Config:
        from_attributes = True


# 共通プロパティ
class StatementBase(BaseModel):
    """
    発言の基本情報
    """
    politician_id: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    source: Optional[str] = None
    source_url: Optional[str] = None
    statement_date: Optional[datetime] = None
    context: Optional[str] = None
    status: Optional[str] = None
    importance: Optional[int] = None


# 作成時に必要なプロパティ
class StatementCreate(StatementBase):
    """
    発言作成時のスキーマ
    """
    politician_id: str = Field(..., description="政治家ID")
    title: str = Field(..., min_length=1, description="タイトル")
    content: str = Field(..., min_length=1, description="発言内容")
    statement_date: datetime = Field(..., description="発言日時")
    topic_ids: Optional[List[str]] = Field(None, description="関連トピックID")


# 更新時に必要なプロパティ
class StatementUpdate(StatementBase):
    """
    発言更新時のスキーマ
    """
    topic_ids: Optional[List[str]] = Field(None, description="関連トピックID")


# DBから取得したデータを返すためのスキーマ
class Statement(StatementBase):
    """
    発言情報のレスポンススキーマ
    """
    id: str
    politician_id: str
    politician_name: str
    party_id: Optional[str] = None
    party_name: Optional[str] = None
    title: str
    content: str
    statement_date: datetime
    status: str
    importance: int
    likes_count: int = 0
    comments_count: int = 0
    created_at: datetime
    updated_at: datetime
    is_liked: Optional[bool] = False
    
    class Config:
        from_attributes = True


# 詳細情報を含む発言スキーマ
class StatementDetail(Statement):
    """
    詳細情報を含む発言情報のレスポンススキーマ
    """
    topics: List[StatementTopic] = []


# 発言一覧のレスポンススキーマ
class StatementList(BaseModel):
    """
    発言一覧のレスポンススキーマ
    """
    total: int
    statements: List[Statement]
    next_cursor: Optional[str] = None