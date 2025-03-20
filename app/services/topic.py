from typing import Dict, List, Optional, Union

from app.models.follows import TopicFollow
from app.models.topic import Topic, TopicRelation
from app.schemas.topic import TopicCreate, TopicUpdate
from sqlalchemy import func
from sqlalchemy.orm import Session


def get_topic(db: Session, id: str) -> Optional[Topic]:
    """
    IDでトピックを取得する
    
    Args:
        db: データベースセッション
        id: トピックID
        
    Returns:
        トピックオブジェクト、存在しない場合はNone
    """
    return db.query(Topic).filter(Topic.id == id).first()


def get_topic_by_slug(db: Session, slug: str) -> Optional[Topic]:
    """
    スラッグでトピックを取得する
    
    Args:
        db: データベースセッション
        slug: トピックスラッグ
        
    Returns:
        トピックオブジェクト、存在しない場合はNone
    """
    return db.query(Topic).filter(Topic.slug == slug).first()


def get_topics(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    status: Optional[str] = None,
    search: Optional[str] = None
) -> List[Topic]:
    """
    トピック一覧を取得する
    
    Args:
        db: データベースセッション
        skip: スキップ数
        limit: 取得上限
        status: ステータスでフィルタリング
        search: 名前で検索
        
    Returns:
        トピックオブジェクトのリスト
    """
    query = db.query(Topic)
    
    if status:
        query = query.filter(Topic.status == status)
    
    if search:
        query = query.filter(
            Topic.name.ilike(f"%{search}%") | 
            Topic.slug.ilike(f"%{search}%")
        )
    
    return query.order_by(Topic.importance.desc()).offset(skip).limit(limit).all()


def create_topic(
    db: Session, obj_in: TopicCreate
) -> Topic:
    """
    新規トピックを作成する
    
    Args:
        db: データベースセッション
        obj_in: トピック作成スキーマ
        
    Returns:
        作成されたトピックオブジェクト
    """
    db_obj = Topic(
        name=obj_in.name,
        slug=obj_in.slug,
        description=obj_in.description,
        category=obj_in.category,
        importance=obj_in.importance or 50,
        icon_url=obj_in.icon_url,
        color_code=obj_in.color_code,
        status=obj_in.status,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_topic(
    db: Session, 
    *, 
    db_obj: Topic, 
    obj_in: Union[TopicUpdate, Dict[str, any]]
) -> Topic:
    """
    トピック情報を更新する
    
    Args:
        db: データベースセッション
        db_obj: 更新対象のトピックオブジェクト
        obj_in: 更新データ（TopicUpdateオブジェクトまたは辞書）
        
    Returns:
        更新されたトピックオブジェクト
    """
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.model_dump(exclude_unset=True)
    
    for field in update_data:
        if field in update_data:
            setattr(db_obj, field, update_data[field])
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_topic(db: Session, *, id: str) -> Topic:
    """
    トピックを削除する
    
    Args:
        db: データベースセッション
        id: トピックID
        
    Returns:
        削除されたトピックオブジェクト
    """
    obj = db.query(Topic).get(id)
    db.delete(obj)
    db.commit()
    return obj


def get_related_topics(
    db: Session, topic_id: str
) -> List[Dict]:
    """
    関連トピック一覧を取得する
    
    Args:
        db: データベースセッション
        topic_id: トピックID
        
    Returns:
        関連トピック情報のリスト
    """
    # 親トピックの関連を取得
    parent_relations = db.query(TopicRelation).filter(
        TopicRelation.child_topic_id == topic_id
    ).all()
    
    # 子トピックの関連を取得
    child_relations = db.query(TopicRelation).filter(
        TopicRelation.parent_topic_id == topic_id
    ).all()
    
    result = []
    
    # 親トピックの情報を追加
    for relation in parent_relations:
        parent_topic = db.query(Topic).get(relation.parent_topic_id)
        if parent_topic:
            result.append({
                "id": parent_topic.id,
                "name": parent_topic.name,
                "slug": parent_topic.slug,
                "relation_type": relation.relation_type,
                "strength": relation.strength
            })
    
    # 子トピックの情報を追加
    for relation in child_relations:
        child_topic = db.query(Topic).get(relation.child_topic_id)
        if child_topic:
            result.append({
                "id": child_topic.id,
                "name": child_topic.name,
                "slug": child_topic.slug,
                "relation_type": relation.relation_type,
                "strength": relation.strength
            })
    
    return result


def get_followers_count(db: Session, *, topic_id: str) -> int:
    """
    トピックのフォロワー数を取得する
    
    Args:
        db: データベースセッション
        topic_id: トピックID
        
    Returns:
        フォロワー数
    """
    return db.query(func.count(TopicFollow.user_id)).filter(
        TopicFollow.topic_id == topic_id
    ).scalar() or 0


def is_following_topic(db: Session, *, topic_id: str, user_id: str) -> bool:
    """
    ユーザーがトピックをフォローしているかどうかを確認する
    
    Args:
        db: データベースセッション
        topic_id: トピックID
        user_id: ユーザーID
        
    Returns:
        フォローしている場合はTrue、していない場合はFalse
    """
    follow = db.query(TopicFollow).filter(
        TopicFollow.topic_id == topic_id,
        TopicFollow.user_id == user_id
    ).first()
    return follow is not None


def get_trending_topics(db: Session, limit: int = 10) -> List[Topic]:
    """
    トレンドトピックを取得する
    
    Args:
        db: データベースセッション
        limit: 取得上限
        
    Returns:
        トピックオブジェクトのリスト
    """
    # 実際にはアクティビティやフォロー数などに基づいてトレンドを計算する
    # ここでは簡易的に重要度の高いトピックを返す
    return db.query(Topic).filter(
        Topic.status == "active"
    ).order_by(Topic.importance.desc()).limit(limit).all()