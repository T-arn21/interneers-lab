from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Product:
    id: int
    name: str
    description: str
    category: str
    price: float
    brand: str
    warehouse_quantity: int
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "price": self.price,
            "brand": self.brand,
            "warehouse_quantity": self.warehouse_quantity,
            "is_deleted": self.is_deleted,
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
        }

