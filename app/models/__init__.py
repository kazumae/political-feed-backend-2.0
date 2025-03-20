from app.models.activity import Notification, UserActivity
from app.models.comment import Comment, CommentReaction
from app.models.data_collection import (
    DataCollectionLog,
    DataCollectionSource,
    SystemLog,
)
from app.models.follows import PoliticianFollow, TopicFollow
from app.models.party import Party, PartyDetail
from app.models.politician import Politician, PoliticianDetail, PoliticianParty
from app.models.report import CommentReport
from app.models.statement import Statement, StatementReaction, StatementTopic
from app.models.topic import Topic, TopicRelation
from app.models.user import User
from app.models.user_settings import UserSettings

# これらのモデルは意図的にインポートされています
# SQLAlchemyのメタデータに登録するため
__all__ = [
    "Notification", "UserActivity",
    "Comment", "CommentReaction",
    "DataCollectionLog", "DataCollectionSource", "SystemLog",
    "PoliticianFollow", "TopicFollow",
    "Party", "PartyDetail",
    "Politician", "PoliticianDetail", "PoliticianParty",
    "CommentReport",
    "Statement", "StatementReaction", "StatementTopic",
    "Topic", "TopicRelation",
    "User",
    "UserSettings"
]
