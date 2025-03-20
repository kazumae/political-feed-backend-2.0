from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# 政治家スキーマの共通フィールド
class PoliticianBase(BaseModel):
    name: str = Field(..., description="政治家の名前")
    name_kana: Optional[str] = Field(None, description="政治家の名前（カナ）")
    current_party_id: Optional[str] = Field(None, description="現在所属している政党のID")
    role: Optional[str] = Field(None, description="役職")
    status: str = Field("active", description="ステータス（active, inactive, former）")
    image_url: Optional[str] = Field(None, description="画像URL")
    profile_summary: Optional[str] = Field(None, description="プロフィール概要")


# 政治家作成時のスキーマ
class PoliticianCreate(PoliticianBase):
    pass


# 政治家更新時のスキーマ
class PoliticianUpdate(BaseModel):
    name: Optional[str] = Field(None, description="政治家の名前")
    name_kana: Optional[str] = Field(None, description="政治家の名前（カナ）")
    current_party_id: Optional[str] = Field(None, description="現在所属している政党のID")
    role: Optional[str] = Field(None, description="役職")
    status: Optional[str] = Field(None, description="ステータス（active, inactive, former）")
    image_url: Optional[str] = Field(None, description="画像URL")
    profile_summary: Optional[str] = Field(None, description="プロフィール概要")


# 政治家詳細の共通フィールド
class PoliticianDetailBase(BaseModel):
    birth_date: Optional[datetime] = Field(None, description="生年月日")
    birth_place: Optional[str] = Field(None, description="出身地")
    education: Optional[str] = Field(None, description="学歴（JSON形式）")
    career: Optional[str] = Field(None, description="経歴（JSON形式）")
    election_history: Optional[str] = Field(None, description="選挙履歴（JSON形式）")
    website_url: Optional[str] = Field(None, description="ウェブサイトURL")
    social_media: Optional[str] = Field(None, description="SNSアカウント（JSON形式）")
    additional_info: Optional[str] = Field(None, description="追加情報（JSON形式）")


# 政治家詳細作成時のスキーマ
class PoliticianDetailCreate(PoliticianDetailBase):
    pass


# 政治家詳細更新時のスキーマ
class PoliticianDetailUpdate(PoliticianDetailBase):
    pass


# 政治家所属政党履歴の共通フィールド
class PoliticianPartyBase(BaseModel):
    politician_id: str = Field(..., description="政治家ID")
    party_id: str = Field(..., description="政党ID")
    joined_date: Optional[datetime] = Field(None, description="入党日")
    left_date: Optional[datetime] = Field(None, description="退党日")
    role: Optional[str] = Field(None, description="役職")
    is_current: bool = Field(False, description="現在所属しているか")
    remarks: Optional[str] = Field(None, description="備考")


# 政治家所属政党履歴作成時のスキーマ
class PoliticianPartyCreate(PoliticianPartyBase):
    pass


# 政治家所属政党履歴更新時のスキーマ
class PoliticianPartyUpdate(BaseModel):
    joined_date: Optional[datetime] = Field(None, description="入党日")
    left_date: Optional[datetime] = Field(None, description="退党日")
    role: Optional[str] = Field(None, description="役職")
    is_current: Optional[bool] = Field(None, description="現在所属しているか")
    remarks: Optional[str] = Field(None, description="備考")


# DB内の政治家詳細を表すスキーマ
class PoliticianDetailInDB(PoliticianDetailBase):
    politician_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# DB内の政治家所属政党履歴を表すスキーマ
class PoliticianPartyInDB(PoliticianPartyBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# DB内の政治家を表すスキーマ
class PoliticianInDB(PoliticianBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# レスポンス用の政治家詳細スキーマ
class PoliticianDetail(PoliticianDetailInDB):
    pass


# レスポンス用の政治家所属政党履歴スキーマ
class PoliticianParty(PoliticianPartyInDB):
    pass


# レスポンス用の政治家スキーマ（基本情報のみ）
class Politician(PoliticianInDB):
    pass


# レスポンス用の政治家詳細スキーマ（詳細情報を含む）
class PoliticianWithDetails(Politician):
    details: Optional[PoliticianDetail] = None
    party_history: List[PoliticianParty] = []