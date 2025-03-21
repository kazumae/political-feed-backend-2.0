"""
ユーザーテストデータ作成モジュール
"""
from app.core.security import get_password_hash
from app.models.user import User
from sqlalchemy.orm import Session


def create_test_users(db: Session):
    """
    テスト用のユーザーデータを作成
    """
    print("ユーザーデータを作成中...")
    
    # 既存のユーザーをチェック
    existing_admin = db.query(User).filter(User.email == "admin@example.com").first()
    existing_moderator = db.query(User).filter(User.email == "moderator@example.com").first()
    
    # 管理者ユーザー
    if not existing_admin:
        admin_user = User(
            username="admin",
            email="admin@example.com",
            password_hash=get_password_hash("admin123"),
            role="admin",
            status="active",
            email_verified=True,
            profile_image="https://randomuser.me/api/portraits/men/1.jpg",
        )
        db.add(admin_user)
        print("管理者ユーザーを作成しました")
    else:
        print("管理者ユーザーは既に存在します")
    
    # 一般ユーザー
    created_users = 0
    for i in range(1, 11):  # 10人の一般ユーザー
        existing_user = db.query(User).filter(User.email == f"user{i}@example.com").first()
        if not existing_user:
            user = User(
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
            db.add(user)
            created_users += 1
    
    # モデレーターユーザー
    if not existing_moderator:
        moderator = User(
            username="moderator",
            email="moderator@example.com",
            password_hash=get_password_hash("moderator123"),
            role="moderator",
            status="active",
            email_verified=True,
            profile_image="https://randomuser.me/api/portraits/men/12.jpg",
        )
        db.add(moderator)
        created_users += 1
        print("モデレーターユーザーを作成しました")
    else:
        print("モデレーターユーザーは既に存在します")
    
    db.commit()
    print(f"ユーザーデータを作成しました: {created_users}件")
