from django.apps import AppConfig


class ProductsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "products"

    def ready(self) -> None:
        from .category_seeds import run_startup_seed

        run_startup_seed()
