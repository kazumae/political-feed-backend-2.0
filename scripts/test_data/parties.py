"""
政党テストデータ作成モジュール
"""
import json
import random
from datetime import datetime

from app.models.party import Party, PartyDetail
from sqlalchemy.orm import Session


def create_test_parties(db: Session):
    """
    テスト用の政党データを作成
    """
    print("政党データを作成中...")
    
    parties = [
        {
            "name": "自由民主党",
            "short_name": "自民党",
            "status": "active",
            "founded_date": datetime(1955, 11, 15),
            "logo_url": "https://example.com/ldp_logo.png",
            "color_code": "#ff0000",
            "description": "日本の保守政党。結党以来、ほぼ一貫して与党の座にある。",
        },
        {
            "name": "立憲民主党",
            "short_name": "立民",
            "status": "active",
            "founded_date": datetime(2017, 10, 2),
            "logo_url": "https://example.com/cdp_logo.png",
            "color_code": "#0000ff",
            "description": "リベラル系の野党第一党。",
        },
        {
            "name": "公明党",
            "short_name": "公明",
            "status": "active",
            "founded_date": datetime(1964, 11, 17),
            "logo_url": "https://example.com/komeito_logo.png",
            "color_code": "#ffff00",
            "description": "中道保守政党。自民党と連立を組んでいる。",
        },
        {
            "name": "日本維新の会",
            "short_name": "維新",
            "status": "active",
            "founded_date": datetime(2015, 10, 25),
            "logo_url": "https://example.com/ishin_logo.png",
            "color_code": "#ff00ff",
            "description": "大阪を拠点とする保守改革政党。",
        },
        {
            "name": "国民民主党",
            "short_name": "国民",
            "status": "active",
            "founded_date": datetime(2018, 5, 7),
            "logo_url": "https://example.com/dpfp_logo.png",
            "color_code": "#00ffff",
            "description": "中道政党。",
        },
    ]
    
    party_objects = []
    for party_data in parties:
        party = Party(
            name=party_data["name"],
            short_name=party_data["short_name"],
            status=party_data["status"],
            founded_date=party_data["founded_date"],
            logo_url=party_data["logo_url"],
            color_code=party_data["color_code"],
            description=party_data["description"],
        )
        db.add(party)
        db.flush()  # IDを取得するためにflush
        
        # 政党詳細情報
        party_detail = PartyDetail(
            party_id=party.id,
            headquarters="東京都千代田区永田町",
            ideology=json.dumps(["保守", "リベラル", "中道"][random.randint(0, 2)]),
            website_url=f"https://example.com/{party.short_name}",
            social_media=json.dumps({
                "twitter": f"https://twitter.com/{party.short_name}",
                "facebook": f"https://facebook.com/{party.short_name}",
            }),
            history=json.dumps([
                {"year": 2000, "event": "党大会開催"},
                {"year": 2010, "event": "党首選挙"},
                {"year": 2020, "event": "政策発表"},
            ]),
        )
        db.add(party_detail)
        party_objects.append(party)
    
    db.commit()
    print(f"政党データを作成しました: {len(parties)}件")
    return party_objects
