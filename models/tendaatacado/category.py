""" Category """
from typing import List

from pydantic import BaseModel, Field


class CategoryModel(BaseModel):
    """ Class CategoryModel """
    name: str = Field(example="ACHOCOLATADO EM PO")
    category_id: int = Field(example=125)
    department_id: int = Field(example=12)
    search_term: str = Field(example="achocolatado-em-po")


class CategoryHeader(BaseModel):
    """ Class CategoryHeader """
    data: List[CategoryModel]
