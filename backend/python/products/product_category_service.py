from typing import Dict, List, Optional

from . import repository as repo
from .models import Product, ProductCategory


class ProductCategoryService:
    @staticmethod
    def create(payload: Dict) -> ProductCategory:
        return repo.create_category(payload)

    @staticmethod
    def list_categories() -> List[ProductCategory]:
        return repo.list_categories()

    @staticmethod
    def get(category_id: int) -> Optional[ProductCategory]:
        return repo.get_category(category_id)

    @staticmethod
    def update(category_id: int, payload: Dict) -> Optional[ProductCategory]:
        category = repo.get_category(category_id)
        if not category:
            return None
        return repo.update_category(category, payload)

    @staticmethod
    def delete(category_id: int) -> bool:
        category = repo.get_category(category_id)
        if not category:
            return False
        repo.delete_category(category)
        return True

    @staticmethod
    def list_products(category_id: int, include_deleted: bool = False) -> Optional[List[Product]]:
        category = repo.get_category(category_id)
        if not category:
            return None
        return repo.list_products_by_category(category, include_deleted=include_deleted)

    @staticmethod
    def add_products(category_id: int, product_ids: List[int]) -> Optional[List[Product]]:
        category = repo.get_category(category_id)
        if not category:
            return None
        products = repo.get_products_by_ids(product_ids, include_deleted=False)
        if len(products) != len(set(product_ids)):
            return None
        repo.assign_products_to_category(category, products)
        return products

    @staticmethod
    def remove_products(category_id: int, product_ids: List[int]) -> Optional[List[Product]]:
        category = repo.get_category(category_id)
        if not category:
            return None
        products = repo.get_products_by_ids(product_ids, include_deleted=False)
        if len(products) != len(set(product_ids)):
            return None
        repo.remove_products_from_category(category, products)
        return products
