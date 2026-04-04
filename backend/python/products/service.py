"""
Business logic for products. Controllers call this layer; persistence is in repository.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from . import repository as repo
from .models import Product


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
    ) -> List[Product]:
        return repo.list_products(
            include_deleted=include_deleted,
            created_after=created_after,
            updated_after=updated_after,
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
