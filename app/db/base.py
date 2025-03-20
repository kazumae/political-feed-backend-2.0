# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.session import Base  # noqa
from app.models.activity import Notification, UserActivity  # noqa
from app.models.comment import Comment, CommentReaction  # noqa
from app.models.data_collection import (  # noqa
    DataCollectionLog,
    DataCollectionSource,
    SystemLog,
)
from app.models.follows import PoliticianFollow, TopicFollow  # noqa
from app.models.party import Party, PartyDetail  # noqa
from app.models.politician import Politician, PoliticianDetail, PoliticianParty  # noqa
from app.models.report import CommentReport  # noqa
from app.models.statement import Statement, StatementReaction, StatementTopic  # noqa
from app.models.topic import Topic, TopicRelation  # noqa
from app.models.user import User  # noqa
from app.models.user_settings import UserSettings  # noqa
