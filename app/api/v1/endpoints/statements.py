from typing import Any, Dict, List, Optional

from app import services
from app.api import deps
from app.models.statement import StatementReaction
from app.models.user import User
from app.schemas.statement import Statement as StatementSchema
from app.schemas.statement import (
    StatementCreate,
    StatementDetail,
    StatementList,
    StatementUpdate,
)
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/", response_model=StatementList)
def read_statements(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 20,
    sort: Optional[str] = Query("date_desc", description="ソート順（date_desc, date_asc, likes）"),
    filter_party: Optional[str] = Query(None, description="政党IDでフィルタリング"),
    filter_topic: Optional[str] = Query(None, description="トピックIDでフィルタリング"),
    filter_date_start: Optional[str] = Query(None, description="開始日（YYYY-MM-DD）"),
    filter_date_end: Optional[str] = Query(None, description="終了日（YYYY-MM-DD）"),
    search: Optional[str] = Query(None, description="キーワード検索"),
    current_user: Any = Depends(deps.get_current_user),
) -> Any:
    """
    発言一覧を取得する
    """
    statements = services.statement.get_statements(
        db, 
        skip=skip, 
        limit=limit, 
        sort=sort,
        filter_party=filter_party,
        filter_topic=filter_topic,
        filter_date_start=filter_date_start,
        filter_date_end=filter_date_end,
        search=search
    )
    
    total = services.statement.count_statements(
        db,
        filter_party=filter_party,
        filter_topic=filter_topic,
        filter_date_start=filter_date_start,
        filter_date_end=filter_date_end,
        search=search
    )
    
    # 次のページがあるかどうかを確認
    next_cursor = None
    if len(statements) == limit and total > skip + limit:
        next_cursor = str(skip + limit)
    
    # ユーザーがいいねしているかどうかを確認
    if current_user:
        for statement in statements:
            statement.is_liked = services.statement.is_statement_liked(
                db, statement_id=statement.id, user_id=current_user.id
            )
    
    return {
        "total": total,
        "statements": statements,
        "next_cursor": next_cursor
    }


@router.get("/following", response_model=StatementList)
def read_following_statements(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 20,
    sort: Optional[str] = Query("date_desc", description="ソート順（date_desc, date_asc, likes）"),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    フォロー中の政治家の発言一覧を取得する
    """
    # フォロー中の政治家IDを取得
    following_politician_ids = services.follows.get_user_following_politicians_ids(
        db, user_id=current_user.id
    )
    
    if not following_politician_ids:
        return {
            "total": 0,
            "statements": [],
            "next_cursor": None
        }
    
    statements = services.statement.get_statements_by_politicians(
        db, 
        politician_ids=following_politician_ids,
        skip=skip, 
        limit=limit, 
        sort=sort
    )
    
    total = services.statement.count_statements_by_politicians(
        db, politician_ids=following_politician_ids
    )
    
    # 次のページがあるかどうかを確認
    next_cursor = None
    if len(statements) == limit and total > skip + limit:
        next_cursor = str(skip + limit)
    
    # ユーザーがいいねしているかどうかを確認
    for statement in statements:
        statement.is_liked = services.statement.is_statement_liked(
            db, statement_id=statement.id, user_id=current_user.id
        )
    
    return {
        "total": total,
        "statements": statements,
        "next_cursor": next_cursor
    }


@router.get("/{statement_id}", response_model=StatementDetail)
def read_statement(
    *,
    db: Session = Depends(deps.get_db),
    statement_id: str = Path(..., description="発言ID"),
    current_user: Any = Depends(deps.get_current_user),
) -> Any:
    """
    発言詳細を取得する
    """
    statement = services.statement.get_statement(db, id=statement_id)
    if not statement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="発言が見つかりません",
        )
    
    # 発言に関連するトピックを取得
    topics = services.statement.get_statement_topics(db, statement_id=statement_id)
    
    # 結果を結合
    result = StatementDetail.model_validate(statement)
    result.topics = topics
    
    # politician_nameフィールドを設定
    if statement.politician:
        result.politician_name = statement.politician.name
        if statement.politician.current_party_id:
            result.party_id = statement.politician.current_party_id
    
    # ユーザーがいいねしているかどうかを確認
    if current_user:
        result.is_liked = services.statement.is_statement_liked(
            db, statement_id=statement_id, user_id=current_user.id
        )
    
    return result


@router.post("/", response_model=StatementSchema, status_code=status.HTTP_201_CREATED)
def create_statement(
    *,
    db: Session = Depends(deps.get_db),
    statement_in: StatementCreate,
    current_user: Any = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    新規発言を作成する（管理者のみ）
    """
    # 政治家が存在するか確認
    politician = services.politician.get_politician(db, id=statement_in.politician_id)
    if not politician:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="政治家が見つかりません",
        )
    
    # トピックが存在するか確認
    if statement_in.topic_ids:
        for topic_id in statement_in.topic_ids:
            topic = services.topic.get_topic(db, id=topic_id)
            if not topic:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"トピックが見つかりません: {topic_id}",
                )
    
    statement = services.statement.create_statement(db, obj_in=statement_in)
    return statement


@router.put("/{statement_id}", response_model=StatementSchema)
def update_statement(
    *,
    db: Session = Depends(deps.get_db),
    statement_id: str = Path(..., description="発言ID"),
    statement_in: StatementUpdate,
    current_user: Any = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    発言情報を更新する（管理者のみ）
    """
    statement = services.statement.get_statement(db, id=statement_id)
    if not statement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="発言が見つかりません",
        )
    
    # 政治家が存在するか確認
    if statement_in.politician_id:
        politician = services.politician.get_politician(db, id=statement_in.politician_id)
        if not politician:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="政治家が見つかりません",
            )
    
    # トピックが存在するか確認
    if statement_in.topic_ids:
        for topic_id in statement_in.topic_ids:
            topic = services.topic.get_topic(db, id=topic_id)
            if not topic:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"トピックが見つかりません: {topic_id}",
                )
    
    statement = services.statement.update_statement(
        db, db_obj=statement, obj_in=statement_in
    )
    return statement


@router.delete("/{statement_id}", response_model=StatementSchema)
def delete_statement(
    *,
    db: Session = Depends(deps.get_db),
    statement_id: str = Path(..., description="発言ID"),
    current_user: Any = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    発言を削除する（管理者のみ）
    """
    statement = services.statement.get_statement(db, id=statement_id)
    if not statement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="発言が見つかりません",
        )
    statement = services.statement.delete_statement(db, id=statement_id)
    return statement


@router.get("/politicians/{politician_id}", response_model=StatementList)
def read_politician_statements(
    *,
    db: Session = Depends(deps.get_db),
    politician_id: str = Path(..., description="政治家ID"),
    skip: int = 0,
    limit: int = 20,
    sort: Optional[str] = Query("date_desc", description="ソート順（date_desc, date_asc, likes）"),
    current_user: Any = Depends(deps.get_current_user),
) -> Any:
    """
    特定の政治家の発言一覧を取得する
    """
    # 政治家が存在するか確認
    politician = services.politician.get_politician(db, id=politician_id)
    if not politician:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="政治家が見つかりません",
        )
    
    statements = services.statement.get_statements_by_politician(
        db, 
        politician_id=politician_id,
        skip=skip, 
        limit=limit, 
        sort=sort
    )
    
    total = services.statement.count_statements_by_politician(
        db, politician_id=politician_id
    )
    
    # 次のページがあるかどうかを確認
    next_cursor = None
    if len(statements) == limit and total > skip + limit:
        next_cursor = str(skip + limit)
    
    # ユーザーがいいねしているかどうかを確認
    if current_user:
        for statement in statements:
            statement.is_liked = services.statement.is_statement_liked(
                db, statement_id=statement.id, user_id=current_user.id
            )
    
    return {
        "total": total,
        "statements": statements,
        "next_cursor": next_cursor
    }


@router.get("/parties/{party_id}", response_model=StatementList)
def read_party_statements(
    *,
    db: Session = Depends(deps.get_db),
    party_id: str = Path(..., description="政党ID"),
    skip: int = 0,
    limit: int = 20,
    sort: Optional[str] = Query("date_desc", description="ソート順（date_desc, date_asc, likes）"),
    current_user: Any = Depends(deps.get_current_user),
) -> Any:
    """
    特定の政党の発言一覧を取得する
    """
    # 政党が存在するか確認
    party = services.party.get_party(db, id=party_id)
    if not party:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="政党が見つかりません",
        )
    
    statements = services.statement.get_statements_by_party(
        db, 
        party_id=party_id,
        skip=skip, 
        limit=limit, 
        sort=sort
    )
    
    total = services.statement.count_statements_by_party(
        db, party_id=party_id
    )
    
    # 次のページがあるかどうかを確認
    next_cursor = None
    if len(statements) == limit and total > skip + limit:
        next_cursor = str(skip + limit)
    
    # ユーザーがいいねしているかどうかを確認
    if current_user:
        for statement in statements:
            statement.is_liked = services.statement.is_statement_liked(
                db, statement_id=statement.id, user_id=current_user.id
            )
    
    return {
        "total": total,
        "statements": statements,
        "next_cursor": next_cursor
    }


@router.get("/topics/{topic_id}", response_model=StatementList)
def read_topic_statements(
    *,
    db: Session = Depends(deps.get_db),
    topic_id: str = Path(..., description="トピックID"),
    skip: int = 0,
    limit: int = 20,
    sort: Optional[str] = Query("date_desc", description="ソート順（date_desc, date_asc, likes）"),
    current_user: Any = Depends(deps.get_current_user),
) -> Any:
    """
    特定のトピックの発言一覧を取得する
    """
    # トピックが存在するか確認
    topic = services.topic.get_topic(db, id=topic_id)
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="トピックが見つかりません",
        )
    
    statements = services.statement.get_statements_by_topic(
        db, 
        topic_id=topic_id,
        skip=skip, 
        limit=limit, 
        sort=sort
    )
    
    total = services.statement.count_statements_by_topic(
        db, topic_id=topic_id
    )
    
    # 次のページがあるかどうかを確認
    next_cursor = None
    if len(statements) == limit and total > skip + limit:
        next_cursor = str(skip + limit)
    
    # ユーザーがいいねしているかどうかを確認
    if current_user:
        for statement in statements:
            statement.is_liked = services.statement.is_statement_liked(
                db, statement_id=statement.id, user_id=current_user.id
            )
    
    return {
        "total": total,
        "statements": statements,
        "next_cursor": next_cursor
    }


@router.post("/{statement_id}/like", status_code=status.HTTP_200_OK)
def like_statement(
    *,
    db: Session = Depends(deps.get_db),
    statement_id: str = Path(..., description="発言ID"),
    current_user: User = Depends(deps.get_current_active_user),
) -> Dict[str, Any]:
    """
    発言にいいねする
    """
    # 発言が存在するか確認
    statement = services.statement.get_statement(db, id=statement_id)
    if not statement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="発言が見つかりません",
        )
    
    # 既にいいねしているか確認
    existing_like = db.query(StatementReaction).filter(
        StatementReaction.statement_id == statement_id,
        StatementReaction.user_id == current_user.id,
        StatementReaction.reaction_type == "like"
    ).first()
    
    if existing_like:
        # 既にいいねしている場合は何もしない
        return {
            "success": True,
            "message": "既にいいねしています",
            "likes_count": services.statement.get_statement_likes_count(
                db, statement_id=statement_id
            )
        }
    
    # いいねを作成
    reaction = StatementReaction(
        statement_id=statement_id,
        user_id=current_user.id,
        reaction_type="like"
    )
    db.add(reaction)
    db.commit()
    
    # いいね数を更新
    services.statement.update_statement_likes_count(db, statement_id=statement_id)
    
    # いいね数を取得
    likes_count = services.statement.get_statement_likes_count(
        db, statement_id=statement_id
    )
    
    return {
        "success": True,
        "likes_count": likes_count
    }


@router.delete("/{statement_id}/like", status_code=status.HTTP_200_OK)
def unlike_statement(
    *,
    db: Session = Depends(deps.get_db),
    statement_id: str = Path(..., description="発言ID"),
    current_user: User = Depends(deps.get_current_active_user),
) -> Dict[str, Any]:
    """
    発言のいいねを解除する
    """
    # 発言が存在するか確認
    statement = services.statement.get_statement(db, id=statement_id)
    if not statement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="発言が見つかりません",
        )
    
    # いいねを取得
    like = db.query(StatementReaction).filter(
        StatementReaction.statement_id == statement_id,
        StatementReaction.user_id == current_user.id,
        StatementReaction.reaction_type == "like"
    ).first()
    
    if not like:
        # いいねしていない場合は何もしない
        return {
            "success": True,
            "message": "いいねしていません",
            "likes_count": services.statement.get_statement_likes_count(
                db, statement_id=statement_id
            )
        }
    
    # いいねを削除
    db.delete(like)
    db.commit()
    
    # いいね数を更新
    services.statement.update_statement_likes_count(db, statement_id=statement_id)
    
    # いいね数を取得
    likes_count = services.statement.get_statement_likes_count(
        db, statement_id=statement_id
    )
    
    return {
        "success": True,
        "likes_count": likes_count
    }