import os
import sys

# プロジェクトのルートディレクトリをPythonパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 以下のimportはsys.pathを設定した後に行う必要があるため、ここに配置
# noqa: E402はFlake8のエラーを無視するためのコメント
from app.db.session import SessionLocal  # noqa: E402
from app.schemas.user import UserCreate  # noqa: E402
from app.services.user import create_user  # noqa: E402


def create_admin_user():
    """
    管理者ユーザーを作成する
    """
    db = SessionLocal()
    try:
        # 管理者ユーザーの作成
        admin_user = UserCreate(
            email="admin@example.com",
            username="admin",
            password="admin123",
            full_name="管理者",
            is_superuser=True,
            is_active=True
        )
        
        # ユーザーの作成
        user = create_user(db, obj_in=admin_user)
        print(f"管理者ユーザーが作成されました: {user.username} (ID: {user.id})")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    create_admin_user()