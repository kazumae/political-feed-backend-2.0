import uuid
from datetime import datetime

from app.db.session import Base
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Text
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship


class CommentReport(Base):
    """
    コメント通報モデル
    """
    __tablename__ = "comment_reports"

    id = Column(
        CHAR(36),
        primary_key=True,
        index=True,
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
    reason = Column(
        Enum(
            "spam", "hate_speech", "inappropriate", "misinformation", "other",
            name="report_reason"
        ),
        nullable=False
    )
    details = Column(Text, nullable=True)
    status = Column(
        Enum(
            "pending", "reviewed", "actioned", "dismissed",
            name="report_status"
        ),
        default="pending",
        nullable=False,
        index=True
    )
    admin_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # リレーションシップ
    comment = relationship("Comment")
    user = relationship("User")

    def __repr__(self) -> str:
        return f"<CommentReport {self.id}>"