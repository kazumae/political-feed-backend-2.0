"""
コメントテストデータ作成モジュール
"""
import random
from datetime import datetime, timedelta

from app.models.comment import Comment
from app.models.statement import Statement
from app.models.user import User
from sqlalchemy.orm import Session


def create_test_comments(db: Session, statements=None):
    """
    テスト用のコメントデータを作成
    """
    print("コメントデータを作成中...")
    
    # 発言とユーザーを取得
    if statements is None:
        statements = db.query(Statement).all()
    
    users = db.query(User).filter(User.role == "user").all()
    
    if not statements or not users:
        print("発言またはユーザーデータが存在しません。先にそれらのデータを作成してください。")
        return []
    
    comments_data = []
    
    # 各発言に対して1〜3件のコメントを作成
    for statement in statements:
        # コメント数をランダムに設定
        num_comments = random.randint(1, 3)
        
        for i in range(num_comments):
            # コメント投稿者をランダムに選択
            user = random.choice(users)
            
            # コメント内容のテンプレート
            templates = [
                f"この発言には{random.choice(['賛成です', '反対です'])}。{random.choice(['もっと具体的な政策を示してほしい', '国民の声を聞いてほしい'])}と思います。",
                f"{random.choice(['興味深い発言です', '重要な指摘だと思います'])}。{random.choice(['今後の展開に期待します', '具体的な行動が伴うことを願います'])}。",
                f"{random.choice(['この点については', 'この発言に関しては'])}、{random.choice(['もっと議論が必要だと思います', '賛同します', '疑問が残ります'])}。",
                f"{random.choice(['なるほど', '確かに'])}、{random.choice(['その通りだと思います', '一理あると思います'])}。{random.choice(['ただ', 'しかし'])}、{random.choice(['課題も多いのでは', '実現は難しいのでは'])}？",
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
    return comment_objects