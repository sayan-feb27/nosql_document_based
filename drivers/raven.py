from random import choice, randint, sample
from typing import Any

from faker import Faker
from pyravendb.store import document_store
from pyravendb.data.query import QueryOperator

from .base import BaseDriver
from .models.general import Bookmark, MovieRating, MovieReview, ReviewRating


class RavenDBDriver(BaseDriver):
    def __init__(self, db_name: str, connection_params: dict):
        self.store = document_store.DocumentStore(database=db_name, **connection_params)
        self.store.initialize()

    def __str__(self):
        return "RavenDBDriver"

    def user_bookmarks(self, user_id, movies_ids):
        with self.store.open_session() as session:
            bookmark = Bookmark(user_id=user_id, bookmarks=movies_ids)
            session.store(bookmark)
            session.save_changes()

    def movie_ratings(self, user_id) -> Any:
        fake = Faker("ru_RU")
        rated_movies_ids = sample(self.db_movie_ids, randint(200, 900))
        with self.store.open_session() as session:
            for r_id in rated_movies_ids:
                rating = MovieRating(
                    movie_id=r_id, user_id=user_id, rating=randint(0, 10)
                )
                session.store(rating)

                to_review = choice((True, False))
                if not to_review:
                    continue

                rating_id = session.advanced.get_document_id(rating)
                self.movie_review(
                    user_id=user_id,
                    movie_id=r_id,
                    rating_id=rating_id,
                    title=fake.sentence(),
                    body=fake.text(),
                )
            session.save_changes()

    def movie_review(
        self, user_id: int, movie_id: int, rating_id: int, title: str, body: str
    ):
        with self.store.open_session() as session:
            movie_review = MovieReview(
                author_id=user_id,
                movie_id=movie_id,
                user_rating_id=rating_id,
                title=title,
                body=body,
            )
            session.store(movie_review)
            session.save_changes()

    def review_ratings(self, user_id):
        with self.store.open_session() as session:
            skip = randint(0, 800)
            limit = 200
            movie_reviews = (
                session.query(object_type=MovieReview)
                .where_not_equals("user_id", user_id)
                .skip(skip)
                .take(limit)
            )

            for review in movie_reviews:
                review_id = session.advanced.get_document_id(review)
                review_rating = ReviewRating(
                    review_id=review_id, user_id=user_id, rating=randint(0, 10)
                )
                session.store(review_rating)
            session.save_changes()

    def populate_db(self):
        for user_id in range(1, 100):
            self.user_bookmarks(
                user_id=user_id, movies_ids=sample(self.db_movie_ids, randint(1, 100))
            )
            self.movie_ratings(user_id)
            self.review_ratings(user_id)

    def get_user_favourites(self, user_id):
        with self.store.open_session() as session:
            return list(
                session.query(
                    object_type=MovieRating, default_operator=QueryOperator.AND
                ).where(user_id=user_id, rating=10)
            )

    def count_movie_likes(self, movie_id):
        with self.store.open_session() as session:
            res = list(
                session.query(
                    object_type=MovieRating,
                    with_statistics=True,
                    default_operator=QueryOperator.AND,
                )
                .where(movie_id=movie_id, rating=10)
                .take(0)
            )[1]["TotalResults"]
            return res

    def count_movie_dislikes(self, movie_id):
        with self.store.open_session() as session:
            res = list(
                session.query(
                    object_type=MovieRating,
                    with_statistics=True,
                    default_operator=QueryOperator.AND,
                )
                .where(movie_id=movie_id, rating=0)
                .take(0)
            )[1]["TotalResults"]
            return res

    def get_user_bookmarks(self, user_id):
        with self.store.open_session() as session:
            return list(session.query(object_type=Bookmark).where(user_id=user_id))

    def get_movie_avg_rating(self, movie_id):
        rql = f"""
        from 'MovieRatings' as mv
        group by mv.movie_id
        where mv.movie_id == {movie_id}
        select sum(mv.rating) as Sum, count() as Count
        """

        with self.store.open_session() as session:
            res = session.query(object_type=dict).raw_query(rql).take(1)
            return list(res)
