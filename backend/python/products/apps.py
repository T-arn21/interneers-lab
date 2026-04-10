import sys

from django.apps import AppConfig


class ProductsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "products"

    def ready(self) -> None:
        if "test" in sys.argv:
            return
        from .category_seeds import run_startup_seed

        run_startup_seed()
