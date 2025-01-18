""" Department """
from typing import List

from pydantic import BaseModel, Field


class DepartmentModel(BaseModel):
    """ Class DepartmentModel """
    name: str = Field(example="ALIMENTOS BASICOS")
    department_id: str = Field(example="f9845b8a-efe4-48a0-a9aa-c45b50eafafe")
    categories: list
    segment_type: str = Field(example="MERCADOS")
    store_id: str = Field(example="ee4559e2-6c68-429c-9dad-89796c13315e")
    latitude: str = Field(example="-23.5942581")
    longitude: str = Field(example="-46.6107278")


class DepartmentHeader(BaseModel):
    """ Class DepartmentHeader """
    data: List[DepartmentModel]
