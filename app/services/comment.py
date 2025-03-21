from typing import Dict, List, Optional, Union

from app.models.comment import Comment, CommentReaction
from app.models.report import CommentReport
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentUpdate
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload


def get_comment(db: Session, id: str) -> Optional[Comment]:
    """
    IDでコメントを取得する
    
    Args:
        db: データベースセッション
        id: コメントID
        
    Returns:
        コメントオブジェクト、存在しない場合はNone
    """
    return db.query(Comment).options(
        joinedload(Comment.user)
    ).filter(Comment.id == id).first()


def get_statement_comments(
    db: Session,
    statement_id: str,
    parent_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    sort: str = "newest"
) -> List[Comment]:
    """
    発言に対するコメント一覧を取得する
    
    Args:
        db: データベースセッション
        statement_id: 発言ID
        parent_id: 親コメントID（返信を取得する場合）
        skip: スキップ数
        limit: 取得上限
        sort: ソート順
        
    Returns:
        コメントオブジェクトのリスト
    """
    try:
        # まずコメントのIDのみを取得
        comment_ids_query = db.query(Comment.id).filter(
            Comment.statement_id == statement_id,
            Comment.status == "published"
        )
        
        # 親コメントIDが指定されている場合は返信を取得
        if parent_id:
            comment_ids_query = comment_ids_query.filter(Comment.parent_id == parent_id)
        else:
            # 親コメントIDが指定されていない場合はトップレベルのコメントを取得
            comment_ids_query = comment_ids_query.filter(Comment.parent_id.is_(None))
        
        # ソート
        if sort == "newest":
            comment_ids_query = comment_ids_query.order_by(Comment.created_at.desc())
        elif sort == "oldest":
            comment_ids_query = comment_ids_query.order_by(Comment.created_at.asc())
        else:
            comment_ids_query = comment_ids_query.order_by(Comment.created_at.desc())
        
        # ページネーション
        comment_ids = comment_ids_query.offset(skip).limit(limit).all()
        
        # IDのリストを取得
        comment_id_list = [comment_id[0] for comment_id in comment_ids]
        
        if not comment_id_list:
            return []
        
        # IDのリストを使用して、コメントを取得
        comments = db.query(Comment).filter(
            Comment.id.in_(comment_id_list)
        ).all()
        
        # ユーザー情報を取得
        user_ids = [comment.user_id for comment in comments]
        users = db.query(User).filter(User.id.in_(user_ids)).all()
        
        # ユーザー情報をコメントに設定
        user_dict = {user.id: user for user in users}
        for comment in comments:
            comment.user = user_dict.get(comment.user_id)
            
            # likes_count, replies_count, reports_countが存在しない場合は0を設定
            if not hasattr(comment, 'likes_count'):
                comment.likes_count = 0
            if not hasattr(comment, 'replies_count'):
                comment.replies_count = 0
            if not hasattr(comment, 'reports_count'):
                comment.reports_count = 0
        
        # ソート順に並び替え
        if sort == "newest":
            comments.sort(key=lambda x: x.created_at, reverse=True)
        elif sort == "oldest":
            comments.sort(key=lambda x: x.created_at)
        
        return comments
    except Exception as e:
        # エラーが発生した場合は、空のリストを返す
        print(f"コメント取得中にエラーが発生: {e}")
        return []


def count_statement_comments(
    db: Session,
    statement_id: str,
    parent_id: Optional[str] = None
) -> int:
    """
    発言に対するコメント数を取得する
    
    Args:
        db: データベースセッション
        statement_id: 発言ID
        parent_id: 親コメントID（返信を取得する場合）
        
    Returns:
        コメント数
    """
    query = db.query(func.count(Comment.id)).filter(
        Comment.statement_id == statement_id,
        Comment.status == "published"
    )
    
    # 親コメントIDが指定されている場合は返信を取得
    if parent_id:
        query = query.filter(Comment.parent_id == parent_id)
    else:
        # 親コメントIDが指定されていない場合はトップレベルのコメントを取得
        query = query.filter(Comment.parent_id == None)
    
    return query.scalar() or 0


def get_comment_replies(
    db: Session, 
    comment_id: str,
    skip: int = 0, 
    limit: int = 20,
    sort: str = "newest"
) -> List[Comment]:
    """
    コメントに対する返信一覧を取得する
    
    Args:
        db: データベースセッション
        comment_id: コメントID
        skip: スキップ数
        limit: 取得上限
        sort: ソート順
        
    Returns:
        コメントオブジェクトのリスト
    """
    query = db.query(Comment).options(
        joinedload(Comment.user)
    ).filter(
        Comment.parent_id == comment_id,
        Comment.status == "published"
    )
    
    # ソート
    if sort == "newest":
        query = query.order_by(Comment.created_at.desc())
    elif sort == "oldest":
        query = query.order_by(Comment.created_at.asc())
    elif sort == "likes":
        query = query.order_by(Comment.likes_count.desc())
    else:
        query = query.order_by(Comment.created_at.desc())
    
    return query.offset(skip).limit(limit).all()


def count_comment_replies(
    db: Session,
    comment_id: str
) -> int:
    """
    コメントに対する返信数を取得する
    
    Args:
        db: データベースセッション
        comment_id: コメントID
        
    Returns:
        返信数
    """
    return db.query(func.count(Comment.id)).filter(
        Comment.parent_id == comment_id,
        Comment.status == "published"
    ).scalar() or 0


def create_comment(
    db: Session, 
    obj_in: CommentCreate, 
    statement_id: str,
    user_id: str
) -> Comment:
    """
    新規コメントを作成する
    
    Args:
        db: データベースセッション
        obj_in: コメント作成スキーマ
        statement_id: 発言ID
        user_id: ユーザーID
        
    Returns:
        作成されたコメントオブジェクト
    """
    db_obj = Comment(
        user_id=user_id,
        statement_id=statement_id,
        parent_id=obj_in.parent_id,
        content=obj_in.content,
        status="published",
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    
    # 親コメントがある場合は返信数を更新
    if obj_in.parent_id:
        update_comment_replies_count(db, comment_id=obj_in.parent_id)
    
    return db_obj


def update_comment(
    db: Session, 
    *, 
    db_obj: Comment, 
    obj_in: Union[CommentUpdate, Dict[str, any]]
) -> Comment:
    """
    コメント情報を更新する
    
    Args:
        db: データベースセッション
        db_obj: 更新対象のコメントオブジェクト
        obj_in: 更新データ（CommentUpdateオブジェクトまたは辞書）
        
    Returns:
        更新されたコメントオブジェクト
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


def delete_comment(db: Session, *, id: str) -> None:
    """
    コメントを削除する
    
    Args:
        db: データベースセッション
        id: コメントID
    """
    comment = db.query(Comment).get(id)
    if comment:
        # 親コメントIDを取得
        parent_id = comment.parent_id
        
        # コメントを削除
        db.delete(comment)
        db.commit()
        
        # 親コメントがある場合は返信数を更新
        if parent_id:
            update_comment_replies_count(db, comment_id=parent_id)


def get_comment_likes_count(db: Session, *, comment_id: str) -> int:
    """
    コメントのいいね数を取得する
    
    Args:
        db: データベースセッション
        comment_id: コメントID
        
    Returns:
        いいね数
    """
    return db.query(func.count(CommentReaction.id)).filter(
        CommentReaction.comment_id == comment_id,
        CommentReaction.reaction_type == "like"
    ).scalar() or 0


def update_comment_likes_count(db: Session, *, comment_id: str) -> None:
    """
    コメントのいいね数を更新する
    
    Args:
        db: データベースセッション
        comment_id: コメントID
    """
    likes_count = get_comment_likes_count(db, comment_id=comment_id)
    
    comment = db.query(Comment).get(comment_id)
    if comment:
        comment.likes_count = likes_count
        db.add(comment)
        db.commit()


def update_comment_replies_count(db: Session, *, comment_id: str) -> None:
    """
    コメントの返信数を更新する
    
    Args:
        db: データベースセッション
        comment_id: コメントID
    """
    replies_count = count_comment_replies(db, comment_id=comment_id)
    
    comment = db.query(Comment).get(comment_id)
    if comment:
        comment.replies_count = replies_count
        db.add(comment)
        db.commit()


def is_comment_liked(db: Session, *, comment_id: str, user_id: str) -> bool:
    """
    ユーザーがコメントにいいねしているかどうかを確認する
    
    Args:
        db: データベースセッション
        comment_id: コメントID
        user_id: ユーザーID
        
    Returns:
        いいねしている場合はTrue、していない場合はFalse
    """
    reaction = db.query(CommentReaction).filter(
        CommentReaction.comment_id == comment_id,
        CommentReaction.user_id == user_id,
        CommentReaction.reaction_type == "like"
    ).first()
    return reaction is not None


def get_comment_report(
    db: Session, *, comment_id: str, user_id: str
) -> Optional[CommentReport]:
    """
    ユーザーのコメント通報を取得する
    
    Args:
        db: データベースセッション
        comment_id: コメントID
        user_id: ユーザーID
        
    Returns:
        コメント通報オブジェクト、存在しない場合はNone
    """
    return db.query(CommentReport).filter(
        CommentReport.comment_id == comment_id,
        CommentReport.user_id == user_id
    ).first()


def create_comment_report(
    db: Session, 
    *, 
    comment_id: str, 
    user_id: str,
    reason: str,
    details: Optional[str] = None
) -> CommentReport:
    """
    コメント通報を作成する
    
    Args:
        db: データベースセッション
        comment_id: コメントID
        user_id: ユーザーID
        reason: 通報理由
        details: 詳細説明
        
    Returns:
        作成されたコメント通報オブジェクト
    """
    db_obj = CommentReport(
        comment_id=comment_id,
        user_id=user_id,
        reason=reason,
        details=details,
        status="pending"
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    
    # 通報数を更新
    update_comment_reports_count(db, comment_id=comment_id)
    
    return db_obj


def update_comment_reports_count(db: Session, *, comment_id: str) -> None:
    """
    コメントの通報数を更新する
    
    Args:
        db: データベースセッション
        comment_id: コメントID
    """
    reports_count = db.query(func.count(CommentReport.id)).filter(
        CommentReport.comment_id == comment_id
    ).scalar() or 0
    
    comment = db.query(Comment).get(comment_id)
    if comment:
        comment.reports_count = reports_count
        db.add(comment)
        db.commit()