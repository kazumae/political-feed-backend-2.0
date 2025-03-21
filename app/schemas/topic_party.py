from typing import List, Optional

from pydantic import BaseModel, Field


class TopicPartyStance(BaseModel):
    """
    トピックに対する政党のスタンス情報
    """
    party_id: str
    party_name: str
    stance: str = Field(..., description="スタンス（support, oppose, neutral, unknown）")
    confidence: int = Field(50, description="確信度（0-100）")
    summary: Optional[str] = None
    manifesto_url: Optional[str] = None

    class Config:
        from_attributes = True


class TopicPartyStances(BaseModel):
    """
    トピックに関する政党スタンス一覧
    """
    topic_id: str
    topic_name: str
    parties: List[TopicPartyStance] = []