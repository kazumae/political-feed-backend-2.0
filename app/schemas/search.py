from typing import List, Optional

from app.schemas.politician import Politician
from app.schemas.statement import Statement
from app.schemas.topic import Topic
from pydantic import BaseModel


class SearchResult(BaseModel):
    """
    検索結果
    """
    statements: List[Statement] = []
    politicians: List[Politician] = []
    topics: List[Topic] = []
    total_statements: int = 0
    total_politicians: int = 0
    total_topics: int = 0
    query: str
    next_cursor: Optional[str] = None