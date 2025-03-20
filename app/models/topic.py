import uuid
from datetime import datetime

from app.db.session import Base
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship


class Topic(Base):
    """
    政策トピックモデル
    """
    __tablename__ = "topics"

    id = Column(
        CHAR(36),
        primary_key=True,
        index=True,
        default=lambda: str(uuid.uuid4())
    )
    name = Column(String(100), nullable=False, unique=True, index=True)
    slug = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    category = Column(
        Enum(
            "economy", "foreign_policy", "security", "environment", 
            "education", "healthcare", "social_welfare", "infrastructure",
            "technology", "agriculture", "energy", "other",
            name="topic_category"
        ),
        nullable=False,
        index=True
    )
    importance = Column(
        Integer, default=50, nullable=False, index=True
    )  # 重要度（0-100）
    icon_url = Column(String(255), nullable=True)
    color_code = Column(String(7), nullable=True)
    status = Column(
        Enum("active", "inactive", name="topic_status"),
        default="active",
        nullable=False,
        index=True
    )
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # リレーションシップ
    statements = relationship(
        "Statement", secondary="statement_topics", back_populates="topics"
    )
    parent_relations = relationship(
        "TopicRelation", 
        foreign_keys="TopicRelation.child_topic_id",
        back_populates="child_topic",
        cascade="all, delete-orphan"
    )
    child_relations = relationship(
        "TopicRelation", 
        foreign_keys="TopicRelation.parent_topic_id",
        back_populates="parent_topic",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Topic {self.name}>"


class TopicRelation(Base):
    """
    トピック間の関連モデル
    """
    __tablename__ = "topic_relations"

    parent_topic_id = Column(
        CHAR(36),
        ForeignKey("topics.id", ondelete="CASCADE"),
        primary_key=True
    )
    child_topic_id = Column(
        CHAR(36),
        ForeignKey("topics.id", ondelete="CASCADE"),
        primary_key=True
    )
    relation_type = Column(
        Enum(
            "parent_child", "related", "opposite", 
            name="topic_relation_type"
        ),
        nullable=False
    )
    strength = Column(
        Integer, default=50, nullable=False
    )  # 関連の強さ（0-100）
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # リレーションシップ
    parent_topic = relationship(
        "Topic", foreign_keys=[parent_topic_id], 
        back_populates="child_relations"
    )
    child_topic = relationship(
        "Topic", foreign_keys=[child_topic_id], 
        back_populates="parent_relations"
    )

    def __repr__(self) -> str:
        return f"<TopicRelation {self.relation_type}>"