from random import choice, randint, sample
from typing import Any

from faker import Faker
from pyArango.connection import Connection as ArangoConnection

from .base import BaseDriver
from .models import Bookmark, MovieRating, MovieReview, ReviewRating


class ArangoDBDriver(BaseDriver):
    def __init__(self, db_name, connection_params):
        self.db_name = db_name
        self.connection_params = connection_params
        self.__db = None

    def __str__(self):
        return "ArangoDBDriver"

    @property
    def db(self):
        if self.__db is None:
            connection = ArangoConnection(**self.connection_params)
            if not connection.hasDatabase(self.db_name):
                connection.createDatabase(self.db_name)
            self.__db = connection[self.db_name]
        return self.__db

    def user_bookmarks(self, user_id, movies_ids):
        bookmarks_collection = self.db["UserBookmarks"]
        bookmark = Bookmark(user_id=user_id, bookmarks=movies_ids)
        bookmark_document = bookmarks_collection.createDocument(
            initDict=bookmark.to_dict()
        )
        bookmark_document.save()

    def movie_ratings(self, user_id) -> Any:
        fake = Faker("ru_RU")
        movie_ratings_collection = self.db["MovieRatings"]

        rated_movies_ids = sample(self.db_movie_ids, randint(200, 900))
        for r_id in rated_movies_ids:
            rating = MovieRating(movie_id=r_id, user_id=user_id, rating=randint(0, 10))
            rating_document = movie_ratings_collection.createDocument(
                initDict=rating.to_dict()
            )
            rating_document.save()

            rating_id = rating_document._key
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
        movie_reviews_collection = self.db["MovieReviews"]
        movie_review = MovieReview(
            author_id=user_id,
            movie_id=movie_id,
            user_rating_id=rating_id,
            title=title,
            body=body,
        )
        movie_review_document = movie_reviews_collection.createDocument(
            initDict=movie_review.to_dict()
        )
        movie_review_document.save()

    def review_ratings(self, user_id):
        review_ratings_collection = self.db["ReviewRatings"]

        aql = """
        FOR review IN MovieReviews
        FILTER review.author_id != @user_id
        LIMIT @skip, @limit
        RETURN review._key
        """
        movie_reviews_ids = self.db.AQLQuery(
            aql,
            rawResults=True,
            batchSize=100,
            bindVars={
                "user_id": user_id,
                "skip": randint(0, 800),
                "limit": 200,
            },
        )
        for review_id in movie_reviews_ids:
            review_rating = ReviewRating(
                review_id=review_id, user_id=user_id, rating=randint(0, 10)
            )
            review_rating_document = review_ratings_collection.createDocument(
                review_rating.to_dict()
            )
            review_rating_document.save()

    def prepare_collections(self):
        collections_names = [
            "UserBookmarks",
            "MovieRatings",
            "MovieReviews",
            "ReviewRatings",
        ]
        for name in collections_names:
            if self.db.hasCollection(name):
                continue
            self.db.createCollection(name=name)

    def populate_db(self):
        self.prepare_collections()

        for user_id in range(1, 100):
            self.user_bookmarks(
                user_id=user_id, movies_ids=sample(self.db_movie_ids, randint(1, 100))
            )
            self.movie_ratings(user_id=user_id)
            self.review_ratings(user_id=user_id)

    def get_user_favourites(self, user_id):
        aql = """
        FOR rating IN MovieRatings
        FILTER rating.user_id == @user_id AND rating.rating == @rating
        RETURN rating
        """
        result = self.db.AQLQuery(
            aql,
            rawResults=True,
            bindVars={"user_id": user_id, "rating": 10},
        )
        return result

    def count_movie_likes(self, movie_id):
        aql = """
        RETURN LENGTH(
            FOR rating IN MovieRatings
            FILTER rating.movie_id == @movie_id AND rating.rating == @rating
            RETURN 1
        )
        """
        result = self.db.AQLQuery(
            aql,
            rawResults=True,
            bindVars={"movie_id": movie_id, "rating": 10},
        )
        return result

    def count_movie_dislikes(self, movie_id):
        aql = """
        RETURN LENGTH(
            FOR rating IN MovieRatings
            FILTER rating.movie_id == @movie_id AND rating.rating == @rating
            RETURN 1
        )
        """
        result = self.db.AQLQuery(
            aql,
            rawResults=True,
            bindVars={"movie_id": movie_id, "rating": 0},
        )
        return result

    def get_user_bookmarks(self, user_id):
        aql = """
        FOR bookmark IN UserBookmarks
        FILTER bookmark.user_id == @user_id
        RETURN bookmark
        """
        result = self.db.AQLQuery(
            aql,
            rawResults=True,
            bindVars={
                "user_id": user_id,
            },
        )
        return result

    def get_movie_avg_rating(self, movie_id):
        aql = """
        FOR rating IN MovieRatings
        FILTER rating.movie_id == @movie_id
        COLLECT AGGREGATE avg_rating = AVG(rating.rating)
        RETURN {
            avg_rating
        }
        """
        result = self.db.AQLQuery(
            aql,
            rawResults=True,
            bindVars={
                "movie_id": movie_id,
            },
        )
        return result
