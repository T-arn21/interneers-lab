from datetime import datetime, timezone
from typing import Any, Dict

from mongoengine import (
    BooleanField,
    DateTimeField,
    Document,
    FloatField,
    IntField,
    SequenceField,
    StringField,
)


class Product(Document):
    """
    MongoEngine document for products. Integer `id` via SequenceField matches URL <int:product_id>.
    """

    meta = {
        "collection": "products",
        "indexes": ["-updated_at", "is_deleted"],
    }

    id = SequenceField(primary_key=True) 
    name = StringField(required=True, max_length=120)
    description = StringField(max_length=1000, default="")
    category = StringField(required=True, max_length=120)
    price = FloatField(required=True)
    brand = StringField(required=True, max_length=120)
    warehouse_quantity = IntField(required=True)
    is_deleted = BooleanField(default=False)
    deleted_at = DateTimeField(null=True)
    created_at = DateTimeField()
    updated_at = DateTimeField()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": int(self.id) if self.id is not None else None,
            "name": self.name,
            "description": self.description or "",
            "category": self.category,
            "price": float(self.price) if self.price is not None else None,
            "brand": self.brand,
            "warehouse_quantity": self.warehouse_quantity,
            "is_deleted": bool(self.is_deleted),
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @staticmethod
    def now_utc() -> datetime:
        return datetime.now(timezone.utc)
