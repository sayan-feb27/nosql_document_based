import abc
from typing import Any, List

DB_MOVIE_IDS = [x for x in range(1, 1000)]


class BaseDriver(abc.ABC):
    @property
    def db_movie_ids(self):
        return DB_MOVIE_IDS

    @abc.abstractmethod
    def populate_db(self):
        """
        Entry point.
        :return:
        """
        pass

    @abc.abstractmethod
    def user_bookmarks(self, user_id: int, movies_ids: List[int]):
        """
        Inserts users' bookmarks into store.
        :param user_id: -
        :param movies_ids: -
        :return:
        """
        pass

    @abc.abstractmethod
    def movie_ratings(self, user_id: int):
        """
        Populates movie_ratings collection.
        :param user_id: -
        :return:
        """
        pass

    @abc.abstractmethod
    def movie_review(
        self, user_id: int, movie_id: int, rating_id: int, title: str, body: str
    ):
        """
        Save user's review into database.
        :param user_id: -
        :param movie_id: -
        :param rating_id: -
        :param title: review's title
        :param body: review's body
        :return:
        """
        pass

    @abc.abstractmethod
    def review_ratings(self, user_id: int):
        """
        Creates reviews' rating collection.
        :param user_id:
        :return:
        """
        pass

    @abc.abstractmethod
    def get_user_favourites(self, user_id: int) -> Any:
        """
        Returns list of user's favourites (that are rated 10 out 10) movies.
        :param user_id:
        :return:
        """
        pass

    @abc.abstractmethod
    def count_movie_likes(self, movie_id: int) -> Any:
        """
        Returns the number of likes (rating == 10).
        :param movie_id:
        :return:
        """
        pass

    @abc.abstractmethod
    def count_movie_dislikes(self, movie_id: int) -> Any:
        """
        Returns the number of dislikes (rating == 0).
        :param movie_id:
        :return:
        """
        pass

    @abc.abstractmethod
    def get_user_bookmarks(self, user_id: int) -> Any:
        """
        Returns user's bookmarks.
        :param user_id:
        :return:
        """
        pass

    @abc.abstractmethod
    def get_movie_avg_rating(self, movie_id: int) -> Any:
        """
        Counts and returns an average movie rating.
        :param movie_id:
        :return:
        """
        pass
