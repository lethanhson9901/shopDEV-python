# src/services/item_service.py
from src.models.item_models import ItemModel
from src.models.clothing_models import ClothingModel
from src.models.electronic_models import ElectronicsModel
from src.core.error_response_handler import ErrorResponseHandler

class ItemFactory:
    item_classes = {
        'Electronics': ElectronicsModel,
        'Clothing': ClothingModel,
    }

    @staticmethod
    async def create_item(type, payload):
        try:
            item_class = ItemFactory.item_classes[type]
            return await item_class(payload).create_item()
        except KeyError:
            raise ErrorResponseHandler.bad_request(f'Invalid Product Type {type}')

class Item:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    async def create_item(self):
        return await ItemModel.create(**self.__dict__)

class Clothing(Item):
    async def create_item(self):
        self.attributes['type'] = 'Clothing'  # Assuming type is needed for model differentiation
        new_clothing = await ClothingModel.create(**self.attributes)
        self.id = new_clothing.id
        return await super().create_item()

class Electronics(Item):
    async def create_item(self):
        self.attributes['shop_owner'] = self.user
        self.attributes['type'] = 'Electronics'
        new_electronics = await ElectronicsModel.create(**self.attributes)
        self.id = new_electronics.id
        return await super().create_item()
