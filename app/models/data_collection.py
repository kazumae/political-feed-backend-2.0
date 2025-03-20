import uuid
from datetime import datetime

from app.db.session import Base
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship


class DataCollectionSource(Base):
    """
    データ収集ソースモデル
    """
    __tablename__ = "data_collection_sources"

    id = Column(
        CHAR(36),
        primary_key=True,
        index=True,
        default=lambda: str(uuid.uuid4())
    )
    name = Column(String(100), nullable=False, unique=True, index=True)
    source_type = Column(
        Enum(
            "website", "api", "rss", "social_media", "manual",
            name="source_type"
        ),
        nullable=False
    )
    url = Column(String(2083), nullable=True)
    config = Column(Text, nullable=True)  # JSON形式で保存
    credentials = Column(Text, nullable=True)  # JSON形式で保存（暗号化）
    schedule = Column(String(50), nullable=True)  # cron形式
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    last_run_at = Column(DateTime, nullable=True)
    next_run_at = Column(DateTime, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # リレーションシップ
    logs = relationship(
        "DataCollectionLog", back_populates="source", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<DataCollectionSource {self.name}>"


class DataCollectionLog(Base):
    """
    データ収集ログモデル
    """
    __tablename__ = "data_collection_logs"

    id = Column(
        CHAR(36),
        primary_key=True,
        index=True,
        default=lambda: str(uuid.uuid4())
    )
    source_id = Column(
        CHAR(36),
        ForeignKey("data_collection_sources.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    status = Column(
        Enum("success", "partial", "failed", name="log_status"),
        nullable=False,
        index=True
    )
    items_found = Column(Integer, nullable=True)
    items_processed = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    details = Column(Text, nullable=True)  # JSON形式で保存
    duration_ms = Column(Integer, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    completed_at = Column(DateTime, nullable=True)

    # リレーションシップ
    source = relationship("DataCollectionSource", back_populates="logs")

    def __repr__(self) -> str:
        return f"<DataCollectionLog {self.id}>"


class SystemLog(Base):
    """
    システムログモデル
    """
    __tablename__ = "system_logs"

    id = Column(
        CHAR(36),
        primary_key=True,
        index=True,
        default=lambda: str(uuid.uuid4())
    )
    level = Column(
        Enum("info", "warning", "error", "critical", name="log_level"),
        nullable=False,
        index=True
    )
    service = Column(String(50), nullable=False, index=True)
    message = Column(Text, nullable=False)
    context = Column(Text, nullable=True)  # JSON形式で保存
    user_id = Column(
        CHAR(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # リレーションシップ
    user = relationship("User")

    def __repr__(self) -> str:
        return f"<SystemLog {self.level}: {self.service}>"