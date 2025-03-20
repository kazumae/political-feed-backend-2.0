import uuid
from datetime import datetime

from app.db.session import Base
from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship


class Politician(Base):
    """
    政治家モデル
    """
    __tablename__ = "politicians"

    id = Column(
        CHAR(36),
        primary_key=True,
        index=True,
        default=lambda: str(uuid.uuid4())
    )
    name = Column(String(100), nullable=False, index=True)
    name_kana = Column(String(100), nullable=True)
    current_party_id = Column(
        CHAR(36),
        ForeignKey("parties.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    role = Column(String(100), nullable=True)
    status = Column(
        Enum("active", "inactive", "former", name="politician_status"),
        default="active",
        nullable=False,
        index=True
    )
    image_url = Column(String(255), nullable=True)
    profile_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # リレーションシップ
    current_party = relationship("Party", back_populates="politicians")
    statements = relationship(
        "Statement", back_populates="politician", cascade="all, delete-orphan"
    )
    politician_details = relationship(
        "PoliticianDetail", back_populates="politician", 
        uselist=False, cascade="all, delete-orphan"
    )
    politician_parties = relationship(
        "PoliticianParty", back_populates="politician", 
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Politician {self.name}>"


class PoliticianDetail(Base):
    """
    政治家詳細モデル
    """
    __tablename__ = "politician_details"

    politician_id = Column(
        CHAR(36),
        ForeignKey("politicians.id", ondelete="CASCADE"),
        primary_key=True
    )
    birth_date = Column(DateTime, nullable=True)
    birth_place = Column(String(100), nullable=True)
    education = Column(Text, nullable=True)  # JSON形式で保存
    career = Column(Text, nullable=True)  # JSON形式で保存
    election_history = Column(Text, nullable=True)  # JSON形式で保存
    website_url = Column(String(255), nullable=True)
    social_media = Column(Text, nullable=True)  # JSON形式で保存
    additional_info = Column(Text, nullable=True)  # JSON形式で保存
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # リレーションシップ
    politician = relationship(
        "Politician", back_populates="politician_details"
    )

    def __repr__(self) -> str:
        return f"<PoliticianDetail {self.politician_id}>"


class PoliticianParty(Base):
    """
    政治家所属政党履歴モデル
    """
    __tablename__ = "politician_parties"

    id = Column(
        CHAR(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    politician_id = Column(
        CHAR(36),
        ForeignKey("politicians.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    party_id = Column(
        CHAR(36),
        ForeignKey("parties.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    joined_date = Column(DateTime, nullable=True)
    left_date = Column(DateTime, nullable=True)
    role = Column(String(100), nullable=True)
    is_current = Column(Boolean, default=False, nullable=False)
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # リレーションシップ
    politician = relationship(
        "Politician", back_populates="politician_parties"
    )
    party = relationship("Party", back_populates="politician_parties")

    def __repr__(self) -> str:
        return f"<PoliticianParty {self.politician_id} - {self.party_id}>"