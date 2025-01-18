""" Department """
from typing import List

from pydantic import BaseModel, Field


class DepartmentModel(BaseModel):
    """ Class DepartmentModel """
    name: str = Field(example="ADEGA")
    department_id: int = Field(example=573383)
    store_id: int = Field(example=253)
    slug: str = Field(example="adega")
    search_term: str = Field(example="Adega")


class DepartmentHeader(BaseModel):
    """ Class DepartmentHeader """
    data: List[DepartmentModel]
