from app.core.config import settings
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLAlchemyエンジンの作成
engine = create_engine(str(settings.DATABASE_URL), pool_pre_ping=True)

# セッションファクトリの作成
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# モデルのベースクラス
Base = declarative_base()


# 依存性注入用のセッション取得関数
def get_db():
    """
    リクエストごとにデータベースセッションを取得し、リクエスト完了後にクローズする
    FastAPIの依存性注入システムで使用される
    
    Yields:
        SQLAlchemy DBセッション
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()