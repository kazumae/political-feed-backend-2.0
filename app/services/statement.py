from datetime import datetime
from typing import Dict, List, Optional, Union

from app.models.politician import Politician
from app.models.statement import Statement, StatementReaction, StatementTopic
from app.schemas.statement import StatementCreate, StatementUpdate
from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session, joinedload


def get_statement(db: Session, id: str) -> Optional[Statement]:
    """
    IDで発言を取得する
    
    Args:
        db: データベースセッション
        id: 発言ID
        
    Returns:
        発言オブジェクト、存在しない場合はNone
    """
    return db.query(Statement).options(
        joinedload(Statement.politician)
    ).filter(Statement.id == id).first()


def get_statements(
    db: Session, 
    skip: int = 0, 
    limit: int = 20,
    sort: str = "date_desc",
    filter_party: Optional[str] = None,
    filter_topic: Optional[str] = None,
    filter_date_start: Optional[str] = None,
    filter_date_end: Optional[str] = None,
    search: Optional[str] = None
) -> List[Statement]:
    """
    発言一覧を取得する
    
    Args:
        db: データベースセッション
        skip: スキップ数
        limit: 取得上限
        sort: ソート順
        filter_party: 政党IDでフィルタリング
        filter_topic: トピックIDでフィルタリング
        filter_date_start: 開始日でフィルタリング
        filter_date_end: 終了日でフィルタリング
        search: キーワード検索
        
    Returns:
        発言オブジェクトのリスト
    """
    query = db.query(Statement).options(
        joinedload(Statement.politician)
    ).filter(Statement.status == "published")
    
    # 政党でフィルタリング
    if filter_party:
        query = query.join(Politician).filter(Politician.current_party_id == filter_party)
    
    # トピックでフィルタリング
    if filter_topic:
        query = query.join(StatementTopic).filter(StatementTopic.topic_id == filter_topic)
    
    # 日付でフィルタリング
    if filter_date_start:
        try:
            start_date = datetime.strptime(filter_date_start, "%Y-%m-%d")
            query = query.filter(Statement.statement_date >= start_date)
        except ValueError:
            pass
    
    if filter_date_end:
        try:
            end_date = datetime.strptime(filter_date_end, "%Y-%m-%d")
            query = query.filter(Statement.statement_date <= end_date)
        except ValueError:
            pass
    
    # キーワード検索
    if search:
        query = query.filter(
            or_(
                Statement.title.ilike(f"%{search}%"),
                Statement.content.ilike(f"%{search}%")
            )
        )
    
    # ソート
    if sort == "date_desc":
        query = query.order_by(Statement.statement_date.desc())
    elif sort == "date_asc":
        query = query.order_by(Statement.statement_date.asc())
    elif sort == "likes":
        query = query.order_by(Statement.likes_count.desc())
    else:
        query = query.order_by(Statement.statement_date.desc())
    
    return query.offset(skip).limit(limit).all()


def count_statements(
    db: Session,
    filter_party: Optional[str] = None,
    filter_topic: Optional[str] = None,
    filter_date_start: Optional[str] = None,
    filter_date_end: Optional[str] = None,
    search: Optional[str] = None
) -> int:
    """
    発言数を取得する
    
    Args:
        db: データベースセッション
        filter_party: 政党IDでフィルタリング
        filter_topic: トピックIDでフィルタリング
        filter_date_start: 開始日でフィルタリング
        filter_date_end: 終了日でフィルタリング
        search: キーワード検索
        
    Returns:
        発言数
    """
    query = db.query(func.count(Statement.id)).filter(Statement.status == "published")
    
    # 政党でフィルタリング
    if filter_party:
        query = query.join(Politician).filter(Politician.current_party_id == filter_party)
    
    # トピックでフィルタリング
    if filter_topic:
        query = query.join(StatementTopic).filter(StatementTopic.topic_id == filter_topic)
    
    # 日付でフィルタリング
    if filter_date_start:
        try:
            start_date = datetime.strptime(filter_date_start, "%Y-%m-%d")
            query = query.filter(Statement.statement_date >= start_date)
        except ValueError:
            pass
    
    if filter_date_end:
        try:
            end_date = datetime.strptime(filter_date_end, "%Y-%m-%d")
            query = query.filter(Statement.statement_date <= end_date)
        except ValueError:
            pass
    
    # キーワード検索
    if search:
        query = query.filter(
            or_(
                Statement.title.ilike(f"%{search}%"),
                Statement.content.ilike(f"%{search}%")
            )
        )
    
    return query.scalar() or 0


def get_statements_by_politician(
    db: Session, 
    politician_id: str,
    skip: int = 0, 
    limit: int = 20,
    sort: str = "date_desc"
) -> List[Statement]:
    """
    特定の政治家の発言一覧を取得する
    
    Args:
        db: データベースセッション
        politician_id: 政治家ID
        skip: スキップ数
        limit: 取得上限
        sort: ソート順
        
    Returns:
        発言オブジェクトのリスト
    """
    query = db.query(Statement).options(
        joinedload(Statement.politician)
    ).filter(
        Statement.politician_id == politician_id,
        Statement.status == "published"
    )
    
    # ソート
    if sort == "date_desc":
        query = query.order_by(Statement.statement_date.desc())
    elif sort == "date_asc":
        query = query.order_by(Statement.statement_date.asc())
    elif sort == "likes":
        query = query.order_by(Statement.likes_count.desc())
    else:
        query = query.order_by(Statement.statement_date.desc())
    
    return query.offset(skip).limit(limit).all()


def count_statements_by_politician(
    db: Session,
    politician_id: str
) -> int:
    """
    特定の政治家の発言数を取得する
    
    Args:
        db: データベースセッション
        politician_id: 政治家ID
        
    Returns:
        発言数
    """
    return db.query(func.count(Statement.id)).filter(
        Statement.politician_id == politician_id,
        Statement.status == "published"
    ).scalar() or 0


def get_statements_by_politicians(
    db: Session, 
    politician_ids: List[str],
    skip: int = 0, 
    limit: int = 20,
    sort: str = "date_desc"
) -> List[Statement]:
    """
    複数の政治家の発言一覧を取得する
    
    Args:
        db: データベースセッション
        politician_ids: 政治家IDのリスト
        skip: スキップ数
        limit: 取得上限
        sort: ソート順
        
    Returns:
        発言オブジェクトのリスト
    """
    query = db.query(Statement).options(
        joinedload(Statement.politician)
    ).filter(
        Statement.politician_id.in_(politician_ids),
        Statement.status == "published"
    )
    
    # ソート
    if sort == "date_desc":
        query = query.order_by(Statement.statement_date.desc())
    elif sort == "date_asc":
        query = query.order_by(Statement.statement_date.asc())
    elif sort == "likes":
        query = query.order_by(Statement.likes_count.desc())
    else:
        query = query.order_by(Statement.statement_date.desc())
    
    return query.offset(skip).limit(limit).all()


def count_statements_by_politicians(
    db: Session,
    politician_ids: List[str]
) -> int:
    """
    複数の政治家の発言数を取得する
    
    Args:
        db: データベースセッション
        politician_ids: 政治家IDのリスト
        
    Returns:
        発言数
    """
    return db.query(func.count(Statement.id)).filter(
        Statement.politician_id.in_(politician_ids),
        Statement.status == "published"
    ).scalar() or 0


def get_statements_by_party(
    db: Session, 
    party_id: str,
    skip: int = 0, 
    limit: int = 20,
    sort: str = "date_desc"
) -> List[Statement]:
    """
    特定の政党の発言一覧を取得する
    
    Args:
        db: データベースセッション
        party_id: 政党ID
        skip: スキップ数
        limit: 取得上限
        sort: ソート順
        
    Returns:
        発言オブジェクトのリスト
    """
    query = db.query(Statement).options(
        joinedload(Statement.politician)
    ).join(Politician).filter(
        Politician.current_party_id == party_id,
        Statement.status == "published"
    )
    
    # ソート
    if sort == "date_desc":
        query = query.order_by(Statement.statement_date.desc())
    elif sort == "date_asc":
        query = query.order_by(Statement.statement_date.asc())
    elif sort == "likes":
        query = query.order_by(Statement.likes_count.desc())
    else:
        query = query.order_by(Statement.statement_date.desc())
    
    return query.offset(skip).limit(limit).all()


def count_statements_by_party(
    db: Session,
    party_id: str
) -> int:
    """
    特定の政党の発言数を取得する
    
    Args:
        db: データベースセッション
        party_id: 政党ID
        
    Returns:
        発言数
    """
    return db.query(func.count(Statement.id)).join(Politician).filter(
        Politician.current_party_id == party_id,
        Statement.status == "published"
    ).scalar() or 0


def get_statements_by_topic(
    db: Session, 
    topic_id: str,
    skip: int = 0, 
    limit: int = 20,
    sort: str = "date_desc"
) -> List[Statement]:
    """
    特定のトピックの発言一覧を取得する
    
    Args:
        db: データベースセッション
        topic_id: トピックID
        skip: スキップ数
        limit: 取得上限
        sort: ソート順
        
    Returns:
        発言オブジェクトのリスト
    """
    query = db.query(Statement).options(
        joinedload(Statement.politician)
    ).join(StatementTopic).filter(
        StatementTopic.topic_id == topic_id,
        Statement.status == "published"
    )
    
    # ソート
    if sort == "date_desc":
        query = query.order_by(Statement.statement_date.desc())
    elif sort == "date_asc":
        query = query.order_by(Statement.statement_date.asc())
    elif sort == "likes":
        query = query.order_by(Statement.likes_count.desc())
    else:
        query = query.order_by(Statement.statement_date.desc())
    
    return query.offset(skip).limit(limit).all()


def count_statements_by_topic(
    db: Session,
    topic_id: str
) -> int:
    """
    特定のトピックの発言数を取得する
    
    Args:
        db: データベースセッション
        topic_id: トピックID
        
    Returns:
        発言数
    """
    return db.query(func.count(Statement.id)).join(StatementTopic).filter(
        StatementTopic.topic_id == topic_id,
        Statement.status == "published"
    ).scalar() or 0


def create_statement(
    db: Session, obj_in: StatementCreate
) -> Statement:
    """
    新規発言を作成する
    
    Args:
        db: データベースセッション
        obj_in: 発言作成スキーマ
        
    Returns:
        作成された発言オブジェクト
    """
    # 政治家情報を取得
    politician = db.query(Politician).get(obj_in.politician_id)
    
    db_obj = Statement(
        politician_id=obj_in.politician_id,
        title=obj_in.title,
        content=obj_in.content,
        source=obj_in.source,
        source_url=obj_in.source_url,
        statement_date=obj_in.statement_date,
        context=obj_in.context,
        status=obj_in.status or "published",
        importance=obj_in.importance or 0,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    
    # トピックを関連付ける
    if obj_in.topic_ids:
        for topic_id in obj_in.topic_ids:
            statement_topic = StatementTopic(
                statement_id=db_obj.id,
                topic_id=topic_id,
                relevance=50  # デフォルト値
            )
            db.add(statement_topic)
        db.commit()
    
    return db_obj


def update_statement(
    db: Session, 
    *, 
    db_obj: Statement, 
    obj_in: Union[StatementUpdate, Dict[str, any]]
) -> Statement:
    """
    発言情報を更新する
    
    Args:
        db: データベースセッション
        db_obj: 更新対象の発言オブジェクト
        obj_in: 更新データ（StatementUpdateオブジェクトまたは辞書）
        
    Returns:
        更新された発言オブジェクト
    """
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.model_dump(exclude_unset=True)
    
    # トピックIDを取り出す
    topic_ids = None
    if "topic_ids" in update_data:
        topic_ids = update_data.pop("topic_ids", None)
    
    # 基本情報を更新
    for field in update_data:
        if field in update_data:
            setattr(db_obj, field, update_data[field])
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    
    # トピックを更新
    if topic_ids is not None:
        # 既存のトピック関連を削除
        db.query(StatementTopic).filter(
            StatementTopic.statement_id == db_obj.id
        ).delete()
        
        # 新しいトピック関連を追加
        for topic_id in topic_ids:
            statement_topic = StatementTopic(
                statement_id=db_obj.id,
                topic_id=topic_id,
                relevance=50  # デフォルト値
            )
            db.add(statement_topic)
        
        db.commit()
    
    return db_obj


def delete_statement(db: Session, *, id: str) -> Statement:
    """
    発言を削除する
    
    Args:
        db: データベースセッション
        id: 発言ID
        
    Returns:
        削除された発言オブジェクト
    """
    obj = db.query(Statement).get(id)
    db.delete(obj)
    db.commit()
    return obj


def get_statement_topics(
    db: Session, statement_id: str
) -> List[Dict]:
    """
    発言に関連するトピック一覧を取得する
    
    Args:
        db: データベースセッション
        statement_id: 発言ID
        
    Returns:
        トピック情報のリスト
    """
    from app.models.topic import Topic
    
    statement_topics = db.query(StatementTopic).filter(
        StatementTopic.statement_id == statement_id
    ).all()
    
    result = []
    for st in statement_topics:
        topic = db.query(Topic).get(st.topic_id)
        if topic:
            result.append({
                "id": topic.id,
                "name": topic.name,
                "slug": topic.slug,
                "category": topic.category,
                "relevance": st.relevance
            })
    
    return result


def get_statement_likes_count(db: Session, *, statement_id: str) -> int:
    """
    発言のいいね数を取得する
    
    Args:
        db: データベースセッション
        statement_id: 発言ID
        
    Returns:
        いいね数
    """
    return db.query(func.count(StatementReaction.id)).filter(
        StatementReaction.statement_id == statement_id,
        StatementReaction.reaction_type == "like"
    ).scalar() or 0


def update_statement_likes_count(db: Session, *, statement_id: str) -> None:
    """
    発言のいいね数を更新する
    
    Args:
        db: データベースセッション
        statement_id: 発言ID
    """
    likes_count = get_statement_likes_count(db, statement_id=statement_id)
    
    statement = db.query(Statement).get(statement_id)
    if statement:
        statement.likes_count = likes_count
        db.add(statement)
        db.commit()


def is_statement_liked(db: Session, *, statement_id: str, user_id: str) -> bool:
    """
    ユーザーが発言にいいねしているかどうかを確認する
    
    Args:
        db: データベースセッション
        statement_id: 発言ID
        user_id: ユーザーID
        
    Returns:
        いいねしている場合はTrue、していない場合はFalse
    """
    reaction = db.query(StatementReaction).filter(
        StatementReaction.statement_id == statement_id,
        StatementReaction.user_id == user_id,
        StatementReaction.reaction_type == "like"
    ).first()
    return reaction is not None


def get_statement_comments_count(db: Session, *, statement_id: str) -> int:
    """
    発言のコメント数を取得する
    
    Args:
        db: データベースセッション
        statement_id: 発言ID
        
    Returns:
        コメント数
    """
    from app.models.comment import Comment
    
    return db.query(func.count(Comment.id)).filter(
        Comment.statement_id == statement_id,
        Comment.status == "published"
    ).scalar() or 0


def update_statement_comments_count(db: Session, *, statement_id: str) -> None:
    """
    発言のコメント数を更新する
    
    Args:
        db: データベースセッション
        statement_id: 発言ID
    """
    comments_count = get_statement_comments_count(db, statement_id=statement_id)
    
    statement = db.query(Statement).get(statement_id)
    if statement:
        statement.comments_count = comments_count
        db.add(statement)
        db.commit()