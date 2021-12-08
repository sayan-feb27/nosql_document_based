from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, List


class BaseModelMixin:
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Bookmark(BaseModelMixin):
    user_id: int
    bookmarks: List[int]


@dataclass
class MovieRating(BaseModelMixin):
    movie_id: int
    user_id: int
    rating: int


@dataclass
class MovieReview(BaseModelMixin):
    author_id: int
    movie_id: int
    user_rating_id: Any
    title: str
    body: str
    created_at: datetime = field(default_factory=lambda: datetime.now())
    published_at: datetime = field(default_factory=lambda: datetime.now())
    is_draft: bool = False


@dataclass
class ReviewRating(BaseModelMixin):
    review_id: Any
    user_id: int
    rating: int
