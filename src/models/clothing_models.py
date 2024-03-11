from src.models.item_models import ItemAttributes, ItemModel
from src.models.category_enum_models import CategoryEnum
from pydantic import Field, Optional


# Extension for specific categories with their unique attributes
class ClothingAttributes(ItemAttributes):
    gender: Optional[str] = Field(None, description="Intended gender for the clothing item.")

class ClothingModel(ItemModel):
    category: CategoryEnum = Field(default=CategoryEnum.CLOTHING, const=True)
    attributes: ClothingAttributes = Field(default_factory=ClothingAttributes)