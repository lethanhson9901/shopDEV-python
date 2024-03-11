from src.models.item_models import ItemAttributes, ItemModel
from src.models.category_enum_models import CategoryEnum
from pydantic import Field, Optional


class ElectronicsAttributes(ItemAttributes):
    warranty_period: Optional[int] = Field(None, description="Warranty period in months.")
    power_usage: Optional[float] = Field(None, description="Power usage in watts.")


class ElectronicsModel(ItemModel):
    category: CategoryEnum = Field(default=CategoryEnum.ELECTRONICS, const=True)
    attributes: ElectronicsAttributes = Field(default_factory=ElectronicsAttributes)
