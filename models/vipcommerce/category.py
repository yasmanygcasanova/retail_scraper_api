""" Category """
from typing import List

from pydantic import BaseModel, Field


class CategoryModel(BaseModel):
    """ Class CategoryModel """
    name: str = Field(example="MOLHO SALADA")
    category_id: int = Field(example=61)
    department_id: int = Field(example=5)
    slug: str = Field(example="/mercearia/molho-salada")
    branch_id: int = Field(example=1)
    distribution_center_id: int = Field(example=1)


class CategoryHeader(BaseModel):
    """ Class CategoryHeader """
    data: List[CategoryModel]
