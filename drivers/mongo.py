from random import choice, randint, sample
from typing import Any

from faker import Faker
from pymongo import MongoClient

from .base import BaseDriver
from .models import Bookmark, MovieRating, MovieReview, ReviewRating


class MongoDBDriver(BaseDriver):
    def __init__(self, db_name: str, connection_params: dict):
        self.db_name = db_name
        self.connection_params = connection_params
        self.__db = None

    def __str__(self):
        return "MongoDBDriver"

    @property
    def db(self):
        if self.__db is None:
            client = MongoClient(**self.connection_params)
            self.__db = client[self.db_name]
        return self.__db

    def user_bookmarks(self, user_id, movies_ids):
        bookmarks_collection = self.db["user_bookmarks"]
        bookmark = Bookmark(user_id=user_id, bookmarks=movies_ids)
        bookmarks_collection.insert_one(bookmark.to_dict())

    def movie_ratings(self, user_id) -> Any:
        fake = Faker("ru_RU")
        movie_ratings_collection = self.db["movie_ratings"]
        rated_movies_ids = sample(self.db_movie_ids, randint(200, 900))

        for r_id in rated_movies_ids:
            rating = MovieRating(movie_id=r_id, user_id=user_id, rating=randint(0, 10))
            rating_id = movie_ratings_collection.insert_one(
                rating.to_dict()
            ).inserted_id

            to_review = choice((True, False))
            if not to_review:
                continue

            self.movie_review(
                user_id=user_id,
                movie_id=r_id,
                rating_id=rating_id,
                title=fake.sentence(),
                body=fake.text(),
            )

    def movie_review(self, user_id, movie_id, rating_id, title, body):
        movie_reviews_collection = self.db["movie_reviews"]
        movie_review = MovieReview(
            author_id=user_id,
            movie_id=movie_id,
            user_rating_id=rating_id,
            title=title,
            body=body,
        )
        movie_reviews_collection.insert_one(movie_review.to_dict())

    def review_ratings(self, user_id):
        review_ratings_collection = self.db["review_ratings"]
        movie_reviews = self.db["movie_reviews"].find(
            {"author_id": {"$ne": user_id}}, skip=randint(0, 800), limit=200
        )
        for review in movie_reviews:
            review_rating = ReviewRating(
                review_id=review["_id"], user_id=user_id, rating=randint(0, 10)
            )
            review_ratings_collection.insert_one(review_rating.to_dict())

    def populate_db(self):
        for user_id in range(1, 100):
            self.user_bookmarks(
                user_id=user_id, movies_ids=sample(self.db_movie_ids, randint(1, 100))
            )
            self.movie_ratings(user_id=user_id)
            self.review_ratings(user_id=user_id)

    def get_user_favourites(self, user_id):
        return list(
            self.db["movie_ratings"].find(
                {
                    "author_id": user_id,
                    "rating": 10,
                }
            )
        )

    def count_movie_likes(self, movie_id):
        return self.db["movie_ratings"].count_documents(
            {
                "movie_id": movie_id,
                "rating": 10,
            }
        )

    def count_movie_dislikes(self, movie_id):
        return self.db["movie_ratings"].count_documents(
            {
                "movie_id": movie_id,
                "rating": 0,
            }
        )

    def get_user_bookmarks(self, user_id):
        return self.db["user_bookmarks"].find_one({"user_id": user_id})

    def get_movie_avg_rating(self, movie_id):
        return list(
            self.db["movie_ratings"].aggregate(
                [
                    {
                        "$match": {"movie_id": movie_id},
                    },
                    {
                        "$group": {"_id": None, "avg_rating": {"$avg": "$rating"}},
                    },
                ]
            )
        )
