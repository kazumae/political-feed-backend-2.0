from typing import Dict, List, Optional

from app import services
from app.models.politician import Politician
from app.models.statement import Statement
from app.models.topic import Topic
from sqlalchemy import or_
from sqlalchemy.orm import Session


def search_statements(
    db: Session,
    query: str,
    skip: int = 0,
    limit: int = 20,
    filter_party: Optional[str] = None,
    filter_topic: Optional[str] = None,
    filter_date_start: Optional[str] = None,
    filter_date_end: Optional[str] = None
) -> Dict:
    """
    発言を検索する
    
    Args:
        db: データベースセッション
        query: 検索クエリ
        skip: スキップ数
        limit: 取得上限
        filter_party: 政党IDでフィルタリング
        filter_topic: トピックIDでフィルタリング
        filter_date_start: 開始日でフィルタリング
        filter_date_end: 終了日でフィルタリング
        
    Returns:
        検索結果
    """
    # 発言を検索
    statements = services.statement.get_statements(
        db=db,
        skip=skip,
        limit=limit,
        sort="date_desc",
        filter_party=filter_party,
        filter_topic=filter_topic,
        filter_date_start=filter_date_start,
        filter_date_end=filter_date_end,
        search=query
    )
    
    # 発言数を取得
    total = services.statement.count_statements(
        db=db,
        filter_party=filter_party,
        filter_topic=filter_topic,
        filter_date_start=filter_date_start,
        filter_date_end=filter_date_end,
        search=query
    )
    
    # 次のカーソルを計算
    next_cursor = None
    if skip + limit < total:
        next_cursor = str(skip + limit)
    
    return {
        "statements": statements,
        "total": total,
        "next_cursor": next_cursor
    }


def search_politicians(
    db: Session,
    query: str,
    skip: int = 0,
    limit: int = 20,
    filter_party: Optional[str] = None
) -> Dict:
    """
    政治家を検索する
    
    Args:
        db: データベースセッション
        query: 検索クエリ
        skip: スキップ数
        limit: 取得上限
        filter_party: 政党IDでフィルタリング
        
    Returns:
        検索結果
    """
    # 政治家を検索
    query_obj = db.query(Politician).filter(
        or_(
            Politician.name.ilike(f"%{query}%"),
            Politician.name_kana.ilike(f"%{query}%"),
            Politician.profile_summary.ilike(f"%{query}%")
        )
    )
    
    # 政党でフィルタリング
    if filter_party:
        query_obj = query_obj.filter(Politician.current_party_id == filter_party)
    
    # 総数を取得
    total = query_obj.count()
    
    # 結果を取得
    politicians = query_obj.offset(skip).limit(limit).all()
    
    # 次のカーソルを計算
    next_cursor = None
    if skip + limit < total:
        next_cursor = str(skip + limit)
    
    return {
        "politicians": politicians,
        "total": total,
        "next_cursor": next_cursor
    }


def search_topics(
    db: Session,
    query: str,
    skip: int = 0,
    limit: int = 20
) -> Dict:
    """
    トピックを検索する
    
    Args:
        db: データベースセッション
        query: 検索クエリ
        skip: スキップ数
        limit: 取得上限
        
    Returns:
        検索結果
    """
    # トピックを検索
    query_obj = db.query(Topic).filter(
        or_(
            Topic.name.ilike(f"%{query}%"),
            Topic.description.ilike(f"%{query}%")
        )
    ).filter(Topic.status == "active")
    
    # 総数を取得
    total = query_obj.count()
    
    # 結果を取得
    topics = query_obj.offset(skip).limit(limit).all()
    
    # 次のカーソルを計算
    next_cursor = None
    if skip + limit < total:
        next_cursor = str(skip + limit)
    
    return {
        "topics": topics,
        "total": total,
        "next_cursor": next_cursor
    }


def search_all(
    db: Session,
    query: str,
    skip: int = 0,
    limit: int = 20,
    filter_party: Optional[str] = None,
    filter_topic: Optional[str] = None,
    filter_date_start: Optional[str] = None,
    filter_date_end: Optional[str] = None
) -> Dict:
    """
    全てのエンティティを検索する
    
    Args:
        db: データベースセッション
        query: 検索クエリ
        skip: スキップ数
        limit: 取得上限
        filter_party: 政党IDでフィルタリング
        filter_topic: トピックIDでフィルタリング
        filter_date_start: 開始日でフィルタリング
        filter_date_end: 終了日でフィルタリング
        
    Returns:
        検索結果
    """
    # 各エンティティを検索
    statements_result = search_statements(
        db=db,
        query=query,
        skip=skip,
        limit=limit,
        filter_party=filter_party,
        filter_topic=filter_topic,
        filter_date_start=filter_date_start,
        filter_date_end=filter_date_end
    )
    
    politicians_result = search_politicians(
        db=db,
        query=query,
        skip=skip,
        limit=limit,
        filter_party=filter_party
    )
    
    topics_result = search_topics(
        db=db,
        query=query,
        skip=skip,
        limit=limit
    )
    
    # 次のカーソルを計算
    next_cursor = None
    if (statements_result["next_cursor"] or 
        politicians_result["next_cursor"] or 
        topics_result["next_cursor"]):
        next_cursor = str(skip + limit)
    
    return {
        "statements": statements_result["statements"],
        "total_statements": statements_result["total"],
        "politicians": politicians_result["politicians"],
        "total_politicians": politicians_result["total"],
        "topics": topics_result["topics"],
        "total_topics": topics_result["total"],
        "query": query,
        "next_cursor": next_cursor
    }