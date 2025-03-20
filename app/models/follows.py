from datetime import datetime

from app.db.session import Base
from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship


class PoliticianFollow(Base):
    """
    政治家フォローモデル
    """
    __tablename__ = "politician_follows"

    politician_id = Column(
        CHAR(36),
        ForeignKey("politicians.id", ondelete="CASCADE"),
        primary_key=True
    )
    user_id = Column(
        CHAR(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # リレーションシップ
    politician = relationship("Politician")
    user = relationship("User")

    def __repr__(self) -> str:
        return f"<PoliticianFollow {self.user_id} -> {self.politician_id}>"


class TopicFollow(Base):
    """
    トピックフォローモデル
    """
    __tablename__ = "topic_follows"

    topic_id = Column(
        CHAR(36),
        ForeignKey("topics.id", ondelete="CASCADE"),
        primary_key=True
    )
    user_id = Column(
        CHAR(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # リレーションシップ
    topic = relationship("Topic")
    user = relationship("User")

    def __repr__(self) -> str:
        return f"<TopicFollow {self.user_id} -> {self.topic_id}>"