from datetime import datetime

from app.db.session import Base
from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship


class UserSettings(Base):
    """
    ユーザー設定モデル
    """
    __tablename__ = "user_settings"

    user_id = Column(
        CHAR(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )
    notification_email = Column(Boolean, default=True, nullable=False)
    notification_web = Column(Boolean, default=True, nullable=False)
    theme = Column(String(20), default="light", nullable=False)
    feed_preference = Column(Text, nullable=True)  # JSON形式で保存
    language = Column(String(10), default="ja", nullable=False)
    privacy_level = Column(
        Enum("public", "private", name="privacy_level"),
        default="public",
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
    user = relationship("User", backref="settings")

    def __repr__(self) -> str:
        return f"<UserSettings {self.user_id}>"