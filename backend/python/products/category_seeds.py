"""
Idempotent default product categories inserted when the Django app starts.

Disable with environment variable: PRODUCT_SKIP_CATEGORY_SEED=1
"""

import os
from typing import Iterable, List, Tuple

from . import repository as repo

# (title, description)
DEFAULT_PRODUCT_CATEGORIES: List[Tuple[str, str]] = [
    ("Electronics", "Devices, accessories, and consumer electronics."),
    ("Food & Beverages", "Groceries, drinks, and pantry items."),
    ("Home & Kitchen", "Cookware, décor, and household goods."),
    ("Sports & Outdoors", "Fitness, recreation, and outdoor gear."),
    ("Books & Media", "Books, e-readers, and media."),
    ("Health & Beauty", "Personal care, wellness, and cosmetics."),
    ("Uncategorized", "Default bucket for migrated or unassigned products."),
]


def seed_product_categories(categories: Iterable[Tuple[str, str]] | None = None) -> int:
    """
    Upsert each seed category by title. Returns how many new documents were created
    (existing titles are left unchanged).
    """
    created = 0
    for title, description in categories or DEFAULT_PRODUCT_CATEGORIES:
        existing = repo.get_category_by_title(title)
        if existing:
            continue
        repo.create_category({"title": title, "description": description})
        created += 1
    return created


def run_startup_seed() -> None:
    if os.environ.get("PRODUCT_SKIP_CATEGORY_SEED", "").strip().lower() in (
        "1",
        "true",
        "yes",
    ):
        return
    seed_product_categories()
