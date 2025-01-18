""" Department """
from typing import List

from pydantic import BaseModel, Field


class DepartmentModel(BaseModel):
    """ Class DepartmentModel """
    name: str = Field(example="MERCEARIA")
    department_id: int = Field(example=731)
    url: str = Field(example="https://mambodelivery.vtexcommercestable.com.br/mercearia")


class DepartmentHeader(BaseModel):
    """ Class DepartmentHeader """
    data: List[DepartmentModel]
