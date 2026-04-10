from __future__ import annotations

from typing import Dict, List

from products.models import Product, ProductCategory
from products.repository import clear_store


def reset_products_test_data() -> None:
    clear_store()


def seed_categories() -> Dict[str, ProductCategory]:
    categories = {
        "Electronics": ProductCategory(title="Electronics", description="Devices"),
        "Food": ProductCategory(title="Food", description="Groceries"),
        "Kitchen": ProductCategory(title="Kitchen", description="Kitchen items"),
    }
    for category in categories.values():
        category.save()
    return categories


def seed_products(categories: Dict[str, ProductCategory]) -> List[Product]:
    now = Product.now_utc()
    products = [
        Product(
            name="Laptop",
            description="High end workstation",
            category_ref=categories["Electronics"],
            price=1500.0,
            brand="Acme",
            warehouse_quantity=5,
            is_deleted=False,
            deleted_at=None,
            created_at=now,
            updated_at=now,
        ),
        Product(
            name="Rice Bag",
            description="Organic rice",
            category_ref=categories["Food"],
            price=30.0,
            brand="FarmFresh",
            warehouse_quantity=40,
            is_deleted=False,
            deleted_at=None,
            created_at=now,
            updated_at=now,
        ),
        Product(
            name="Steel Pan",
            description="Kitchen cookware",
            category_ref=categories["Kitchen"],
            price=55.0,
            brand="Acme",
            warehouse_quantity=12,
            is_deleted=False,
            deleted_at=None,
            created_at=now,
            updated_at=now,
        ),
    ]
    for product in products:
        product.save()
    return products
