from datetime import datetime
from typing import Dict, List, Optional

from .models import Product


def clear_store() -> None:
    """Remove all product documents (used by tests)."""
    Product.drop_collection()


def create_product(payload: dict) -> Product:
    now = Product.now_utc()
    product = Product(
        name=payload["name"],
        description=payload.get("description") or "",
        category=payload["category"],
        price=float(payload["price"]),
        brand=payload["brand"],
        warehouse_quantity=payload["warehouse_quantity"],
        is_deleted=False,
        deleted_at=None,
        created_at=now,
        updated_at=now,
    )
    product.save()
    return product


def get_product(product_id: int, include_deleted: bool = False) -> Optional[Product]:
    product = Product.objects(id=product_id).first()
    if not product:
        return None
    if product.is_deleted and not include_deleted:
        return None
    return product


def list_products(
    include_deleted: bool = False,
    created_after: Optional[datetime] = None,
    updated_after: Optional[datetime] = None,
) -> List[Product]:
    qs = Product.objects
    if not include_deleted:
        qs = qs.filter(is_deleted=False)
    if created_after is not None:
        qs = qs.filter(created_at__gte=created_after)
    if updated_after is not None:
        qs = qs.filter(updated_at__gte=updated_after)
    return list(qs.order_by("-updated_at"))


def update_product(product: Product, payload: dict) -> Product:
    now = Product.now_utc()
    for key, value in payload.items():
        if key == "price":
            setattr(product, key, float(value))
            continue
        setattr(product, key, value)
    product.updated_at = now
    product.save()
    return product


def soft_delete_product(product: Product) -> Product:
    now = Product.now_utc()
    product.is_deleted = True
    product.deleted_at = now
    product.updated_at = now
    product.save()
    return product
