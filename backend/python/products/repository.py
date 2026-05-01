from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from mongoengine import NotUniqueError, Q

from .models import Product, ProductCategory


def clear_store() -> None:
    """Remove all product/category documents (used by tests)."""
    Product.drop_collection()
    ProductCategory.drop_collection()


def get_or_create_category_by_title(title: str, description: str = "") -> ProductCategory:
    category = ProductCategory.objects(title=title).first()
    if category:
        return category
    category = ProductCategory(title=title, description=description or "")
    try:
        category.save()
    except NotUniqueError:
        return ProductCategory.objects(title=title).first()
    return category


def create_category(payload: dict) -> ProductCategory:
    category = ProductCategory(
        title=payload["title"],
        description=payload.get("description") or "",
    )
    category.save()
    return category


def list_categories() -> List[ProductCategory]:
    return list(ProductCategory.objects.order_by("title"))


def get_category(category_id: int) -> Optional[ProductCategory]:
    return ProductCategory.objects(id=category_id).first()


def get_category_by_title(title: str) -> Optional[ProductCategory]:
    return ProductCategory.objects(title=title).first()


class CategoryFilterError(ValueError):
    """Raised when list filter references an unknown category id or title."""


def resolve_categories_for_filter(
    category_ids: Optional[List[int]] = None,
    category_titles: Optional[List[str]] = None,
) -> List[ProductCategory]:
    out: List[ProductCategory] = []
    if category_ids:
        for cid in category_ids:
            c = get_category(cid)
            if not c:
                raise CategoryFilterError(f"Unknown category_id: {cid}")
            out.append(c)
    if category_titles:
        for title in category_titles:
            c = get_category_by_title(title)
            if not c:
                raise CategoryFilterError(f"Unknown category title: {title!r}")
            out.append(c)
    return list({c.id: c for c in out}.values())


def update_category(category: ProductCategory, payload: dict) -> ProductCategory:
    for key, value in payload.items():
        setattr(category, key, value)
    category.save()
    return category


def delete_category(category: ProductCategory) -> None:
    Product.objects(category_ref=category).update(unset__category_ref=1, updated_at=Product.now_utc())
    category.delete()


def list_products_by_category(
    category: ProductCategory,
    include_deleted: bool = False,
) -> Any:
    qs = Product.objects(category_ref=category)
    if not include_deleted:
        qs = qs.filter(is_deleted=False)
    return qs.order_by("-updated_at")


def assign_products_to_category(category: ProductCategory, products: List[Product]) -> None:
    now = Product.now_utc()
    for product in products:
        product.category_ref = category
        product.updated_at = now
        product.save()


def remove_products_from_category(category: ProductCategory, products: List[Product]) -> None:
    now = Product.now_utc()
    for product in products:
        if product.category_ref and product.category_ref.id == category.id:
            product.category_ref = None
            product.updated_at = now
            product.save()


def create_product(payload: dict) -> Product:
    now = Product.now_utc()
    category = get_or_create_category_by_title(payload["category"])
    product = Product(
        name=payload["name"],
        description=payload.get("description") or "",
        category_ref=category,
        price=Decimal(str(payload["price"])),
        brand=payload.get("brand"),
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


def get_products_by_ids(product_ids: List[int], include_deleted: bool = False) -> List[Product]:
    qs = Product.objects(id__in=product_ids)
    if not include_deleted:
        qs = qs.filter(is_deleted=False)
    return list(qs)


def list_products(
    include_deleted: bool = False,
    created_after: Optional[datetime] = None,
    updated_after: Optional[datetime] = None,
    created_before: Optional[datetime] = None,
    updated_before: Optional[datetime] = None,
    filter_categories: Optional[List[ProductCategory]] = None,
    min_price: Optional[Decimal] = None,
    max_price: Optional[Decimal] = None,
    min_warehouse_quantity: Optional[int] = None,
    max_warehouse_quantity: Optional[int] = None,
    brand: Optional[str] = None,
    brand_icontains: Optional[str] = None,
    search: Optional[str] = None,
    has_category: Optional[bool] = None,
) -> Any:
    qs = Product.objects
    if not include_deleted:
        qs = qs.filter(is_deleted=False)
    if created_after is not None:
        qs = qs.filter(created_at__gte=created_after)
    if updated_after is not None:
        qs = qs.filter(updated_at__gte=updated_after)
    if created_before is not None:
        qs = qs.filter(created_at__lte=created_before)
    if updated_before is not None:
        qs = qs.filter(updated_at__lte=updated_before)
    if min_price is not None:
        qs = qs.filter(price__gte=min_price)
    if max_price is not None:
        qs = qs.filter(price__lte=max_price)
    if min_warehouse_quantity is not None:
        qs = qs.filter(warehouse_quantity__gte=min_warehouse_quantity)
    if max_warehouse_quantity is not None:
        qs = qs.filter(warehouse_quantity__lte=max_warehouse_quantity)
    if brand is not None:
        qs = qs.filter(brand=brand)
    if brand_icontains:
        qs = qs.filter(brand__icontains=brand_icontains)
    if search:
        term = search.strip()
        if term:
            qs = qs.filter(Q(name__icontains=term) | Q(description__icontains=term))
    if has_category is True:
        qs = qs.filter(category_ref__ne=None)
    if has_category is False:
        qs = qs.filter(category_ref=None)

    if filter_categories:
        qs = qs.filter(category_ref__in=filter_categories)

    return qs.order_by("-updated_at")


def update_product(product: Product, payload: dict) -> Product:
    now = Product.now_utc()
    for key, value in payload.items():
        if key == "price":
            setattr(product, key, Decimal(str(value)))
            continue
        if key == "category":
            product.category_ref = get_or_create_category_by_title(str(value))
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
