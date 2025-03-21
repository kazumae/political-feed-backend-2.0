from app.api.v1.endpoints import (
    auth,
    comments,
    health,
    mypage,
    parties,
    politicians,
    search,
    statements,
    topics,
    users,
)
from fastapi import APIRouter

api_router = APIRouter()

# 各エンドポイントのルーターを登録
api_router.include_router(auth.router, prefix="/auth", tags=["認証"])
api_router.include_router(users.router, prefix="/users", tags=["ユーザー"])
api_router.include_router(
    mypage.router, prefix="/users/me", tags=["マイページ"]
)
api_router.include_router(
    politicians.router, prefix="/politicians", tags=["政治家"]
)
api_router.include_router(
    topics.router, prefix="/topics", tags=["トピック"]
)
api_router.include_router(
    statements.router, prefix="/statements", tags=["発言"]
)
api_router.include_router(
    parties.router, prefix="/parties", tags=["政党"]
)
api_router.include_router(
    comments.router, prefix="/comments", tags=["コメント"]
)
api_router.include_router(
    search.router, prefix="/search", tags=["検索"]
)
api_router.include_router(
    health.router, tags=["ヘルスチェック"]
)