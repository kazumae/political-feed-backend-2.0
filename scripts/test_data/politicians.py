"""
政治家テストデータ作成モジュール
"""
import json
import random
from datetime import datetime

from app.models.party import Party
from app.models.politician import Politician, PoliticianDetail, PoliticianParty
from sqlalchemy.orm import Session


def create_test_politicians(db: Session, parties=None):
    """
    テスト用の政治家データを作成
    """
    print("政治家データを作成中...")
    
    # 政党を取得
    if parties is None:
        parties = db.query(Party).all()
    
    if not parties:
        print("政党データが存在しません。先に政党データを作成してください。")
        return []
    
    politicians_data = [
        {
            "name": "山田太郎",
            "name_kana": "ヤマダタロウ",
            "role": "代表",
            "status": "active",
            "image_url": "https://randomuser.me/api/portraits/men/20.jpg",
            "profile_summary": "元財務大臣。経済政策に詳しい。",
            "party_id": parties[0].id,  # 自民党
        },
        {
            "name": "鈴木花子",
            "name_kana": "スズキハナコ",
            "role": "幹事長",
            "status": "active",
            "image_url": "https://randomuser.me/api/portraits/women/20.jpg",
            "profile_summary": "元厚生労働大臣。社会保障政策に詳しい。",
            "party_id": parties[0].id,  # 自民党
        },
        {
            "name": "佐藤健太",
            "name_kana": "サトウケンタ",
            "role": "代表",
            "status": "active",
            "image_url": "https://randomuser.me/api/portraits/men/21.jpg",
            "profile_summary": "元外務大臣。外交政策に詳しい。",
            "party_id": parties[1].id,  # 立憲民主党
        },
        {
            "name": "田中美咲",
            "name_kana": "タナカミサキ",
            "role": "幹事長",
            "status": "active",
            "image_url": "https://randomuser.me/api/portraits/women/21.jpg",
            "profile_summary": "元環境大臣。環境政策に詳しい。",
            "party_id": parties[1].id,  # 立憲民主党
        },
        {
            "name": "伊藤誠",
            "name_kana": "イトウマコト",
            "role": "代表",
            "status": "active",
            "image_url": "https://randomuser.me/api/portraits/men/22.jpg",
            "profile_summary": "元文部科学大臣。教育政策に詳しい。",
            "party_id": parties[2].id,  # 公明党
        },
    ]
    
    politician_objects = []
    for pol_data in politicians_data:
        # 政治家基本情報
        politician = Politician(
            name=pol_data["name"],
            name_kana=pol_data["name_kana"],
            current_party_id=pol_data["party_id"],
            role=pol_data["role"],
            status=pol_data["status"],
            image_url=pol_data["image_url"],
            profile_summary=pol_data["profile_summary"],
        )
        db.add(politician)
        db.flush()  # IDを取得するためにflush
        
        # 政治家詳細情報
        birth_year = random.randint(1950, 1980)
        birth_month = random.randint(1, 12)
        birth_day = random.randint(1, 28)
        
        politician_detail = PoliticianDetail(
            politician_id=politician.id,
            birth_date=datetime(birth_year, birth_month, birth_day),
            birth_place=["東京都", "大阪府", "愛知県", "福岡県", "北海道"][random.randint(0, 4)],
            education=json.dumps([
                {"year": birth_year + 18, "school": "○○大学", "degree": "学士"},
                {"year": birth_year + 22, "school": "△△大学院", "degree": "修士"},
            ]),
            career=json.dumps([
                {"year": birth_year + 23, "position": "○○株式会社入社"},
                {"year": birth_year + 30, "position": "△△議員秘書"},
                {"year": birth_year + 35, "position": "□□市議会議員"},
                {"year": birth_year + 40, "position": "国会議員初当選"},
            ]),
            election_history=json.dumps([
                {"year": birth_year + 40, "election": "衆議院選挙", "result": "当選"},
                {"year": birth_year + 43, "election": "衆議院選挙", "result": "当選"},
                {"year": birth_year + 47, "election": "衆議院選挙", "result": "当選"},
            ]),
            website_url=f"https://example.com/{politician.name}",
            social_media=json.dumps({
                "twitter": f"https://twitter.com/{politician.name}",
                "facebook": f"https://facebook.com/{politician.name}",
            }),
        )
        db.add(politician_detail)
        
        # 政治家所属政党履歴
        politician_party = PoliticianParty(
            politician_id=politician.id,
            party_id=pol_data["party_id"],
            joined_date=datetime(birth_year + 40, 1, 1),
            is_current=True,
            role=pol_data["role"],
        )
        db.add(politician_party)
        
        politician_objects.append(politician)
    
    db.commit()
    print(f"政治家データを作成しました: {len(politicians_data)}件")
    return politician_objects