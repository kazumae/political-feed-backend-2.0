import logging
from datetime import datetime
from typing import Dict, List, Optional

from app.db.session import SessionLocal
from app.models.data_collection import DataCollectionLog, DataCollectionSource
from app.tasks.base import BaseTask
from app.tasks.worker import celery_app
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class DataCollectionTask(BaseTask):
    """
    データ収集タスクの基底クラス
    """
    abstract = True


@celery_app.task(
    bind=True,
    base=DataCollectionTask,
    name="app.tasks.data_collection.collect_data",
    queue="low_priority",
)
def collect_data(self) -> Dict[str, int]:
    """
    データ収集のメインタスク
    
    Returns:
        収集結果の統計情報
    """
    logger.info("データ収集タスクを開始します")
    start_time = datetime.utcnow()
    
    # 収集結果の統計情報
    stats = {
        "total_sources": 0,
        "processed_sources": 0,
        "total_items": 0,
        "new_items": 0,
        "updated_items": 0,
        "failed_sources": 0,
    }
    
    try:
        # データベースセッションの作成
        db = SessionLocal()
        try:
            # アクティブなデータソースを取得
            sources = get_active_sources(db)
            stats["total_sources"] = len(sources)
            
            # 各ソースからデータを収集
            for source in sources:
                try:
                    source_stats = process_source(db, source)
                    stats["processed_sources"] += 1
                    stats["total_items"] += source_stats.get("total_items", 0)
                    stats["new_items"] += source_stats.get("new_items", 0)
                    stats["updated_items"] += source_stats.get(
                        "updated_items", 0)
                    
                    # 収集ログの記録
                    log_collection_result(
                        db, 
                        source.id, 
                        "success", 
                        source_stats.get("total_items", 0),
                        source_stats.get("processed_items", 0),
                        None,
                        source_stats
                    )
                    
                except Exception as e:
                    logger.error(
                        f"ソース '{source.name}' からのデータ収集中にエラーが発生しました: {e}",
                        exc_info=True
                    )
                    stats["failed_sources"] += 1
                    
                    # エラーログの記録
                    log_collection_result(
                        db, 
                        source.id, 
                        "failed", 
                        0, 
                        0, 
                        str(e),
                        None
                    )
        finally:
            db.close()
        
        # 処理時間の計算
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        logger.info(
            f"データ収集タスクが完了しました（所要時間: {duration:.2f}秒）"
            f" - 処理ソース数: "
            f"{stats['processed_sources']}/{stats['total_sources']},"
            f" 新規アイテム: {stats['new_items']},"
            f" 更新アイテム: {stats['updated_items']}"
        )
        
        return stats
    
    except Exception as e:
        logger.error(f"データ収集中にエラーが発生しました: {e}", exc_info=True)
        stats["failed_sources"] += 1
        raise


def get_active_sources(db: Session) -> List[DataCollectionSource]:
    """
    アクティブなデータ収集ソースを取得
    
    Args:
        db: データベースセッション
        
    Returns:
        アクティブなデータ収集ソースのリスト
    """
    return db.query(DataCollectionSource).filter(
        DataCollectionSource.is_active == True  # noqa: E712
    ).all()


def process_source(
    db: Session,
    source: DataCollectionSource
) -> Dict[str, int]:
    """
    特定のソースからデータを収集して処理
    
    Args:
        db: データベースセッション
        source: データ収集ソース
        
    Returns:
        処理結果の統計情報
    """
    logger.info(f"ソース '{source.name}' からデータ収集を開始します")
    
    # 現在は実装されていないため、ダミーの結果を返す
    # 実際の実装では、ソースタイプに応じた収集処理を行う
    result = {
        "total_items": 0,
        "processed_items": 0,
        "new_items": 0,
        "updated_items": 0,
    }
    
    # ソースの最終実行時間を更新
    source.last_run_at = datetime.utcnow()
    db.commit()
    
    logger.info(f"ソース '{source.name}' からのデータ収集が完了しました")
    return result


def log_collection_result(
    db: Session,
    source_id: str,
    status: str,
    items_found: int,
    items_processed: int,
    error_message: Optional[str] = None,
    details: Optional[Dict] = None
) -> None:
    """
    データ収集結果をログに記録
    
    Args:
        db: データベースセッション
        source_id: データ収集ソースID
        status: 実行結果ステータス
        items_found: 発見アイテム数
        items_processed: 処理アイテム数
        error_message: エラーメッセージ
        details: 詳細情報
    """
    started_at = datetime.utcnow()
    
    log = DataCollectionLog(
        source_id=source_id,
        status=status,
        items_found=items_found,
        items_processed=items_processed,
        error_message=error_message,
        details=str(details) if details else None,
        started_at=started_at,
        completed_at=datetime.utcnow()
    )
    
    db.add(log)
    db.commit()