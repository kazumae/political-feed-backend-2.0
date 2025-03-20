import uuid
from datetime import datetime

from app.db.session import Base
from sqlalchemy import Column, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship


class Party(Base):
    """
    政党モデル
    """
    __tablename__ = "parties"

    id = Column(
        CHAR(36),
        primary_key=True,
        index=True,
        default=lambda: str(uuid.uuid4())
    )
    name = Column(String(100), nullable=False, unique=True, index=True)
    short_name = Column(String(50), nullable=True)
    status = Column(
        Enum("active", "disbanded", "merged", name="party_status"),
        default="active",
        nullable=False,
        index=True
    )
    founded_date = Column(DateTime, nullable=True)
    disbanded_date = Column(DateTime, nullable=True)
    logo_url = Column(String(255), nullable=True)
    color_code = Column(String(7), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # リレーションシップ
    politicians = relationship(
        "Politician", back_populates="current_party"
    )
    party_details = relationship(
        "PartyDetail", back_populates="party", 
        uselist=False, cascade="all, delete-orphan"
    )
    politician_parties = relationship(
        "PoliticianParty", back_populates="party", 
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Party {self.name}>"


class PartyDetail(Base):
    """
    政党詳細モデル
    """
    __tablename__ = "party_details"

    party_id = Column(
        CHAR(36),
        ForeignKey("parties.id", ondelete="CASCADE"),
        primary_key=True
    )
    president_id = Column(
        CHAR(36),
        ForeignKey("politicians.id", ondelete="SET NULL"),
        nullable=True
    )
    headquarters = Column(String(255), nullable=True)
    ideology = Column(Text, nullable=True)  # JSON形式で保存
    website_url = Column(String(255), nullable=True)
    social_media = Column(Text, nullable=True)  # JSON形式で保存
    history = Column(Text, nullable=True)  # JSON形式で保存
    additional_info = Column(Text, nullable=True)  # JSON形式で保存
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # リレーションシップ
    party = relationship("Party", back_populates="party_details")
    president = relationship("Politician")

    def __repr__(self) -> str:
        return f"<PartyDetail {self.party_id}>"