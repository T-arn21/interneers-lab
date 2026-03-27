from datetime import datetime, timezone
from typing import Dict, List, Optional

from .models import Product


PRODUCTS: Dict[int, Product] = {}
_NEXT_PRODUCT_ID = 1


def clear_store() -> None:
    global _NEXT_PRODUCT_ID
    PRODUCTS.clear()
    _NEXT_PRODUCT_ID = 1


def create_product(payload: dict) -> Product:
    global _NEXT_PRODUCT_ID
    product = Product(
        id=_NEXT_PRODUCT_ID,
        name=payload["name"],
        description=payload.get("description", ""),
        category=payload["category"],
        price=float(payload["price"]),
        brand=payload["brand"],
        warehouse_quantity=payload["warehouse_quantity"],
    )
    PRODUCTS[product.id] = product
    _NEXT_PRODUCT_ID += 1
    return product


def get_product(product_id: int, include_deleted: bool = False) -> Optional[Product]:
    product = PRODUCTS.get(product_id)
    if not product:
        return None
    if product.is_deleted and not include_deleted:
        return None
    return product


def list_products(include_deleted: bool = False) -> List[Product]:
    products = sorted(PRODUCTS.values(), key=lambda item: item.id)
    if include_deleted:
        return products
    return [product for product in products if not product.is_deleted]


def update_product(product: Product, payload: dict) -> Product:
    for key, value in payload.items():
        if key == "price":
            setattr(product, key, float(value))
            continue
        setattr(product, key, value)
    return product


def soft_delete_product(product: Product) -> Product:
    product.is_deleted = True
    product.deleted_at = datetime.now(timezone.utc)
    return product

