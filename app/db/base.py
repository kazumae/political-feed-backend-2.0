# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.session import Base  # noqa
from app.models.comment import Comment, CommentReaction  # noqa
from app.models.party import Party, PartyDetail  # noqa
from app.models.politician import Politician, PoliticianDetail, PoliticianParty  # noqa
from app.models.statement import Statement, StatementReaction, StatementTopic  # noqa
from app.models.topic import Topic, TopicRelation  # noqa
from app.models.user import User  # noqa
