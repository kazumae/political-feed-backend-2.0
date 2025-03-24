from typing import Any, List, Optional

from app import services
from app.api import deps
from app.schemas.party import Party as PartySchema
from app.schemas.party import PartyCreate, PartyDetail, PartyUpdate
from app.schemas.party_topic import PartyTopicStances
from app.schemas.politician import Politician as PoliticianSchema
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/", response_model=List[PartySchema])
def read_parties(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = Query(None, description="ステータスでフィルタリング"),
    search: Optional[str] = Query(None, description="名前で検索"),
) -> Any:
    """
    政党一覧を取得する（認証不要）
    """
    parties = services.party.get_parties(
        db, skip=skip, limit=limit, status=status, search=search
    )
    return parties


@router.post("/", response_model=PartySchema, status_code=status.HTTP_201_CREATED)
def create_party(
    *,
    db: Session = Depends(deps.get_db),
    party_in: PartyCreate,
    current_user: Any = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    新規政党を作成する（管理者のみ）
    """
    party = services.party.create_party(db, obj_in=party_in)
    return party


@router.get("/{id}", response_model=PartyDetail)
def read_party(
    *,
    db: Session = Depends(deps.get_db),
    id: str = Path(..., description="政党ID"),
) -> Any:
    """
    政党の詳細情報を取得する（認証不要）
    """
    party = services.party.get_party(db, id=id)
    if not party:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="政党が見つかりません",
        )
    
    # 詳細情報を取得
    details = services.party.get_party_detail(db, party_id=id)
    
    # 所属政治家数を取得
    members_count = services.party.get_party_members_count(db, party_id=id)
    
    # 結果を結合
    result = PartyDetail.model_validate(party)
    if details:
        result.president = details.president
        result.headquarters = details.headquarters
        result.ideology = details.ideology
        result.website_url = details.website_url
        result.social_media = details.social_media
        result.history = details.history
        result.additional_info = details.additional_info
    
    result.members_count = members_count
    
    return result


@router.put("/{id}", response_model=PartySchema)
def update_party(
    *,
    db: Session = Depends(deps.get_db),
    id: str = Path(..., description="政党ID"),
    party_in: PartyUpdate,
    current_user: Any = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    政党情報を更新する（管理者のみ）
    """
    party = services.party.get_party(db, id=id)
    if not party:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="政党が見つかりません",
        )
    party = services.party.update_party(
        db, db_obj=party, obj_in=party_in
    )
    return party


@router.delete("/{id}", response_model=PartySchema)
def delete_party(
    *,
    db: Session = Depends(deps.get_db),
    id: str = Path(..., description="政党ID"),
    current_user: Any = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    政党を削除する（管理者のみ）
    """
    party = services.party.get_party(db, id=id)
    if not party:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="政党が見つかりません",
        )
    party = services.party.delete_party(db, id=id)
    return party


@router.get("/{party_id}/politicians", response_model=List[PoliticianSchema])
def read_party_politicians(
    *,
    db: Session = Depends(deps.get_db),
    party_id: str = Path(..., description="政党ID"),
    skip: int = 0,
    limit: int = 100,
    role: Optional[str] = Query(None, description="役職でフィルタリング"),
) -> Any:
    """
    政党に所属する政治家一覧を取得する（認証不要）
    """
    # 政党が存在するか確認
    party = services.party.get_party(db, id=party_id)
    if not party:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="政党が見つかりません",
        )
    
    politicians = services.politician.get_politicians_by_party(
        db, party_id=party_id, skip=skip, limit=limit, role=role
    )
    
    return politicians


@router.get("/{party_id}/topics", response_model=PartyTopicStances)
def read_party_topics(
    *,
    db: Session = Depends(deps.get_db),
    party_id: str = Path(..., description="政党ID"),
) -> Any:
    """
    政党のトピック別スタンス一覧を取得する（認証不要）
    """
    # 政党が存在するか確認
    party = services.party.get_party(db, id=party_id)
    if not party:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="政党が見つかりません",
        )
    
    # 政党の発言からトピック別スタンスを集計
    topic_stances = services.statement.get_party_statement_topics(
        db, party_id=party_id
    )
    
    # 結果を返す
    result = {
        "party_id": party.id,
        "party_name": party.name,
        "topics": topic_stances
    }
    
    return result