from typing import Any, Optional

from app import services
from app.api import deps
from app.schemas.search import SearchResult
from app.schemas.statement import StatementList
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/statements", response_model=StatementList)
def search_statements(
    db: Session = Depends(deps.get_db),
    q: str = Query(..., description="検索キーワード"),
    skip: int = Query(0, description="スキップ数"),
    limit: int = Query(20, description="取得上限"),
    filter_party: Optional[str] = Query(None, description="政党IDでフィルタリング"),
    filter_topic: Optional[str] = Query(None, description="トピックIDでフィルタリング"),
    filter_date_start: Optional[str] = Query(None, description="開始日でフィルタリング（YYYY-MM-DD）"),
    filter_date_end: Optional[str] = Query(None, description="終了日でフィルタリング（YYYY-MM-DD）"),
    current_user: Any = Depends(deps.get_current_user),
) -> Any:
    """
    発言を検索する
    """
    result = services.search.search_statements(
        db=db,
        query=q,
        skip=skip,
        limit=limit,
        filter_party=filter_party,
        filter_topic=filter_topic,
        filter_date_start=filter_date_start,
        filter_date_end=filter_date_end
    )
    
    return {
        "statements": result["statements"],
        "total": result["total"],
        "next_cursor": result["next_cursor"]
    }


@router.get("/all", response_model=SearchResult)
def search_all(
    db: Session = Depends(deps.get_db),
    q: str = Query(..., description="検索キーワード"),
    skip: int = Query(0, description="スキップ数"),
    limit: int = Query(20, description="取得上限"),
    filter_party: Optional[str] = Query(None, description="政党IDでフィルタリング"),
    filter_topic: Optional[str] = Query(None, description="トピックIDでフィルタリング"),
    filter_date_start: Optional[str] = Query(None, description="開始日でフィルタリング（YYYY-MM-DD）"),
    filter_date_end: Optional[str] = Query(None, description="終了日でフィルタリング（YYYY-MM-DD）"),
    current_user: Any = Depends(deps.get_current_user),
) -> Any:
    """
    全てのエンティティを検索する
    """
    result = services.search.search_all(
        db=db,
        query=q,
        skip=skip,
        limit=limit,
        filter_party=filter_party,
        filter_topic=filter_topic,
        filter_date_start=filter_date_start,
        filter_date_end=filter_date_end
    )
    
    return result