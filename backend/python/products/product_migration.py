"""
Backfill `Product.category_ref` for documents that predate the ProductCategory model.

Scans the raw `products` collection so legacy string field `category` (if present) can
still be read; MongoEngine drops unknown fields when loading documents.

Run once (or idempotently) via:

  python manage.py migrate_product_categories
  python manage.py migrate_product_categories --dry-run
"""

from __future__ import annotations

from typing import Any, Dict

from mongoengine.connection import get_db

from . import repository as repo
from .models import Product


def migrate_legacy_product_categories(*, dry_run: bool = False) -> Dict[str, Any]:
    """
    For each product document without `category_ref`:
    - If a legacy string field `category` exists, ensure a ProductCategory exists and link it.
    - Otherwise assign the seeded \"Uncategorized\" category.

    Documents that already have `category_ref` are left unchanged.
    """
    db = get_db()
    coll = db["products"]
    stats: Dict[str, Any] = {
        "examined": 0,
        "skipped_has_category_ref": 0,
        "linked_from_legacy_category_string": 0,
        "assigned_uncategorized": 0,
        "dry_run": dry_run,
    }
    now = Product.now_utc()

    for raw in coll.find():
        stats["examined"] += 1
        pid = raw.get("id")
        if pid is None:
            continue

        if raw.get("category_ref") is not None:
            stats["skipped_has_category_ref"] += 1
            continue

        legacy = raw.get("category")
        if isinstance(legacy, str) and legacy.strip():
            title = legacy.strip()
            if not dry_run:
                cat = repo.get_or_create_category_by_title(title)
                Product.objects(id=pid).update(set__category_ref=cat, set__updated_at=now)
            stats["linked_from_legacy_category_string"] += 1
            continue

        if not dry_run:
            unc = repo.get_or_create_category_by_title(
                "Uncategorized",
                "Products not yet assigned to a category.",
            )
            Product.objects(id=pid).update(set__category_ref=unc, set__updated_at=now)
        stats["assigned_uncategorized"] += 1

    return stats
