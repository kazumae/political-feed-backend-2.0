from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


# 共通プロパティ
class PartyBase(BaseModel):
    """
    政党の基本情報
    """
    name: Optional[str] = None
    short_name: Optional[str] = None
    status: Optional[str] = None
    founded_date: Optional[datetime] = None
    disbanded_date: Optional[datetime] = None
    logo_url: Optional[str] = None
    color_code: Optional[str] = None
    description: Optional[str] = None


# 作成時に必要なプロパティ
class PartyCreate(PartyBase):
    """
    政党作成時のスキーマ
    """
    name: str = Field(..., min_length=1, max_length=100)
    status: str = Field("active")


# 更新時に必要なプロパティ
class PartyUpdate(PartyBase):
    """
    政党更新時のスキーマ
    """
    pass


# 政党の所属政治家情報
class PartyPolitician(BaseModel):
    """
    政党に所属する政治家の情報
    """
    id: str
    name: str
    role: Optional[str] = None
    image_url: Optional[str] = None

    class Config:
        from_attributes = True


# 政党の代表者情報
class PartyPresident(BaseModel):
    """
    政党の代表者情報
    """
    id: str
    name: str
    image_url: Optional[str] = None

    class Config:
        from_attributes = True


# DBから取得したデータを返すためのスキーマ
class Party(PartyBase):
    """
    政党情報のレスポンススキーマ
    """
    id: str
    name: str
    short_name: Optional[str] = None
    status: str
    founded_date: Optional[datetime] = None
    disbanded_date: Optional[datetime] = None
    logo_url: Optional[str] = None
    color_code: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# 詳細情報を含む政党スキーマ
class PartyDetail(Party):
    """
    詳細情報を含む政党情報のレスポンススキーマ
    """
    president: Optional[PartyPresident] = None
    headquarters: Optional[str] = None
    ideology: Optional[str] = None
    website_url: Optional[str] = None
    social_media: Optional[str] = None
    history: Optional[str] = None
    additional_info: Optional[str] = None
    members_count: int = 0