import uuid
from datetime import datetime

from app.db.session import Base
from sqlalchemy import Boolean, Column, DateTime, Enum, String
from sqlalchemy.dialects.mysql import CHAR


class User(Base):
    """
    ユーザーモデル
    """
    __tablename__ = "users"

    id = Column(
        CHAR(36),
        primary_key=True,
        index=True,
        default=lambda: str(uuid.uuid4())
    )
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(
        Enum("user", "moderator", "admin", name="user_role"),
        default="user",
        nullable=False
    )
    status = Column(
        Enum("active", "suspended", "inactive", name="user_status"),
        default="active",
        nullable=False,
        index=True
    )
    email_verified = Column(Boolean, default=False, nullable=False)
    profile_image = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    last_login_at = Column(DateTime, nullable=True)

    # プロパティ
    @property
    def is_active(self) -> bool:
        """ユーザーがアクティブかどうか"""
        return self.status == "active"

    @property
    def is_superuser(self) -> bool:
        """ユーザーが管理者かどうか"""
        return self.role == "admin"

    @property
    def is_moderator(self) -> bool:
        """ユーザーがモデレーターかどうか"""
        return self.role in ["admin", "moderator"]

    def __repr__(self) -> str:
        return f"<User {self.username}>"