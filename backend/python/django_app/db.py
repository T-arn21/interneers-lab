from django.conf import settings
from mongoengine import connect


def initialize_db() -> None:
    """
    Connect to MongoDB using django settings (env-driven; defaults align with docker-compose).
    """
    connect(
        db=settings.MONGO_DB_NAME,
        host=settings.MONGO_HOST,
        port=settings.MONGO_PORT,
        username=settings.MONGO_USERNAME,
        password=settings.MONGO_PASSWORD,
        authentication_source=settings.MONGO_AUTH_SOURCE,
        alias="default",
    )
