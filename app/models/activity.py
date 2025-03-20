import uuid
from datetime import datetime

from app.db.session import Base
from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship


class UserActivity(Base):
    """
    ユーザーアクティビティモデル
    """
    __tablename__ = "user_activities"

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
    activity_type = Column(
        Enum(
            "view", "like", "comment", "follow", "search",
            name="activity_type"
        ),
        nullable=False
    )
    target_type = Column(
        Enum(
            "statement", "politician", "party", "topic", "comment",
            name="activity_target_type"
        ),
        nullable=False
    )
    target_id = Column(CHAR(36), nullable=False)
    activity_metadata = Column(Text, nullable=True)  # JSON形式で保存
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # リレーションシップ
    user = relationship("User")

    def __repr__(self) -> str:
        return f"<UserActivity {self.activity_type} on {self.target_type}>"


class Notification(Base):
    """
    通知モデル
    """
    __tablename__ = "notifications"

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
    type = Column(
        Enum(
            "comment_reply", "like", "follow", "system", "mention",
            name="notification_type"
        ),
        nullable=False
    )
    actor_id = Column(
        CHAR(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    target_type = Column(
        Enum(
            "statement", "comment", "politician", "topic",
            name="notification_target_type"
        ),
        nullable=False
    )
    target_id = Column(CHAR(36), nullable=False)
    message = Column(String(255), nullable=False)
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    notification_metadata = Column(Text, nullable=True)  # JSON形式で保存
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # リレーションシップ
    user = relationship("User", foreign_keys=[user_id])
    actor = relationship("User", foreign_keys=[actor_id])

    def __repr__(self) -> str:
        return f"<Notification {self.type} to {self.user_id}>"