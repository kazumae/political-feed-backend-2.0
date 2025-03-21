import uuid
from datetime import datetime

from app.db.session import Base
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship


class Comment(Base):
    """
    コメントモデル
    """
    __tablename__ = "comments"

    id = Column(
        CHAR(36),
        primary_key=True,
        index=True,
        default=lambda: str(uuid.uuid4())
    )
    user_id = Column(
        CHAR(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    statement_id = Column(
        CHAR(36),
        ForeignKey("statements.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    parent_id = Column(
        CHAR(36),
        ForeignKey("comments.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )
    content = Column(Text, nullable=False)
    status = Column(
        Enum("published", "hidden", "deleted", name="comment_status"),
        default="published",
        nullable=False,
        index=True
    )
    likes_count = Column(Integer, default=0, nullable=False)
    replies_count = Column(Integer, default=0, nullable=False)
    reports_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # リレーションシップ
    user = relationship("User")
    statement = relationship("Statement", back_populates="comments")
    parent = relationship(
        "Comment", remote_side=[id], backref="replies"
    )
    reactions = relationship(
        "CommentReaction", back_populates="comment", 
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Comment {self.id}>"


class CommentReaction(Base):
    """
    コメントへのリアクションモデル
    """
    __tablename__ = "comment_reactions"

    id = Column(
        CHAR(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    comment_id = Column(
        CHAR(36),
        ForeignKey("comments.id", ondelete="CASCADE"),
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
            name="comment_reaction_type"
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
    comment = relationship("Comment", back_populates="reactions")
    user = relationship("User")

    def __repr__(self) -> str:
        return f"<CommentReaction {self.reaction_type}>"