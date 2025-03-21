from datetime import datetime
from typing import Dict, List, Optional

from app import services
from app.models.activity import Notification, UserActivity
from app.models.comment import Comment
from app.models.follows import PoliticianFollow, TopicFollow
from app.models.statement import Statement, StatementReaction
from sqlalchemy import desc, func
from sqlalchemy.orm import Session, joinedload


def get_user_following_politicians(
    db: Session, user_id: str, skip: int = 0, limit: int = 20
) -> Dict:
    """
    ユーザーがフォローしている政治家一覧を取得する
    
    Args:
        db: データベースセッション
        user_id: ユーザーID
        skip: スキップ数
        limit: 取得上限
        
    Returns:
        フォローしている政治家一覧
    """
    # フォロー関係を取得
    follows = db.query(PoliticianFollow).filter(
        PoliticianFollow.user_id == user_id
    ).offset(skip).limit(limit).all()
    
    # 政治家IDのリストを取得
    politician_ids = [follow.politician_id for follow in follows]
    
    # 政治家情報を取得
    politicians = []
    if politician_ids:
        politicians = db.query(services.politician.Politician).filter(
            services.politician.Politician.id.in_(politician_ids)
        ).all()
    
    # 総数を取得
    total = db.query(func.count(PoliticianFollow.politician_id)).filter(
        PoliticianFollow.user_id == user_id
    ).scalar() or 0
    
    return {
        "politicians": politicians,
        "total": total
    }


def get_user_following_topics(
    db: Session, user_id: str, skip: int = 0, limit: int = 20
) -> Dict:
    """
    ユーザーがフォローしているトピック一覧を取得する
    
    Args:
        db: データベースセッション
        user_id: ユーザーID
        skip: スキップ数
        limit: 取得上限
        
    Returns:
        フォローしているトピック一覧
    """
    # フォロー関係を取得
    follows = db.query(TopicFollow).filter(
        TopicFollow.user_id == user_id
    ).offset(skip).limit(limit).all()
    
    # トピックIDのリストを取得
    topic_ids = [follow.topic_id for follow in follows]
    
    # トピック情報を取得
    topics = []
    if topic_ids:
        topics = db.query(services.topic.Topic).filter(
            services.topic.Topic.id.in_(topic_ids)
        ).all()
    
    # 総数を取得
    total = db.query(func.count(TopicFollow.topic_id)).filter(
        TopicFollow.user_id == user_id
    ).scalar() or 0
    
    return {
        "topics": topics,
        "total": total
    }


def get_user_liked_statements(
    db: Session, user_id: str, skip: int = 0, limit: int = 20
) -> Dict:
    """
    ユーザーがいいねした発言一覧を取得する
    
    Args:
        db: データベースセッション
        user_id: ユーザーID
        skip: スキップ数
        limit: 取得上限
        
    Returns:
        いいねした発言一覧
    """
    # いいね関係を取得
    likes = db.query(StatementReaction).filter(
        StatementReaction.user_id == user_id,
        StatementReaction.reaction_type == "like"
    ).order_by(
        desc(StatementReaction.created_at)
    ).offset(skip).limit(limit).all()
    
    # 発言IDのリストを取得
    statement_ids = [like.statement_id for like in likes]
    
    # 発言情報を取得
    statements = []
    if statement_ids:
        statements = db.query(Statement).options(
            joinedload(Statement.politician)
        ).filter(
            Statement.id.in_(statement_ids),
            Statement.status == "published"
        ).all()
        
        # politician_nameフィールドを設定
        for statement in statements:
            if statement.politician:
                statement.politician_name = statement.politician.name
                if statement.politician.current_party_id:
                    statement.party_id = statement.politician.current_party_id
    
    # 総数を取得
    total = db.query(func.count(StatementReaction.id)).filter(
        StatementReaction.user_id == user_id,
        StatementReaction.reaction_type == "like"
    ).scalar() or 0
    
    return {
        "statements": statements,
        "total": total
    }


def get_user_comments(
    db: Session, user_id: str, skip: int = 0, limit: int = 20
) -> Dict:
    """
    ユーザーが投稿したコメント一覧を取得する
    
    Args:
        db: データベースセッション
        user_id: ユーザーID
        skip: スキップ数
        limit: 取得上限
        
    Returns:
        投稿したコメント一覧
    """
    # コメントを取得
    comments = db.query(Comment).options(
        joinedload(Comment.statement)
    ).filter(
        Comment.user_id == user_id,
        Comment.status == "published"
    ).order_by(
        desc(Comment.created_at)
    ).offset(skip).limit(limit).all()
    
    # 発言の抜粋を設定
    for comment in comments:
        if comment.statement:
            # 発言の内容を抜粋（最初の50文字）
            comment.statement_excerpt = comment.statement.content[:50] + "..." if len(comment.statement.content) > 50 else comment.statement.content
            
            # 政治家名を設定
            if comment.statement.politician:
                comment.politician_name = comment.statement.politician.name
    
    # 総数を取得
    total = db.query(func.count(Comment.id)).filter(
        Comment.user_id == user_id,
        Comment.status == "published"
    ).scalar() or 0
    
    return {
        "comments": comments,
        "total": total
    }


def get_user_view_history(
    db: Session, user_id: str, skip: int = 0, limit: int = 20
) -> Dict:
    """
    ユーザーの閲覧履歴を取得する
    
    Args:
        db: データベースセッション
        user_id: ユーザーID
        skip: スキップ数
        limit: 取得上限
        
    Returns:
        閲覧履歴
    """
    # 閲覧履歴を取得
    history_records = db.query(UserActivity).filter(
        UserActivity.user_id == user_id,
        UserActivity.activity_type == "view",
        UserActivity.target_type == "statement"
    ).order_by(
        desc(UserActivity.created_at)
    ).offset(skip).limit(limit).all()
    
    # 発言IDのリストを取得
    statement_ids = [record.target_id for record in history_records]
    
    # 発言情報を取得
    statements_dict = {}
    if statement_ids:
        statements = db.query(Statement).options(
            joinedload(Statement.politician)
        ).filter(
            Statement.id.in_(statement_ids),
            Statement.status == "published"
        ).all()
        
        # 辞書に変換
        for statement in statements:
            statements_dict[statement.id] = statement
    
    # 閲覧履歴を構築
    history = []
    for record in history_records:
        statement = statements_dict.get(record.target_id)
        if statement:
            # 発言の内容を抜粋（最初の50文字）
            statement_excerpt = statement.content[:50] + "..." if len(statement.content) > 50 else statement.content
            
            # 政治家名を取得
            politician_name = statement.politician.name if statement.politician else "不明"
            
            history.append({
                "statement_id": statement.id,
                "statement_excerpt": statement_excerpt,
                "politician_name": politician_name,
                "viewed_at": record.created_at
            })
    
    # 総数を取得
    total = db.query(func.count(UserActivity.id)).filter(
        UserActivity.user_id == user_id,
        UserActivity.activity_type == "view",
        UserActivity.target_type == "statement"
    ).scalar() or 0
    
    return {
        "history": history,
        "total": total
    }


def get_user_notifications(
    db: Session, user_id: str, skip: int = 0, limit: int = 20, read: Optional[bool] = None
) -> Dict:
    """
    ユーザーの通知一覧を取得する
    
    Args:
        db: データベースセッション
        user_id: ユーザーID
        skip: スキップ数
        limit: 取得上限
        read: 既読/未読でフィルタリング
        
    Returns:
        通知一覧
    """
    # 通知を取得
    query = db.query(Notification).filter(
        Notification.user_id == user_id
    )
    
    # 既読/未読でフィルタリング
    if read is not None:
        query = query.filter(Notification.is_read == read)
    
    # 通知を取得
    notifications = query.order_by(
        desc(Notification.created_at)
    ).offset(skip).limit(limit).all()
    
    # 総数を取得
    total = db.query(func.count(Notification.id)).filter(
        Notification.user_id == user_id
    ).scalar() or 0
    
    # 未読数を取得
    unread_count = db.query(func.count(Notification.id)).filter(
        Notification.user_id == user_id,
        Notification.is_read == False
    ).scalar() or 0
    
    return {
        "notifications": notifications,
        "total": total,
        "unread_count": unread_count
    }


def mark_notification_as_read(db: Session, notification_id: str, user_id: str) -> bool:
    """
    通知を既読にする
    
    Args:
        db: データベースセッション
        notification_id: 通知ID
        user_id: ユーザーID
        
    Returns:
        成功した場合はTrue、失敗した場合はFalse
    """
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == user_id
    ).first()
    
    if not notification:
        return False
    
    notification.is_read = True
    db.add(notification)
    db.commit()
    
    return True


def mark_all_notifications_as_read(db: Session, user_id: str) -> int:
    """
    全ての通知を既読にする
    
    Args:
        db: データベースセッション
        user_id: ユーザーID
        
    Returns:
        既読にした通知の数
    """
    result = db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.is_read == False
    ).update({"is_read": True})
    
    db.commit()
    
    return result


def record_view_activity(
    db: Session, user_id: str, statement_id: str
) -> UserActivity:
    """
    閲覧アクティビティを記録する
    
    Args:
        db: データベースセッション
        user_id: ユーザーID
        statement_id: 発言ID
        
    Returns:
        作成されたアクティビティ
    """
    # 既存のアクティビティを確認（同じ発言を短時間に複数回閲覧した場合は記録しない）
    existing = db.query(UserActivity).filter(
        UserActivity.user_id == user_id,
        UserActivity.activity_type == "view",
        UserActivity.target_type == "statement",
        UserActivity.target_id == statement_id,
        UserActivity.created_at > datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    ).first()
    
    if existing:
        # 既存のアクティビティの日時を更新
        existing.created_at = datetime.utcnow()
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return existing
    
    # 新しいアクティビティを作成
    activity = UserActivity(
        user_id=user_id,
        activity_type="view",
        target_type="statement",
        target_id=statement_id,
        created_at=datetime.utcnow()
    )
    
    db.add(activity)
    db.commit()
    db.refresh(activity)
    
    return activity


def get_personalized_feed(
    db: Session, user_id: str, skip: int = 0, limit: int = 20
) -> Dict:
    """
    パーソナライズドフィードを取得する
    
    Args:
        db: データベースセッション
        user_id: ユーザーID
        skip: スキップ数
        limit: 取得上限
        
    Returns:
        パーソナライズドフィード
    """
    # フォローしている政治家IDを取得
    politician_ids = services.follows.get_user_following_politicians_ids(
        db, user_id=user_id
    )
    
    # フォローしている政治家の発言を取得
    statements = []
    total = 0
    
    if politician_ids:
        statements = services.statement.get_statements_by_politicians(
            db, politician_ids=politician_ids, skip=skip, limit=limit
        )
        
        total = services.statement.count_statements_by_politicians(
            db, politician_ids=politician_ids
        )
    
    return {
        "statements": statements,
        "total": total
    }