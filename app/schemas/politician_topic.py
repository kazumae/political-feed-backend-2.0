from typing import List, Optional

from pydantic import BaseModel, Field


class PoliticianTopicStance(BaseModel):
    """
    政治家のトピックに対するスタンス情報
    """
    topic_id: str
    topic_name: str
    topic_slug: str
    stance: str = Field(..., description="スタンス（support, oppose, neutral, unknown）")
    confidence: int = Field(50, description="確信度（0-100）")
    summary: Optional[str] = None
    last_updated: Optional[str] = None

    class Config:
        from_attributes = True


class PoliticianTopicStances(BaseModel):
    """
    政治家のトピック別スタンス一覧
    """
    politician_id: str
    politician_name: str
    topics: List[PoliticianTopicStance] = []