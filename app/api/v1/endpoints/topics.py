from typing import Any, Dict, List, Optional

from app import services
from app.api import deps
from app.models.follows import TopicFollow
from app.models.user import User
from app.schemas.topic import Topic as TopicSchema
from app.schemas.topic import TopicCreate, TopicUpdate, TopicWithDetails
from app.schemas.topic_party import TopicPartyStances
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/", response_model=List[TopicSchema])
def read_topics(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = Query(None, description="ステータスでフィルタリング"),
    category: Optional[str] = Query(None, description="カテゴリでフィルタリング"),
    search: Optional[str] = Query(None, description="名前で検索"),
) -> Any:
    """
    トピック一覧を取得する（認証不要）
    """
    topics = services.topic.get_topics(
        db,
        skip=skip,
        limit=limit,
        status=status,
        category=category,
        search=search
    )
    return topics


@router.post(
    "/",
    response_model=TopicSchema,
    status_code=status.HTTP_201_CREATED
)
def create_topic(
    *,
    db: Session = Depends(deps.get_db),
    topic_in: TopicCreate,
    current_user: Any = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    新規トピックを作成する（管理者のみ）
    """
    topic = services.topic.create_topic(db, obj_in=topic_in)
    return topic


@router.get("/{id}", response_model=TopicWithDetails)
def read_topic(
    *,
    db: Session = Depends(deps.get_db),
    id: str = Path(..., description="トピックID"),
    current_user: Any = Depends(deps.get_current_user_optional),
) -> Any:
    """
    トピックの詳細情報を取得する（認証不要）
    """
    topic = services.topic.get_topic(db, id=id)
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="トピックが見つかりません",
        )
    
    # 関連トピックを取得
    related_topics = services.topic.get_related_topics(db, topic_id=id)
    
    # 結果を結合
    result = TopicWithDetails.model_validate(topic)
    result.related_topics = related_topics
    
    # ユーザーがフォローしているかどうかを確認（ログイン時のみ）
    if current_user:
        result.is_following = services.topic.is_following_topic(
            db, topic_id=id, user_id=current_user.id
        )
    else:
        result.is_following = False
    
    return result


@router.put("/{id}", response_model=TopicSchema)
def update_topic(
    *,
    db: Session = Depends(deps.get_db),
    id: str = Path(..., description="トピックID"),
    topic_in: TopicUpdate,
    current_user: Any = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    トピック情報を更新する（管理者のみ）
    """
    topic = services.topic.get_topic(db, id=id)
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="トピックが見つかりません",
        )
    topic = services.topic.update_topic(
        db, db_obj=topic, obj_in=topic_in
    )
    return topic


@router.delete("/{id}", response_model=TopicSchema)
def delete_topic(
    *,
    db: Session = Depends(deps.get_db),
    id: str = Path(..., description="トピックID"),
    current_user: Any = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    トピックを削除する（管理者のみ）
    """
    topic = services.topic.get_topic(db, id=id)
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="トピックが見つかりません",
        )
    topic = services.topic.delete_topic(db, id=id)
    return topic


# トピックフォロー関連のエンドポイント

@router.post("/{topic_id}/follow", status_code=status.HTTP_200_OK)
def follow_topic(
    *,
    db: Session = Depends(deps.get_db),
    topic_id: str = Path(..., description="トピックID"),
    current_user: User = Depends(deps.get_current_active_user),
) -> Dict[str, Any]:
    """
    トピックをフォローする
    """
    # トピックが存在するか確認
    topic = services.topic.get_topic(db, id=topic_id)
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="トピックが見つかりません",
        )
    
    # 既にフォローしているか確認
    existing_follow = db.query(TopicFollow).filter(
        TopicFollow.topic_id == topic_id,
        TopicFollow.user_id == current_user.id
    ).first()
    
    if existing_follow:
        # 既にフォローしている場合は何もしない
        return {
            "success": True,
            "message": "既にフォローしています",
            "followers_count": services.topic.get_followers_count(
                db, topic_id=topic_id
            )
        }
    
    # フォロー関係を作成
    follow = TopicFollow(
        topic_id=topic_id,
        user_id=current_user.id
    )
    db.add(follow)
    db.commit()
    
    # フォロワー数を取得
    followers_count = services.topic.get_followers_count(
        db, topic_id=topic_id
    )
    
    return {
        "success": True,
        "followers_count": followers_count
    }


@router.delete("/{topic_id}/follow", status_code=status.HTTP_200_OK)
def unfollow_topic(
    *,
    db: Session = Depends(deps.get_db),
    topic_id: str = Path(..., description="トピックID"),
    current_user: User = Depends(deps.get_current_active_user),
) -> Dict[str, Any]:
    """
    トピックのフォローを解除する
    """
    # トピックが存在するか確認
    topic = services.topic.get_topic(db, id=topic_id)
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="トピックが見つかりません",
        )
    
    # フォロー関係を取得
    follow = db.query(TopicFollow).filter(
        TopicFollow.topic_id == topic_id,
        TopicFollow.user_id == current_user.id
    ).first()
    
    if not follow:
        # フォローしていない場合は何もしない
        return {
            "success": True,
            "message": "フォローしていません",
            "followers_count": services.topic.get_followers_count(
                db, topic_id=topic_id
            )
        }
    
    # フォロー関係を削除
    db.delete(follow)
    db.commit()
    
    # フォロワー数を取得
    followers_count = services.topic.get_followers_count(
        db, topic_id=topic_id
    )
    
    return {
        "success": True,
        "followers_count": followers_count
    }


@router.get("/{topic_id}/parties", response_model=TopicPartyStances)
def read_topic_parties(
    *,
    db: Session = Depends(deps.get_db),
    topic_id: str = Path(..., description="トピックID"),
) -> Any:
    """
    トピックに関する政党スタンス一覧を取得する（認証不要）
    """
    # トピックが存在するか確認
    topic = services.topic.get_topic(db, id=topic_id)
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="トピックが見つかりません",
        )
    
    # トピックに関する政党スタンスを集計
    party_stances = services.statement.get_topic_party_stances(
        db, topic_id=topic_id
    )
    
    # 結果を返す
    result = {
        "topic_id": topic.id,
        "topic_name": topic.name,
        "parties": party_stances
    }
    
    return result


@router.get("/trending", response_model=List[TopicSchema])
def get_trending_topics(
    db: Session = Depends(deps.get_db),
    limit: int = Query(10, description="取得数"),
) -> Any:
    """
    トレンドトピックを取得する（認証不要）
    """
    topics = services.topic.get_trending_topics(db, limit=limit)
    # データがない場合でも空のリストを返す（404エラーを返さない）
    return topics or []