from typing import Any, List, Optional

from app import services
from app.api import deps
from app.models.politician import Politician
from app.schemas.politician import Politician as PoliticianSchema
from app.schemas.politician import (
    PoliticianCreate,
    PoliticianDetail,
    PoliticianDetailCreate,
    PoliticianDetailUpdate,
    PoliticianParty,
    PoliticianPartyCreate,
    PoliticianPartyUpdate,
    PoliticianUpdate,
    PoliticianWithDetails,
)
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/", response_model=List[PoliticianSchema])
def read_politicians(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = Query(None, description="ステータスでフィルタリング"),
    party_id: Optional[str] = Query(None, description="政党IDでフィルタリング"),
    search: Optional[str] = Query(None, description="名前で検索"),
    current_user: Any = Depends(deps.get_current_user),
) -> Any:
    """
    政治家一覧を取得する
    """
    politicians = services.politician.get_politicians(
        db, skip=skip, limit=limit, status=status, 
        party_id=party_id, search=search
    )
    return politicians


@router.post("/", response_model=PoliticianSchema, status_code=status.HTTP_201_CREATED)
def create_politician(
    *,
    db: Session = Depends(deps.get_db),
    politician_in: PoliticianCreate,
    current_user: Any = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    新規政治家を作成する（管理者のみ）
    """
    politician = services.politician.create_politician(db, obj_in=politician_in)
    return politician


@router.get("/{id}", response_model=PoliticianWithDetails)
def read_politician(
    *,
    db: Session = Depends(deps.get_db),
    id: str = Path(..., description="政治家ID"),
    current_user: Any = Depends(deps.get_current_user),
) -> Any:
    """
    政治家の詳細情報を取得する
    """
    politician = services.politician.get_politician(db, id=id)
    if not politician:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="政治家が見つかりません",
        )
    
    # 詳細情報を取得
    details = services.politician.get_politician_detail(db, politician_id=id)
    
    # 所属政党履歴を取得
    party_history = services.politician.get_politician_parties(db, politician_id=id)
    
    # 結果を結合
    result = PoliticianWithDetails.model_validate(politician)
    result.details = details
    result.party_history = party_history
    
    return result


@router.put("/{id}", response_model=PoliticianSchema)
def update_politician(
    *,
    db: Session = Depends(deps.get_db),
    id: str = Path(..., description="政治家ID"),
    politician_in: PoliticianUpdate,
    current_user: Any = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    政治家情報を更新する（管理者のみ）
    """
    politician = services.politician.get_politician(db, id=id)
    if not politician:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="政治家が見つかりません",
        )
    politician = services.politician.update_politician(
        db, db_obj=politician, obj_in=politician_in
    )
    return politician


@router.delete("/{id}", response_model=PoliticianSchema)
def delete_politician(
    *,
    db: Session = Depends(deps.get_db),
    id: str = Path(..., description="政治家ID"),
    current_user: Any = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    政治家を削除する（管理者のみ）
    """
    politician = services.politician.get_politician(db, id=id)
    if not politician:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="政治家が見つかりません",
        )
    politician = services.politician.delete_politician(db, id=id)
    return politician


# 政治家詳細関連のエンドポイント

@router.post(
    "/{id}/details", 
    response_model=PoliticianDetail, 
    status_code=status.HTTP_201_CREATED
)
def create_politician_detail(
    *,
    db: Session = Depends(deps.get_db),
    id: str = Path(..., description="政治家ID"),
    detail_in: PoliticianDetailCreate,
    current_user: Any = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    政治家詳細情報を作成する（管理者のみ）
    """
    politician = services.politician.get_politician(db, id=id)
    if not politician:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="政治家が見つかりません",
        )
    
    # 既に詳細情報が存在するか確認
    existing_detail = services.politician.get_politician_detail(
        db, politician_id=id
    )
    if existing_detail:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="この政治家の詳細情報は既に存在します",
        )
    
    detail = services.politician.create_politician_detail(
        db, obj_in=detail_in, politician_id=id
    )
    return detail


@router.put("/{id}/details", response_model=PoliticianDetail)
def update_politician_detail(
    *,
    db: Session = Depends(deps.get_db),
    id: str = Path(..., description="政治家ID"),
    detail_in: PoliticianDetailUpdate,
    current_user: Any = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    政治家詳細情報を更新する（管理者のみ）
    """
    detail = services.politician.get_politician_detail(db, politician_id=id)
    if not detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="政治家詳細情報が見つかりません",
        )
    detail = services.politician.update_politician_detail(
        db, db_obj=detail, obj_in=detail_in
    )
    return detail


# 政治家所属政党履歴関連のエンドポイント

@router.get("/{id}/parties", response_model=List[PoliticianParty])
def read_politician_parties(
    *,
    db: Session = Depends(deps.get_db),
    id: str = Path(..., description="政治家ID"),
    current_user: Any = Depends(deps.get_current_user),
) -> Any:
    """
    政治家の所属政党履歴一覧を取得する
    """
    politician = services.politician.get_politician(db, id=id)
    if not politician:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="政治家が見つかりません",
        )
    
    parties = services.politician.get_politician_parties(db, politician_id=id)
    return parties


@router.post(
    "/{id}/parties", 
    response_model=PoliticianParty, 
    status_code=status.HTTP_201_CREATED
)
def create_politician_party(
    *,
    db: Session = Depends(deps.get_db),
    id: str = Path(..., description="政治家ID"),
    party_in: PoliticianPartyCreate,
    current_user: Any = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    政治家の所属政党履歴を作成する（管理者のみ）
    """
    # 政治家IDが一致するか確認
    if party_in.politician_id != id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="リクエストボディの政治家IDがパスパラメータと一致しません",
        )
    
    politician = services.politician.get_politician(db, id=id)
    if not politician:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="政治家が見つかりません",
        )
    
    party = services.politician.create_politician_party(db, obj_in=party_in)
    return party


@router.put("/parties/{party_id}", response_model=PoliticianParty)
def update_politician_party(
    *,
    db: Session = Depends(deps.get_db),
    party_id: str = Path(..., description="政治家所属政党履歴ID"),
    party_in: PoliticianPartyUpdate,
    current_user: Any = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    政治家の所属政党履歴を更新する（管理者のみ）
    """
    party = services.politician.get_politician_party(db, id=party_id)
    if not party:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="政治家所属政党履歴が見つかりません",
        )
    
    party = services.politician.update_politician_party(
        db, db_obj=party, obj_in=party_in
    )
    return party


@router.delete("/parties/{party_id}", response_model=PoliticianParty)
def delete_politician_party(
    *,
    db: Session = Depends(deps.get_db),
    party_id: str = Path(..., description="政治家所属政党履歴ID"),
    current_user: Any = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    政治家の所属政党履歴を削除する（管理者のみ）
    """
    party = services.politician.get_politician_party(db, id=party_id)
    if not party:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="政治家所属政党履歴が見つかりません",
        )
    
    party = services.politician.delete_politician_party(db, id=party_id)
    return party