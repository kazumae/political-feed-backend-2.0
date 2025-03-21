#!/usr/bin/env python
"""
テストデータを登録するスクリプト（Dockerコンテナ内で実行用）
"""
import importlib.util
import os
import sys

# 環境変数を設定
os.environ["TESTING"] = "False"  # 本番DBに接続するため、TESTINGはFalse

# 以下のimportはsys.pathを設定した後に行う
from app.db.session import SessionLocal

# テストデータ作成モジュールを直接インポート
current_dir = os.path.dirname(os.path.abspath(__file__))

def load_module(name, path):
    """
    指定されたパスからモジュールを動的にロードする
    """
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# 各モジュールをロード
users_module = load_module("users", os.path.join(current_dir, "test_data", "users.py"))
parties_module = load_module("parties", os.path.join(current_dir, "test_data", "parties.py"))
politicians_module = load_module("politicians", os.path.join(current_dir, "test_data", "politicians.py"))
topics_module = load_module("topics", os.path.join(current_dir, "test_data", "topics.py"))
statements_module = load_module("statements", os.path.join(current_dir, "test_data", "statements.py"))
comments_module = load_module("comments", os.path.join(current_dir, "test_data", "comments.py"))

# 各関数を取得
create_test_users = users_module.create_test_users
create_test_parties = parties_module.create_test_parties
create_test_politicians = politicians_module.create_test_politicians
create_test_topics = topics_module.create_test_topics
create_test_statements = statements_module.create_test_statements
create_test_comments = comments_module.create_test_comments


def create_test_data():
    """
    テストデータを作成する
    """
    db = SessionLocal()
    try:
        # ユーザーデータ
        create_test_users(db)
        
        # 政党データ
        parties = create_test_parties(db)
        
        # 政治家データ
        politicians = create_test_politicians(db, parties)
        
        # トピックデータ
        topics = create_test_topics(db)
        
        # 発言データ
        statements = create_test_statements(db, politicians, topics)
        
        # コメントデータ
        create_test_comments(db, statements)
        
        print("テストデータの作成が完了しました")
        
    except Exception as e:
        db.rollback()
        print(f"エラーが発生しました: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_test_data()