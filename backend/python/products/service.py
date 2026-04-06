"""
Business logic for products. Controllers call this layer; persistence is in repository.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from . import repository as repo
from .models import Product
from .repository import resolve_categories_for_filter


class ProductService:
    """Create, read, update, soft-delete products with the same semantics as the HTTP API."""

    @staticmethod
    def create(payload: Dict[str, Any]) -> Product:
        return repo.create_product(payload)

    @staticmethod
    def create_bulk(payloads: List[Dict[str, Any]]) -> List[Product]:
        return [repo.create_product(payload) for payload in payloads]

    @staticmethod
    def list_products(
        include_deleted: bool = False,
        created_after: Optional[datetime] = None,
        updated_after: Optional[datetime] = None,
        created_before: Optional[datetime] = None,
        updated_before: Optional[datetime] = None,
        category_ids: Optional[List[int]] = None,
        category_titles: Optional[List[str]] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_warehouse_quantity: Optional[int] = None,
        max_warehouse_quantity: Optional[int] = None,
        brand: Optional[str] = None,
        brand_icontains: Optional[str] = None,
        search: Optional[str] = None,
        has_category: Optional[bool] = None,
    ) -> List[Product]:
        filter_categories = None
        if category_ids or category_titles:
            filter_categories = resolve_categories_for_filter(
                category_ids=category_ids,
                category_titles=category_titles,
            )
        return repo.list_products(
            include_deleted=include_deleted,
            created_after=created_after,
            updated_after=updated_after,
            created_before=created_before,
            updated_before=updated_before,
            filter_categories=filter_categories,
            min_price=min_price,
            max_price=max_price,
            min_warehouse_quantity=min_warehouse_quantity,
            max_warehouse_quantity=max_warehouse_quantity,
            brand=brand,
            brand_icontains=brand_icontains,
            search=search,
            has_category=has_category,
        )

    @staticmethod
    def get_product(product_id: int, include_deleted: bool = False) -> Optional[Product]:
        return repo.get_product(product_id, include_deleted=include_deleted)

    @staticmethod
    def update(product_id: int, validated: Dict[str, Any]) -> Optional[Product]:
        product = repo.get_product(product_id, include_deleted=False)
        if not product:
            return None

        data = dict(validated)
        if data.get("deleted") is True:
            return repo.soft_delete_product(product)

        data.pop("deleted", None)
        if not data:
            return repo.update_product(product, {})

        return repo.update_product(product, data)

    @staticmethod
    def soft_delete(product_id: int) -> Optional[Product]:
        product = repo.get_product(product_id, include_deleted=False)
        if not product:
            return None
        return repo.soft_delete_product(product)
