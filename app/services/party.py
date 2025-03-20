from typing import Dict, List, Optional, Union

from app.models.party import Party, PartyDetail
from app.models.politician import Politician
from app.schemas.party import PartyCreate, PartyUpdate
from sqlalchemy import func
from sqlalchemy.orm import Session


def get_party(db: Session, id: str) -> Optional[Party]:
    """
    IDで政党を取得する
    
    Args:
        db: データベースセッション
        id: 政党ID
        
    Returns:
        政党オブジェクト、存在しない場合はNone
    """
    return db.query(Party).filter(Party.id == id).first()


def get_party_by_name(db: Session, name: str) -> Optional[Party]:
    """
    名前で政党を取得する
    
    Args:
        db: データベースセッション
        name: 政党名
        
    Returns:
        政党オブジェクト、存在しない場合はNone
    """
    return db.query(Party).filter(Party.name == name).first()


def get_parties(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    status: Optional[str] = None,
    search: Optional[str] = None
) -> List[Party]:
    """
    政党一覧を取得する
    
    Args:
        db: データベースセッション
        skip: スキップ数
        limit: 取得上限
        status: ステータスでフィルタリング
        search: 名前で検索
        
    Returns:
        政党オブジェクトのリスト
    """
    query = db.query(Party)
    
    if status:
        query = query.filter(Party.status == status)
    
    if search:
        query = query.filter(
            Party.name.ilike(f"%{search}%") | 
            Party.short_name.ilike(f"%{search}%")
        )
    
    return query.offset(skip).limit(limit).all()


def create_party(
    db: Session, obj_in: PartyCreate
) -> Party:
    """
    新規政党を作成する
    
    Args:
        db: データベースセッション
        obj_in: 政党作成スキーマ
        
    Returns:
        作成された政党オブジェクト
    """
    db_obj = Party(
        name=obj_in.name,
        short_name=obj_in.short_name,
        status=obj_in.status,
        founded_date=obj_in.founded_date,
        disbanded_date=obj_in.disbanded_date,
        logo_url=obj_in.logo_url,
        color_code=obj_in.color_code,
        description=obj_in.description,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_party(
    db: Session, 
    *, 
    db_obj: Party, 
    obj_in: Union[PartyUpdate, Dict[str, any]]
) -> Party:
    """
    政党情報を更新する
    
    Args:
        db: データベースセッション
        db_obj: 更新対象の政党オブジェクト
        obj_in: 更新データ（PartyUpdateオブジェクトまたは辞書）
        
    Returns:
        更新された政党オブジェクト
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


def delete_party(db: Session, *, id: str) -> Party:
    """
    政党を削除する
    
    Args:
        db: データベースセッション
        id: 政党ID
        
    Returns:
        削除された政党オブジェクト
    """
    obj = db.query(Party).get(id)
    db.delete(obj)
    db.commit()
    return obj


def get_party_detail(
    db: Session, party_id: str
) -> Optional[PartyDetail]:
    """
    政党詳細を取得する
    
    Args:
        db: データベースセッション
        party_id: 政党ID
        
    Returns:
        政党詳細オブジェクト、存在しない場合はNone
    """
    return db.query(PartyDetail).filter(
        PartyDetail.party_id == party_id
    ).first()


def get_party_members_count(db: Session, *, party_id: str) -> int:
    """
    政党の所属議員数を取得する
    
    Args:
        db: データベースセッション
        party_id: 政党ID
        
    Returns:
        所属議員数
    """
    return db.query(func.count(Politician.id)).filter(
        Politician.current_party_id == party_id,
        Politician.status == "active"
    ).scalar() or 0