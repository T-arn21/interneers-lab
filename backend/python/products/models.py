from datetime import datetime, timezone
from typing import Any, Dict

from mongoengine import (
    BooleanField,
    DateTimeField,
    Document,
    DecimalField,
    IntField,
    ListField,
    ReferenceField,
    SequenceField,
    StringField,
)


class ProductCategory(Document):
    meta = {"collection": "product_categories", "indexes": ["title"]}

    id = SequenceField(primary_key=True)  # type: ignore[assignment]
    title = StringField(required=True, unique=True, max_length=120)
    description = StringField(max_length=1000, default="")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": int(self.id) if self.id is not None else None,
            "title": self.title,
            "description": self.description or "",
        }


class Product(Document):
    """
    MongoEngine document for products. Integer `id` via SequenceField matches URL <int:product_id>.
    """

    meta = {
        "collection": "products",
        "indexes": ["-updated_at", "is_deleted", "categories_ref"],
    }

    id = SequenceField(primary_key=True) 
    name = StringField(required=True, max_length=120)
    description = StringField(max_length=1000, default="")
    categories_ref = ListField(ReferenceField(ProductCategory), default=list)
    price = DecimalField(required=True)
    brand = StringField(required=False, max_length=120, null=True)
    image = StringField(required=False, null=True)
    warehouse_quantity = IntField(required=True)
    is_deleted = BooleanField(default=False)
    deleted_at = DateTimeField(null=True)
    created_at = DateTimeField()
    updated_at = DateTimeField()

    def to_dict(self) -> Dict[str, Any]:
        categories = [c.title for c in self.categories_ref if c] if self.categories_ref else []
        return {
            "id": int(self.id) if self.id is not None else None,
            "name": self.name,
            "description": self.description or "",
            "categories": categories,
            "price": str(self.price) if self.price is not None else None,
            "brand": self.brand,
            "image": self.image,
            "warehouse_quantity": self.warehouse_quantity,
            "is_deleted": bool(self.is_deleted),
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @staticmethod
    def now_utc() -> datetime:
        return datetime.now(timezone.utc)

class AdminUser(Document):
    meta = {"collection": "admin_users", "indexes": ["username"]}

    id = SequenceField(primary_key=True)
    username = StringField(required=True, unique=True, max_length=120)
    password = StringField(required=True)  # Store hashed password
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": int(self.id) if self.id is not None else None,
            "username": self.username,
        }
