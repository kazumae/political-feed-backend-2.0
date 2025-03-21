from typing import Any, Dict, Optional

from app import services
from app.api import deps
from app.models.user import User
from app.schemas.activity import (
    UserComments,
    UserFollowingPoliticians,
    UserFollowingTopics,
    UserLikedStatements,
    UserNotifications,
    UserViewHistory,
)
from app.schemas.statement import StatementList
from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/following/politicians", response_model=UserFollowingPoliticians)
def read_following_politicians(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, description="スキップ数"),
    limit: int = Query(20, description="取得上限"),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    フォロー中の政治家一覧を取得する
    """
    result = services.activity.get_user_following_politicians(
        db, user_id=current_user.id, skip=skip, limit=limit
    )
    
    return {
        "politicians": result["politicians"],
        "total": result["total"]
    }


@router.get("/following/topics", response_model=UserFollowingTopics)
def read_following_topics(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, description="スキップ数"),
    limit: int = Query(20, description="取得上限"),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    フォロー中のトピック一覧を取得する
    """
    result = services.activity.get_user_following_topics(
        db, user_id=current_user.id, skip=skip, limit=limit
    )
    
    return {
        "topics": result["topics"],
        "total": result["total"]
    }


@router.get("/likes", response_model=UserLikedStatements)
def read_liked_statements(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, description="スキップ数"),
    limit: int = Query(20, description="取得上限"),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    いいねした発言一覧を取得する
    """
    result = services.activity.get_user_liked_statements(
        db, user_id=current_user.id, skip=skip, limit=limit
    )
    
    return {
        "statements": result["statements"],
        "total": result["total"]
    }


@router.get("/comments", response_model=UserComments)
def read_user_comments(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, description="スキップ数"),
    limit: int = Query(20, description="取得上限"),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    投稿したコメント一覧を取得する
    """
    result = services.activity.get_user_comments(
        db, user_id=current_user.id, skip=skip, limit=limit
    )
    
    return {
        "comments": result["comments"],
        "total": result["total"]
    }


@router.get("/history", response_model=UserViewHistory)
def read_view_history(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, description="スキップ数"),
    limit: int = Query(20, description="取得上限"),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    閲覧履歴を取得する
    """
    result = services.activity.get_user_view_history(
        db, user_id=current_user.id, skip=skip, limit=limit
    )
    
    return {
        "history": result["history"],
        "total": result["total"]
    }


@router.get("/feed", response_model=StatementList)
def read_personalized_feed(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, description="スキップ数"),
    limit: int = Query(20, description="取得上限"),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    パーソナライズドフィードを取得する
    """
    result = services.activity.get_personalized_feed(
        db, user_id=current_user.id, skip=skip, limit=limit
    )
    
    return {
        "statements": result["statements"],
        "total": result["total"],
        "next_cursor": None
    }


@router.get("/notifications", response_model=UserNotifications)
def read_notifications(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, description="スキップ数"),
    limit: int = Query(20, description="取得上限"),
    read: Optional[bool] = Query(None, description="既読/未読でフィルタリング"),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    通知一覧を取得する
    """
    result = services.activity.get_user_notifications(
        db, user_id=current_user.id, skip=skip, limit=limit, read=read
    )
    
    return {
        "notifications": result["notifications"],
        "total": result["total"],
        "unread_count": result["unread_count"]
    }


@router.post("/notifications/{notification_id}/read", status_code=status.HTTP_200_OK)
def mark_notification_as_read(
    *,
    db: Session = Depends(deps.get_db),
    notification_id: str = Path(..., description="通知ID"),
    current_user: User = Depends(deps.get_current_active_user),
) -> Dict[str, bool]:
    """
    通知を既読にする
    """
    success = services.activity.mark_notification_as_read(
        db, notification_id=notification_id, user_id=current_user.id
    )
    
    return {"success": success}


@router.post("/notifications/read-all", status_code=status.HTTP_200_OK)
def mark_all_notifications_as_read(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Dict[str, bool]:
    """
    全ての通知を既読にする
    """
    services.activity.mark_all_notifications_as_read(
        db, user_id=current_user.id
    )
    
    return {"success": True}