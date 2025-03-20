from typing import List, Optional

from app.models.follows import PoliticianFollow, TopicFollow
from sqlalchemy.orm import Session


def get_politician_followers(
    db: Session, *, politician_id: str, skip: int = 0, limit: int = 100
) -> List[PoliticianFollow]:
    """
    政治家のフォロワー一覧を取得する
    
    Args:
        db: データベースセッション
        politician_id: 政治家ID
        skip: スキップ数
        limit: 取得上限
        
    Returns:
        PoliticianFollowオブジェクトのリスト
    """
    return db.query(PoliticianFollow).filter(
        PoliticianFollow.politician_id == politician_id
    ).offset(skip).limit(limit).all()


def get_user_following_politicians(
    db: Session, *, user_id: str, skip: int = 0, limit: int = 100
) -> List[PoliticianFollow]:
    """
    ユーザーがフォローしている政治家一覧を取得する
    
    Args:
        db: データベースセッション
        user_id: ユーザーID
        skip: スキップ数
        limit: 取得上限
        
    Returns:
        PoliticianFollowオブジェクトのリスト
    """
    return db.query(PoliticianFollow).filter(
        PoliticianFollow.user_id == user_id
    ).offset(skip).limit(limit).all()


def get_user_following_politicians_ids(
    db: Session, *, user_id: str
) -> List[str]:
    """
    ユーザーがフォローしている政治家IDのリストを取得する
    
    Args:
        db: データベースセッション
        user_id: ユーザーID
        
    Returns:
        政治家IDのリスト
    """
    follows = db.query(PoliticianFollow.politician_id).filter(
        PoliticianFollow.user_id == user_id
    ).all()
    return [follow[0] for follow in follows]


def get_politician_follow(
    db: Session, *, politician_id: str, user_id: str
) -> Optional[PoliticianFollow]:
    """
    特定のユーザーと政治家のフォロー関係を取得する
    
    Args:
        db: データベースセッション
        politician_id: 政治家ID
        user_id: ユーザーID
        
    Returns:
        PoliticianFollowオブジェクト、存在しない場合はNone
    """
    return db.query(PoliticianFollow).filter(
        PoliticianFollow.politician_id == politician_id,
        PoliticianFollow.user_id == user_id
    ).first()


def get_topic_followers(
    db: Session, *, topic_id: str, skip: int = 0, limit: int = 100
) -> List[TopicFollow]:
    """
    トピックのフォロワー一覧を取得する
    
    Args:
        db: データベースセッション
        topic_id: トピックID
        skip: スキップ数
        limit: 取得上限
        
    Returns:
        TopicFollowオブジェクトのリスト
    """
    return db.query(TopicFollow).filter(
        TopicFollow.topic_id == topic_id
    ).offset(skip).limit(limit).all()


def get_user_following_topics(
    db: Session, *, user_id: str, skip: int = 0, limit: int = 100
) -> List[TopicFollow]:
    """
    ユーザーがフォローしているトピック一覧を取得する
    
    Args:
        db: データベースセッション
        user_id: ユーザーID
        skip: スキップ数
        limit: 取得上限
        
    Returns:
        TopicFollowオブジェクトのリスト
    """
    return db.query(TopicFollow).filter(
        TopicFollow.user_id == user_id
    ).offset(skip).limit(limit).all()


def get_topic_follow(
    db: Session, *, topic_id: str, user_id: str
) -> Optional[TopicFollow]:
    """
    特定のユーザーとトピックのフォロー関係を取得する
    
    Args:
        db: データベースセッション
        topic_id: トピックID
        user_id: ユーザーID
        
    Returns:
        TopicFollowオブジェクト、存在しない場合はNone
    """
    return db.query(TopicFollow).filter(
        TopicFollow.topic_id == topic_id,
        TopicFollow.user_id == user_id
    ).first()