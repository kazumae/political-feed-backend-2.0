from typing import Any, Dict, List, Optional

from app import services
from app.api import deps
from app.models.comment import Comment, CommentReaction
from app.models.user import User
from app.schemas.comment import Comment as CommentSchema
from app.schemas.comment import CommentCreate, CommentList, CommentUpdate
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/statement/{statement_id}", response_model=CommentList)
def read_statement_comments(
    *,
    db: Session = Depends(deps.get_db),
    statement_id: str = Path(..., description="発言ID"),
    skip: int = 0,
    limit: int = 20,
    sort: Optional[str] = Query("newest", description="ソート順（newest, oldest, likes）"),
    parent_id: Optional[str] = Query(None, description="親コメントID（返信を取得する場合）"),
    current_user: Any = Depends(deps.get_current_user),
) -> Any:
    """
    発言に対するコメント一覧を取得する
    """
    # 発言が存在するか確認
    statement = services.statement.get_statement(db, id=statement_id)
    if not statement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="発言が見つかりません",
        )
    
    comments = services.comment.get_statement_comments(
        db, 
        statement_id=statement_id,
        parent_id=parent_id,
        skip=skip, 
        limit=limit, 
        sort=sort
    )
    
    total = services.comment.count_statement_comments(
        db, statement_id=statement_id, parent_id=parent_id
    )
    
    # ユーザーがいいねしているかどうかを確認
    if current_user:
        for comment in comments:
            comment.is_liked = services.comment.is_comment_liked(
                db, comment_id=comment.id, user_id=current_user.id
            )
            comment.is_own = comment.user_id == current_user.id
    
    return {
        "total": total,
        "comments": comments
    }


@router.post("/statement/{statement_id}", response_model=CommentSchema, status_code=status.HTTP_201_CREATED)
def create_comment(
    *,
    db: Session = Depends(deps.get_db),
    statement_id: str = Path(..., description="発言ID"),
    comment_in: CommentCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    発言にコメントを投稿する
    """
    # 発言が存在するか確認
    statement = services.statement.get_statement(db, id=statement_id)
    if not statement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="発言が見つかりません",
        )
    
    # 親コメントが存在するか確認
    if comment_in.parent_id:
        parent_comment = services.comment.get_comment(db, id=comment_in.parent_id)
        if not parent_comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="親コメントが見つかりません",
            )
        
        # 親コメントが同じ発言に対するものか確認
        if parent_comment.statement_id != statement_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="親コメントが別の発言に対するものです",
            )
    
    # コメントを作成
    comment = services.comment.create_comment(
        db, 
        obj_in=comment_in, 
        statement_id=statement_id,
        user_id=current_user.id
    )
    
    # コメント数を更新
    services.statement.update_statement_comments_count(db, statement_id=statement_id)
    
    return comment


@router.get("/{comment_id}", response_model=CommentSchema)
def read_comment(
    *,
    db: Session = Depends(deps.get_db),
    comment_id: str = Path(..., description="コメントID"),
    current_user: Any = Depends(deps.get_current_user),
) -> Any:
    """
    コメント詳細を取得する
    """
    comment = services.comment.get_comment(db, id=comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="コメントが見つかりません",
        )
    
    # ユーザーがいいねしているかどうかを確認
    if current_user:
        comment.is_liked = services.comment.is_comment_liked(
            db, comment_id=comment.id, user_id=current_user.id
        )
        comment.is_own = comment.user_id == current_user.id
    
    return comment


@router.put("/{comment_id}", response_model=CommentSchema)
def update_comment(
    *,
    db: Session = Depends(deps.get_db),
    comment_id: str = Path(..., description="コメントID"),
    comment_in: CommentUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    コメントを編集する（自分のコメントのみ）
    """
    comment = services.comment.get_comment(db, id=comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="コメントが見つかりません",
        )
    
    # 自分のコメントかどうか確認
    if comment.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="このコメントを編集する権限がありません",
        )
    
    comment = services.comment.update_comment(
        db, db_obj=comment, obj_in=comment_in
    )
    
    return comment


@router.delete("/{comment_id}", status_code=status.HTTP_200_OK)
def delete_comment(
    *,
    db: Session = Depends(deps.get_db),
    comment_id: str = Path(..., description="コメントID"),
    current_user: User = Depends(deps.get_current_active_user),
) -> Dict[str, bool]:
    """
    コメントを削除する（自分のコメントのみ）
    """
    comment = services.comment.get_comment(db, id=comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="コメントが見つかりません",
        )
    
    # 自分のコメントかどうか確認
    if comment.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="このコメントを削除する権限がありません",
        )
    
    statement_id = comment.statement_id
    
    services.comment.delete_comment(db, id=comment_id)
    
    # コメント数を更新
    services.statement.update_statement_comments_count(db, statement_id=statement_id)
    
    return {"success": True}


@router.get("/{comment_id}/replies", response_model=CommentList)
def read_comment_replies(
    *,
    db: Session = Depends(deps.get_db),
    comment_id: str = Path(..., description="コメントID"),
    skip: int = 0,
    limit: int = 20,
    sort: Optional[str] = Query("newest", description="ソート順（newest, oldest, likes）"),
    current_user: Any = Depends(deps.get_current_user),
) -> Any:
    """
    コメントに対する返信一覧を取得する
    """
    # コメントが存在するか確認
    comment = services.comment.get_comment(db, id=comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="コメントが見つかりません",
        )
    
    replies = services.comment.get_comment_replies(
        db, 
        comment_id=comment_id,
        skip=skip, 
        limit=limit, 
        sort=sort
    )
    
    total = services.comment.count_comment_replies(db, comment_id=comment_id)
    
    # ユーザーがいいねしているかどうかを確認
    if current_user:
        for reply in replies:
            reply.is_liked = services.comment.is_comment_liked(
                db, comment_id=reply.id, user_id=current_user.id
            )
            reply.is_own = reply.user_id == current_user.id
    
    return {
        "total": total,
        "comments": replies
    }


@router.post("/{comment_id}/like", status_code=status.HTTP_200_OK)
def like_comment(
    *,
    db: Session = Depends(deps.get_db),
    comment_id: str = Path(..., description="コメントID"),
    current_user: User = Depends(deps.get_current_active_user),
) -> Dict[str, Any]:
    """
    コメントにいいねする
    """
    # コメントが存在するか確認
    comment = services.comment.get_comment(db, id=comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="コメントが見つかりません",
        )
    
    # 既にいいねしているか確認
    existing_like = db.query(CommentReaction).filter(
        CommentReaction.comment_id == comment_id,
        CommentReaction.user_id == current_user.id,
        CommentReaction.reaction_type == "like"
    ).first()
    
    if existing_like:
        # 既にいいねしている場合は何もしない
        return {
            "success": True,
            "message": "既にいいねしています",
            "likes_count": services.comment.get_comment_likes_count(
                db, comment_id=comment_id
            )
        }
    
    # いいねを作成
    reaction = CommentReaction(
        comment_id=comment_id,
        user_id=current_user.id,
        reaction_type="like"
    )
    db.add(reaction)
    db.commit()
    
    # いいね数を更新
    services.comment.update_comment_likes_count(db, comment_id=comment_id)
    
    # いいね数を取得
    likes_count = services.comment.get_comment_likes_count(
        db, comment_id=comment_id
    )
    
    return {
        "success": True,
        "likes_count": likes_count
    }


@router.delete("/{comment_id}/like", status_code=status.HTTP_200_OK)
def unlike_comment(
    *,
    db: Session = Depends(deps.get_db),
    comment_id: str = Path(..., description="コメントID"),
    current_user: User = Depends(deps.get_current_active_user),
) -> Dict[str, Any]:
    """
    コメントのいいねを解除する
    """
    # コメントが存在するか確認
    comment = services.comment.get_comment(db, id=comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="コメントが見つかりません",
        )
    
    # いいねを取得
    like = db.query(CommentReaction).filter(
        CommentReaction.comment_id == comment_id,
        CommentReaction.user_id == current_user.id,
        CommentReaction.reaction_type == "like"
    ).first()
    
    if not like:
        # いいねしていない場合は何もしない
        return {
            "success": True,
            "message": "いいねしていません",
            "likes_count": services.comment.get_comment_likes_count(
                db, comment_id=comment_id
            )
        }
    
    # いいねを削除
    db.delete(like)
    db.commit()
    
    # いいね数を更新
    services.comment.update_comment_likes_count(db, comment_id=comment_id)
    
    # いいね数を取得
    likes_count = services.comment.get_comment_likes_count(
        db, comment_id=comment_id
    )
    
    return {
        "success": True,
        "likes_count": likes_count
    }


@router.post("/{comment_id}/report", status_code=status.HTTP_200_OK)
def report_comment(
    *,
    db: Session = Depends(deps.get_db),
    comment_id: str = Path(..., description="コメントID"),
    reason: str = Query(..., description="通報理由"),
    details: Optional[str] = Query(None, description="詳細説明"),
    current_user: User = Depends(deps.get_current_active_user),
) -> Dict[str, bool]:
    """
    コメントを通報する
    """
    # コメントが存在するか確認
    comment = services.comment.get_comment(db, id=comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="コメントが見つかりません",
        )
    
    # 既に通報しているか確認
    existing_report = services.comment.get_comment_report(
        db, comment_id=comment_id, user_id=current_user.id
    )
    
    if existing_report:
        # 既に通報している場合は何もしない
        return {
            "success": True,
            "message": "既に通報しています"
        }
    
    # 通報を作成
    services.comment.create_comment_report(
        db, 
        comment_id=comment_id, 
        user_id=current_user.id,
        reason=reason,
        details=details
    )
    
    return {"success": True}