# path/filename: models/item_model.py
from enum import Enum
from typing import Dict, List, Optional, Set
from uuid import uuid4

from pydantic import BaseModel, Field, root_validator, validator


class ItemState(str, Enum):
    ACTIVE = "active"
    DISCONTINUED = "discontinued"
    OUT_OF_STOCK = "out_of_stock"


class ItemModel(BaseModel):
    id: Optional[str] = Field(
        default_factory=lambda: str(uuid4()), 
        description="Autogenerated unique identifier."
    )
    name: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="The name of the item."
    )
    description: Optional[str] = Field(
        None,
        description="A brief item description."
    )
    price: float = Field(
        ...,
        gt=0,
        description="Item price, must be positive."
    )
    stock_quantity: int = Field(
        ...,
        ge=0,
        description="Stock quantity, non-negative."
    )
    category: Optional[str] = Field(
        None,
        description="Item category."
    )
    tags: List[str] = Field(
        default_factory=list,
        description="Searchable tags.",
        max_items=10
    )
    state: ItemState = Field(
        default=ItemState.ACTIVE,
        description="Current state of the item."
    )
    audit_trail: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Audit trail for item changes."
    )

    @validator('tags', pre=True)
    def ensure_tags_are_unique(cls, v):
        if isinstance(v, list) and len(v) != len(set(v)):
            raise ValueError("Tags must be unique")
        return list(set(v))

    @root_validator(pre=True)
    def check_state_based_on_stock(cls, values):
        stock_quantity = values.get('stock_quantity', 0)
        state = values.get('state', ItemState.ACTIVE)
        if stock_quantity == 0 and state != ItemState.DISCONTINUED:
            values['state'] = ItemState.OUT_OF_STOCK
        return values

    def apply_discount(self, percentage: float) -> None:
        if not 0 <= percentage <= 100:
            raise ValueError("Discount must be between 0% and 100%.")
        self.price *= (1 - percentage / 100)
        self.audit_trail.append(
            {"action": "apply_discount", "percentage": str(percentage)}
        )

    def adjust_stock(self, quantity: int, reason: str = "adjustment") -> None:
        if reason == "return" and quantity < 0:
            raise ValueError("Return quantity must be positive")
        self.stock_quantity += quantity
        self.audit_trail.append(
            {"action": "adjust_stock", "quantity": str(quantity), "reason": reason}
        )

    def can_user_modify(self, user_role: str, permission_service) -> bool:
        return permission_service.check_permission(user_role, "modify_item")

    def __eq__(self, other):
        if not isinstance(other, ItemModel):
            return NotImplemented
        return self.id == other.id

    def __lt__(self, other):
        if not isinstance(other, ItemModel):
            return NotImplemented
        return self.price < other.price

    class Config:
        anystr_strip_whitespace = True
        min_anystr_length = 1
        validate_assignment = True
        use_enum_values = True

    def custom_json(self, **kwargs):
        return self.dict(**kwargs)
