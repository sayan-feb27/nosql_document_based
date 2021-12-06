import argparse
from timeit import default_timer as timer

from drivers import BaseDriver, MongoDBDriver, ArangoDBDriver, RavenDBDriver


def time_it(driver: BaseDriver, operation: str, *args, **kwargs):
    start = timer()

    print(f"performing {operation}:")
    print(getattr(driver, operation)(*args, **kwargs))

    end = timer()

    print(end - start, end="\n\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "driver",
        help="which driver to run",
        type=str,
        choices=["mongo", "arango", "raven"],
    )
    parser.add_argument("--populate", default=False, type=bool)

    args = parser.parse_args()

    driver = None
    driver_name = args.driver
    if driver_name == "mongo":
        driver = MongoDBDriver(
            db_name="ugc", connection_params={"host": "localhost", "port": 27017}
        )
    elif driver_name == "arango":
        driver = ArangoDBDriver(
            db_name="ugc", connection_params={"username": "root", "password": "a"}
        )
    else:
        driver = RavenDBDriver(
            db_name="ugc",
            connection_params={
                "urls": [
                    "http://localhost:8080",
                ]
            },
        )

    if args.populate:
        driver.populate_db()

    operations = [
        {"name": "get_user_favourites", "args": [], "kwargs": {"user_id": 1}},
        {"name": "count_movie_likes", "args": [], "kwargs": {"movie_id": 1}},
        {"name": "count_movie_dislikes", "args": [], "kwargs": {"movie_id": 1}},
        {"name": "get_user_bookmarks", "args": [], "kwargs": {"user_id": 12}},
        {"name": "get_movie_avg_rating", "args": [], "kwargs": {"movie_id": 790}},
    ]

    print(f"{driver}: ", end="\n\n")
    for operation in operations:
        time_it(driver, operation["name"], **operation["kwargs"])
    print("*" * 50, end="\n\n")
