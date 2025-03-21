import json
import os
import random
import sys
from datetime import datetime, timedelta

# プロジェクトのルートディレクトリをPythonパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 環境変数を設定してテスト環境を有効にする
os.environ["TESTING"] = "True"

# 以下のimportはsys.pathを設定した後に行う
from app.core.security import get_password_hash  # noqa: E402
from app.models.comment import Comment  # noqa: E402
from app.models.party import Party, PartyDetail  # noqa: E402
from app.models.politician import (  # noqa: E402
    Politician,
    PoliticianDetail,
    PoliticianParty,
)
from app.models.statement import Statement, StatementTopic  # noqa: E402
from app.models.topic import Topic, TopicRelation  # noqa: E402
from app.models.user import User  # noqa: E402
from tests.db_session import Base, TestSessionLocal, engine  # noqa: E402

# 設定をオーバーライド
from tests.override_config import settings  # noqa: E402


def create_test_data():
    """
    テストデータを作成する
    """
    # テスト用のデータベースを初期化
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = TestSessionLocal()
    try:
        # ユーザーデータ
        create_test_users(db)
        
        # 政党データ
        create_test_parties(db)
        
        # 政治家データ
        create_test_politicians(db)
        
        # トピックデータ
        create_test_topics(db)
        
        # 発言データ
        create_test_statements(db)
        
        # コメントデータ
        create_test_comments(db)
        
        print("テストデータの作成が完了しました")
        
    except Exception as e:
        db.rollback()
        print(f"エラーが発生しました: {e}")
        raise
    finally:
        db.close()


def create_test_users(db):
    """
    テスト用のユーザーデータを作成
    """
    print("ユーザーデータを作成中...")
    
    # 管理者ユーザー
    admin_user = User(
        username="admin",
        email="admin@example.com",
        password_hash=get_password_hash("admin123"),
        role="admin",
        status="active",
        email_verified=True,
        profile_image="https://randomuser.me/api/portraits/men/1.jpg",
    )
    
    # 一般ユーザー
    users = [
        User(
            username=f"user{i}",
            email=f"user{i}@example.com",
            password_hash=get_password_hash(f"password{i}"),
            role="user",
            status="active",
            email_verified=True,
            profile_image=f"https://randomuser.me/api/portraits/men/{i+2}.jpg" 
                if i % 2 == 0 else 
                f"https://randomuser.me/api/portraits/women/{i+2}.jpg",
        )
        for i in range(1, 11)  # 10人の一般ユーザー
    ]
    
    # モデレーターユーザー
    moderator = User(
        username="moderator",
        email="moderator@example.com",
        password_hash=get_password_hash("moderator123"),
        role="moderator",
        status="active",
        email_verified=True,
        profile_image="https://randomuser.me/api/portraits/men/12.jpg",
    )
    
    db.add(admin_user)
    db.add(moderator)
    for user in users:
        db.add(user)
    
    db.commit()
    print(f"ユーザーデータを作成しました: {len(users) + 2}件")


def create_test_parties(db):
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


def create_test_politicians(db):
    """
    テスト用の政治家データを作成
    """
    print("政治家データを作成中...")
    
    # 政党を取得
    parties = db.query(Party).all()
    if not parties:
        print("政党データが存在しません。先に政党データを作成してください。")
        return
    
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


def create_test_topics(db):
    """
    テスト用のトピックデータを作成
    """
    print("トピックデータを作成中...")
    
    topics_data = [
        {
            "name": "経済政策",
            "slug": "economy",
            "description": "経済成長、財政政策、金融政策などに関するトピック",
            "category": "economy",
            "importance": 90,
            "icon_url": "https://example.com/icons/economy.png",
            "color_code": "#00ff00",
        },
        {
            "name": "外交・安全保障",
            "slug": "foreign_policy",
            "description": "外交関係、安全保障政策、防衛政策などに関するトピック",
            "category": "foreign_policy",
            "importance": 85,
            "icon_url": "https://example.com/icons/foreign_policy.png",
            "color_code": "#0000ff",
        },
        {
            "name": "社会保障",
            "slug": "social_welfare",
            "description": "医療、年金、介護、生活保護などに関するトピック",
            "category": "social_welfare",
            "importance": 80,
            "icon_url": "https://example.com/icons/social_welfare.png",
            "color_code": "#ff00ff",
        },
    ]
    
    topic_objects = []
    for topic_data in topics_data:
        topic = Topic(
            name=topic_data["name"],
            slug=topic_data["slug"],
            description=topic_data["description"],
            category=topic_data["category"],
            importance=topic_data["importance"],
            icon_url=topic_data["icon_url"],
            color_code=topic_data["color_code"],
            status="active",
        )
        db.add(topic)
        topic_objects.append(topic)
    
    db.commit()
    
    # トピック間の関連を作成
    for i in range(len(topic_objects)):
        for j in range(i + 1, len(topic_objects)):
            relation_type = ["related", "parent_child", "opposite"][random.randint(0, 2)]
            
            # 関連の強さをランダムに設定
            strength = random.randint(30, 90)
            
            topic_relation = TopicRelation(
                parent_topic_id=topic_objects[i].id,
                child_topic_id=topic_objects[j].id,
                relation_type=relation_type,
                strength=strength,
            )
            db.add(topic_relation)
    
    db.commit()
    print(f"トピックデータを作成しました: {len(topics_data)}件")
    return topic_objects


def create_test_statements(db):
    """
    テスト用の発言データを作成
    """
    print("発言データを作成中...")
    
    # 政治家とトピックを取得
    politicians = db.query(Politician).all()
    topics = db.query(Topic).all()
    
    if not politicians or not topics:
        print("政治家またはトピックデータが存在しません。先にそれらのデータを作成してください。")
        return
    
    statements_data = []
    
    # 各政治家に対して複数の発言を作成
    for politician in politicians:
        # 各政治家に2〜3件の発言を作成（テスト用に少なめに）
        num_statements = random.randint(2, 3)
        
        for i in range(num_statements):
            # 発言日時をランダムに設定（過去1年以内）
            days_ago = random.randint(1, 365)
            statement_date = datetime.now() - timedelta(days=days_ago)
            
            # 発言内容のテンプレート
            templates = [
                f"{politician.name}は、「{random.choice(['経済成長', '社会保障', '教育改革'])}について、{random.choice(['積極的に取り組む', '慎重に検討する'])}必要がある」と述べた。",
                f"{politician.name}は記者会見で、「{random.choice(['国民の生活', '日本の安全'])}を{random.choice(['守るため', '実現するため'])}に、{random.choice(['新たな政策', '具体的な施策'])}を{random.choice(['検討している', '提案する'])}」と発言した。",
            ]
            
            statement_content = random.choice(templates)
            
            # 発言のタイトル
            title = statement_content[:30] + "..." if len(statement_content) > 30 else statement_content
            
            statement_data = {
                "politician_id": politician.id,
                "title": title,
                "content": statement_content,
                "source": random.choice(["記者会見", "国会答弁", "党大会"]),
                "source_url": f"https://example.com/source/{politician.id}/{i}",
                "statement_date": statement_date,
                "context": f"{statement_date.strftime('%Y年%m月%d日')}に行われた{random.choice(['記者会見', '国会質疑', '党大会'])}での発言。",
                "importance": random.randint(50, 90),
            }
            
            statements_data.append(statement_data)
    
    statement_objects = []
    for stmt_data in statements_data:
        statement = Statement(
            politician_id=stmt_data["politician_id"],
            title=stmt_data["title"],
            content=stmt_data["content"],
            source=stmt_data["source"],
            source_url=stmt_data["source_url"],
            statement_date=stmt_data["statement_date"],
            context=stmt_data["context"],
            status="published",
            importance=stmt_data["importance"],
        )
        db.add(statement)
        db.flush()  # IDを取得するためにflush
        
        # 発言に1〜2個のトピックをランダムに関連付け
        num_topics = min(random.randint(1, 2), len(topics))
        selected_topics = random.sample(topics, num_topics)
        
        for topic in selected_topics:
            # 関連度をランダムに設定
            relevance = random.randint(50, 90)
            
            statement_topic = StatementTopic(
                statement_id=statement.id,
                topic_id=topic.id,
                relevance=relevance,
            )
            db.add(statement_topic)
        
        statement_objects.append(statement)
    
    db.commit()
    print(f"発言データを作成しました: {len(statements_data)}件")
    return statement_objects


def create_test_comments(db):
    """
    テスト用のコメントデータを作成
    """
    print("コメントデータを作成中...")
    
    # 発言とユーザーを取得
    statements = db.query(Statement).all()
    users = db.query(User).filter(User.role == "user").all()
    
    if not statements or not users:
        print("発言またはユーザーデータが存在しません。先にそれらのデータを作成してください。")
        return
    
    comments_data = []
    
    # 各発言に対して1〜2件のコメントを作成（テスト用に少なめに）
    for statement in statements:
        # コメント数をランダムに設定
        num_comments = random.randint(1, 2)
        
        for i in range(num_comments):
            # コメント投稿者をランダムに選択
            user = random.choice(users)
            
            # コメント内容のテンプレート
            templates = [
                f"この発言には{random.choice(['賛成です', '反対です'])}。{random.choice(['もっと具体的な政策を示してほしい', '国民の声を聞いてほしい'])}と思います。",
                f"{random.choice(['興味深い発言です', '重要な指摘だと思います'])}。{random.choice(['今後の展開に期待します', '具体的な行動が伴うことを願います'])}。",
            ]
            
            comment_content = random.choice(templates)
            
            # コメント投稿日時をランダムに設定（発言日時以降）
            days_after = random.randint(0, 10)
            comment_date = statement.statement_date + timedelta(days=days_after)
            if comment_date > datetime.now():
                comment_date = datetime.now()
            
            comment_data = {
                "user_id": user.id,
                "statement_id": statement.id,
                "content": comment_content,
                "created_at": comment_date,
            }
            
            comments_data.append(comment_data)
    
    comment_objects = []
    for cmt_data in comments_data:
        comment = Comment(
            user_id=cmt_data["user_id"],
            statement_id=cmt_data["statement_id"],
            content=cmt_data["content"],
            status="published",
            created_at=cmt_data["created_at"],
            updated_at=cmt_data["created_at"],
        )
        db.add(comment)
        comment_objects.append(comment)
    
    db.commit()
    print(f"コメントデータを作成しました: {len(comments_data)}件")


if __name__ == "__main__":
    create_test_data()