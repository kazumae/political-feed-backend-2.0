import importlib.util
import os
import sys

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.user import User
from app.schemas.token import TokenPayload
from app.services.user import get_user
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

# テスト環境の場合はTestSessionLocalをインポート
TestSessionLocal = None
if os.getenv("TESTING") == "True":
    try:
        # プロジェクトのルートディレクトリをPythonパスに追加
        sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        from tests.db_session import TestSessionLocal
        print("TestSessionLocal imported successfully")
    except ImportError as e:
        print(f"Failed to import TestSessionLocal: {e}")
        # インポートに失敗した場合は、SQLiteを使用するセッションを作成
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        # SQLiteエンジンの作成
        test_engine = create_engine(
            "sqlite:///./test.db",
            connect_args={"check_same_thread": False}  # SQLite用の設定
        )
        
        # セッションファクトリの作成
        TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
        print("Created fallback TestSessionLocal")

# OAuth2のトークン取得エンドポイント
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)


# テスト用のセッションを保持する変数
_test_db = None

def get_db():
    """
    リクエストごとにデータベースセッションを取得し、リクエスト完了後にクローズする
    テスト環境の場合はTestSessionLocalを使用する
    
    Yields:
        SQLAlchemy DBセッション
    """
    global _test_db
    print(f"TESTING environment variable: {os.getenv('TESTING')}")
    print(f"TestSessionLocal defined: {TestSessionLocal is not None}")
    
    if os.getenv("TESTING") == "True":
        # テスト環境では同じセッションを再利用
        if _test_db is None:
            if TestSessionLocal is not None:
                _test_db = TestSessionLocal()
                print(f"Created new TestSessionLocal: {_test_db}")
            else:
                _test_db = SessionLocal()
                print(f"Created new SessionLocal for testing: {_test_db}")
            
            # テスト用のユーザーを作成
            try:
                from app.core.security import get_password_hash
                from app.models.user import User

                # テスト用ユーザーのリスト
                test_users = [
                    {
                        "email": "test@example.com",
                        "username": "testuser",
                        "password": "password123",
                        "role": "user",
                        "status": "active"
                    },
                    {
                        "email": "test2@example.com",
                        "username": "testuser2",
                        "password": "password123",
                        "role": "user",
                        "status": "active"
                    },
                    {
                        "email": "inactive@example.com",
                        "username": "inactiveuser",
                        "password": "password123",
                        "role": "user",
                        "status": "inactive"
                    },
                    {
                        "email": "current@example.com",
                        "username": "currentuser",
                        "password": "password123",
                        "role": "user",
                        "status": "active"
                    }
                ]
                
                # 各テストユーザーを作成または更新
                for user_data in test_users:
                    test_user = _test_db.query(User).filter(User.email == user_data["email"]).first()
                    if test_user is None:
                        print(f"Creating test user: {user_data['email']}")
                        test_user = User(
                            email=user_data["email"],
                            username=user_data["username"],
                            password_hash=get_password_hash(user_data["password"]),
                            role=user_data["role"],
                            status=user_data["status"],
                            email_verified=True
                        )
                        _test_db.add(test_user)
                    else:
                        print(f"Updating test user: {user_data['email']}")
                        test_user.status = user_data["status"]
                
                _test_db.commit()
                
                # データベース内のユーザーを確認
                users = _test_db.query(User).all()
                print(f"Users in test database: {users}")
            except Exception as e:
                print(f"Error setting up test database: {e}")
        
        print(f"Using test database session: {_test_db}")
        db = _test_db
    else:
        # 通常環境では新しいセッションを作成
        db = SessionLocal()
    
    try:
        yield db
    finally:
        # テスト環境ではセッションを閉じない（再利用するため）
        if os.getenv("TESTING") != "True":
            db.close()


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    """
    現在のユーザーを取得する
    
    Args:
        db: データベースセッション
        token: JWTトークン
        
    Returns:
        現在のユーザーオブジェクト
        
    Raises:
        HTTPException: トークンが無効な場合
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
        print(f"トークンデータ: {token_data}")
        print(f"ユーザーID: {token_data.sub}")
    except (jwt.JWTError, ValidationError) as e:
        print(f"トークンデコードエラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="認証情報が無効です",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # データベース内のユーザーを確認
    all_users = db.query(User).all()
    print(f"データベース内のユーザー数: {len(all_users)}")
    for u in all_users:
        print(f"ユーザー: {u.id}, {u.email}, {u.username}")
    
    user = get_user(db, id=token_data.sub)
    if not user:
        print(f"ユーザーが見つかりません: {token_data.sub}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ユーザーが見つかりません",
        )
    print(f"ユーザーが見つかりました: {user.id}, {user.email}, {user.username}")
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    現在のアクティブなユーザーを取得する
    
    Args:
        current_user: 現在のユーザーオブジェクト
        
    Returns:
        現在のアクティブなユーザーオブジェクト
        
    Raises:
        HTTPException: ユーザーが非アクティブな場合
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="アカウントが無効です",
        )
    return current_user


def get_current_active_superuser(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    現在のアクティブな管理者ユーザーを取得する
    
    Args:
        current_user: 現在のユーザーオブジェクト
        
    Returns:
        現在のアクティブな管理者ユーザーオブジェクト
        
    Raises:
        HTTPException: ユーザーが管理者でない場合
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="管理者権限が必要です",
        )
    return current_user