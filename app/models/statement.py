import uuid
from datetime import datetime

from app.db.session import Base
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship


class Statement(Base):
    """
    政治家発言モデル
    """
    __tablename__ = "statements"

    id = Column(
        CHAR(36),
        primary_key=True,
        index=True,
        default=lambda: str(uuid.uuid4())
    )
    politician_id = Column(
        CHAR(36),
        ForeignKey("politicians.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    title = Column(String(255), nullable=False, index=True)
    content = Column(Text, nullable=False)
    source = Column(String(255), nullable=True)
    source_url = Column(String(255), nullable=True)
    statement_date = Column(DateTime, nullable=False, index=True)
    context = Column(Text, nullable=True)
    status = Column(
        Enum("published", "draft", "archived", name="statement_status"),
        default="published",
        nullable=False,
        index=True
    )
    importance = Column(
        Integer, default=0, nullable=False, index=True
    )  # 重要度（0-100）
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # リレーションシップ
    politician = relationship("Politician", back_populates="statements")
    topics = relationship(
        "Topic", secondary="statement_topics", back_populates="statements"
    )
    comments = relationship(
        "Comment", back_populates="statement", cascade="all, delete-orphan"
    )
    reactions = relationship(
        "StatementReaction", back_populates="statement", 
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Statement {self.title}>"


class StatementTopic(Base):
    """
    発言とトピックの中間テーブル
    """
    __tablename__ = "statement_topics"

    statement_id = Column(
        CHAR(36),
        ForeignKey("statements.id", ondelete="CASCADE"),
        primary_key=True
    )
    topic_id = Column(
        CHAR(36),
        ForeignKey("topics.id", ondelete="CASCADE"),
        primary_key=True
    )
    relevance = Column(Integer, default=50, nullable=False)  # 関連度（0-100）
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<StatementTopic {self.statement_id} - {self.topic_id}>"


class StatementReaction(Base):
    """
    発言へのリアクションモデル
    """
    __tablename__ = "statement_reactions"

    id = Column(
        CHAR(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    statement_id = Column(
        CHAR(36),
        ForeignKey("statements.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    user_id = Column(
        CHAR(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    reaction_type = Column(
        Enum(
            "like", "dislike", "agree", "disagree", 
            "important", "fake", name="reaction_type"
        ),
        nullable=False
    )
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # リレーションシップ
    statement = relationship("Statement", back_populates="reactions")
    user = relationship("User")

    def __repr__(self) -> str:
        return f"<StatementReaction {self.reaction_type}>"