from django.apps import AppConfig


class DjangoAppConfig(AppConfig):
    name = "django_app"

    def ready(self) -> None:
        from .db import initialize_db
        initialize_db()
