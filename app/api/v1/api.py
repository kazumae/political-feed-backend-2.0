# 未実装のエンドポイントはコメントアウト
from app.api.v1.endpoints import auth, politicians, users
from fastapi import APIRouter

api_router = APIRouter()

# 各エンドポイントのルーターを登録
api_router.include_router(auth.router, prefix="/auth", tags=["認証"])
api_router.include_router(users.router, prefix="/users", tags=["ユーザー"])
api_router.include_router(
    politicians.router, prefix="/politicians", tags=["政治家"]
)
# 未実装のエンドポイント
# api_router.include_router(
#     statements.router, prefix="/statements", tags=["発言"]
# )
# api_router.include_router(parties.router, prefix="/parties", tags=["政党"])
# api_router.include_router(topics.router, prefix="/topics", tags=["トピック"])
# api_router.include_router(comments.router, prefix="/comments", tags=["コメント"])