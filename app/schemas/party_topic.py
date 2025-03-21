from typing import List, Optional

from pydantic import BaseModel, Field


class PartyTopicStance(BaseModel):
    """
    政党のトピックに対するスタンス情報
    """
    topic_id: str
    topic_name: str
    topic_slug: str
    stance: str = Field(..., description="スタンス（support, oppose, neutral, unknown）")
    confidence: int = Field(50, description="確信度（0-100）")
    summary: Optional[str] = None
    manifesto_url: Optional[str] = None
    last_updated: Optional[str] = None

    class Config:
        from_attributes = True


class PartyTopicStances(BaseModel):
    """
    政党のトピック別スタンス一覧
    """
    party_id: str
    party_name: str
    topics: List[PartyTopicStance] = []