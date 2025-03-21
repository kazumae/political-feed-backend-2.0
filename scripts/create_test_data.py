#!/usr/bin/env python
"""
テストデータ登録用スクリプト
"""
import os
import sys
import uuid
from datetime import datetime, timedelta

# プロジェクトのルートディレクトリをPythonパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.security import get_password_hash
from app.db.base import Base
from app.models.comment import Comment
from app.models.party import Party
from app.models.politician import Politician
from app.models.statement import Statement
from app.models.topic import Topic
from app.models.user import User
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# データベース接続設定
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# テーブル作成
Base.metadata.create_all(bind=engine)


def create_test_data():
    """テストデータを作成する"""
    db = SessionLocal()
    try:
        # ユーザーデータ作成
        print("ユーザーデータを作成中...")
        users = []
        for i in range(10):
            user = User(
                id=str(uuid.uuid4()),
                username=f"testuser{i}",
                email=f"test{i}@example.com",
                password_hash=get_password_hash("password"),
                role="user",
                status="active",
                email_verified=True
            )
            users.append(user)
            db.add(user)
        
        # 管理者ユーザー
        admin = User(
            id=str(uuid.uuid4()),
            username="admin",
            email="admin@example.com",
            password_hash=get_password_hash("adminpassword"),
            role="admin",
            status="active",
            email_verified=True
        )
        users.append(admin)
        db.add(admin)
        
        # モデレーターユーザー
        moderator = User(
            id=str(uuid.uuid4()),
            username="moderator",
            email="moderator@example.com",
            password_hash=get_password_hash("moderatorpassword"),
            role="moderator",
            status="active",
            email_verified=True
        )
        users.append(moderator)
        db.add(moderator)
        
        db.commit()
        print(f"ユーザーデータを作成しました: {len(users)}件")
        
        # 政党データ作成
        print("政党データを作成中...")
        parties = []
        party_names = ["自由民主党", "立憲民主党", "公明党", "日本維新の会", "国民民主党"]
        for name in party_names:
            party = Party(
                id=str(uuid.uuid4()),
                name=name,
                short_name=name[:2],
                status="active",
                founded_date=datetime(2000, 1, 1),
                description=f"{name}の説明文です。"
            )
            parties.append(party)
            db.add(party)
        db.commit()
        print(f"政党データを作成しました: {len(parties)}件")
        
        # 政治家データ作成
        print("政治家データを作成中...")
        politicians = []
        politician_names = ["田中太郎", "鈴木一郎", "佐藤花子", "高橋次郎", "伊藤三郎"]
        for i, name in enumerate(politician_names):
            politician = Politician(
                id=str(uuid.uuid4()),
                name=name,
                name_kana=f"テスト{i}",
                current_party_id=parties[i % len(parties)].id,
                role="議員",
                status="active"
            )
            politicians.append(politician)
            db.add(politician)
        db.commit()
        print(f"政治家データを作成しました: {len(politicians)}件")
        
        # トピックデータ作成
        print("トピックデータを作成中...")
        topics = []
        topic_names = ["経済", "外交", "環境"]
        for name in topic_names:
            topic = Topic(
                id=str(uuid.uuid4()),
                name=name,
                slug=name.lower(),
                description=f"{name}に関するトピックです。",
                category="economy",
                status="active"
            )
            topics.append(topic)
            db.add(topic)
        db.commit()
        print(f"トピックデータを作成しました: {len(topics)}件")
        
        # 発言データ作成
        print("発言データを作成中...")
        statements = []
        for i in range(10):
            politician = politicians[i % len(politicians)]
            statement = Statement(
                id=str(uuid.uuid4()),
                politician_id=politician.id,
                title=f"{politician.name}の発言{i+1}",
                content=f"これは{politician.name}の発言{i+1}です。",
                statement_date=datetime.now() - timedelta(days=i),
                source="記者会見",
                source_url=f"https://example.com/source/{i}",
                context="記者会見にて",
                status="published",
                importance=50
            )
            statements.append(statement)
            db.add(statement)
            
            # 発言とトピックの関連付け
            for topic in topics[:2]:
                statement.topics.append(topic)
        db.commit()
        print(f"発言データを作成しました: {len(statements)}件")
        
        # コメントデータ作成
        print("コメントデータを作成中...")
        comments = []
        for i in range(20):
            user = users[i % len(users)]
            statement = statements[i % len(statements)]
            comment = Comment(
                id=str(uuid.uuid4()),
                statement_id=statement.id,
                user_id=user.id,
                content=f"これは{user.username}による{statement.title}へのコメント{i+1}です。",
                status="published"
            )
            comments.append(comment)
            db.add(comment)
        db.commit()
        print(f"コメントデータを作成しました: {len(comments)}件")
        
    except Exception as e:
        db.rollback()
        print(f"エラーが発生しました: {e}")
        raise
    finally:
        db.close()
    
    print("テストデータの作成が完了しました")


if __name__ == "__main__":
    create_test_data()