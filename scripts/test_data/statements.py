"""
発言テストデータ作成モジュール
"""
import random
from datetime import datetime, timedelta

from app.models.politician import Politician
from app.models.statement import Statement, StatementTopic
from app.models.topic import Topic
from sqlalchemy.orm import Session


def create_test_statements(db: Session, politicians=None, topics=None):
    """
    テスト用の発言データを作成
    """
    print("発言データを作成中...")
    
    # 政治家とトピックを取得
    if politicians is None:
        politicians = db.query(Politician).all()
    
    if topics is None:
        topics = db.query(Topic).all()
    
    if not politicians or not topics:
        print("政治家またはトピックデータが存在しません。先にそれらのデータを作成してください。")
        return []
    
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
                f"{politician.name}は{random.choice(['党大会', '記者会見', '国会質疑'])}で、「{random.choice(['少子化対策', '経済対策', '外交政策'])}は{random.choice(['最重要課題', '優先課題'])}である」と強調した。",
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
            statement_date=stmt_data["statement_date"],
            context=stmt_data["context"],
            status="published",
            importance=stmt_data["importance"],
        )
        db.add(statement)
        db.flush()  # IDを取得するためにflush
        
        # 発言の出典情報はStatementに直接設定
        statement.source = stmt_data["source"]
        statement.source_url = stmt_data["source_url"]
        
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