from typing import Optional
from pydantic import BaseModel 
from sqlmodel import Field, SQLModel

class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    category:str
    description: str
    price: float

    def __init__(self, id, name, category, description, price):
        self.id = id
        self.name = name
        self.category = category
        self.description = description
        self.price = price

#could also have 
# The "Response" version - used for data going OUT
# class ProductResponse(BaseModel):
#     id: int
#     name: str
#     price: float
#     # Notice we might leave out 'description' if we want a shorter list view


# API Input contract
class ProductRequest(BaseModel):
    id: Optional[int] = None
    name: str = Field(min_length=1)
    category: str = Field(min_length=1)
    description: str =Field(min_length=1, max_length=100)
    price: float = Field(gt=0) # Price must be greater than 0

    class Config:
        json_schema_extra = {
            'example': {
                'name': 'Innovative Widget',
                'category': 'Widgets',
                'description': 'An innovative widget that solves all your widget needs',
                'price': 19.99
            }
        }
