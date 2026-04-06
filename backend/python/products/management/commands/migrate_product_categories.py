from django.core.management.base import BaseCommand

from products.product_migration import migrate_legacy_product_categories


class Command(BaseCommand):
    help = (
        "Link products missing category_ref to ProductCategory: use legacy `category` "
        "string if present, otherwise assign Uncategorized."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Report counts only; do not write to MongoDB.",
        )

    def handle(self, *args, **options):
        stats = migrate_legacy_product_categories(dry_run=options["dry_run"])
        for key, value in stats.items():
            self.stdout.write(f"{key}: {value}")
