import logging

from app.core.config import settings
from app.db.session import Base, engine
from app.models import comment, party, politician, statement, topic, user
from sqlalchemy.orm import Session

# ロガーの設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db() -> None:
    """
    データベースの初期化を行う
    テーブルの作成と初期データの投入
    """
    try:
        # テーブルの作成
        # SQLAlchemyのモデルからテーブルを作成
        Base.metadata.create_all(bind=engine)
        logger.info("データベーステーブルが正常に作成されました")
        
        # 初期データの投入は必要に応じてここに実装
        # init_data()
        
    except Exception as e:
        logger.error(f"データベースの初期化中にエラーが発生しました: {e}")
        raise


def init_data(db: Session) -> None:
    """
    初期データを投入する
    
    Args:
        db: データベースセッション
    """
    # 初期データの投入処理を実装
    # 例: 管理者ユーザーの作成、初期政党データの投入など
    pass


if __name__ == "__main__":
    logger.info("データベースの初期化を開始します")
    init_db()
    logger.info("データベースの初期化が完了しました")