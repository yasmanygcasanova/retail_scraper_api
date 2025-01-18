""" Category """
from typing import List

from pydantic import BaseModel, Field


class CategoryModel(BaseModel):
    """ Class CategoryModel """
    name: str = Field(example="CAFES E CEVADAS")
    category_id: int = Field(example=572093)
    department_id: int = Field(example=572065)
    store_id: int = Field(example=253)
    slug: str = Field(example="cafes-e-cevadas")
    search_term: str = Field(example="Cafes e Cevadas")


class CategoryHeader(BaseModel):
    """ Class CategoryHeader """
    data: List[CategoryModel]
