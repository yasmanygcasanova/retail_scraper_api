""" Category """
from typing import List

from pydantic import BaseModel, Field


class CategoryModel(BaseModel):
    """ Class CategoryModel """
    name: str = Field(example="CARNES")
    department_id: int = Field(example=3)
    category_id: int = Field(example=9)
    url: str = Field(example="https://mambodelivery.vtexcommercestable.com.br/acougue/carnes")


class CategoryHeader(BaseModel):
    """ Class CategoryHeader """
    data: List[CategoryModel]
