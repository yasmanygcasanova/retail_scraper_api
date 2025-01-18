""" Department """
from typing import List

from pydantic import BaseModel, Field


class DepartmentModel(BaseModel):
    """ Class DepartmentModel """
    name: str = Field(example="MERCEARIA")
    department_id: int = Field(example=5)
    slug: str = Field(example="/mercearia")
    branch_id: int = Field(example=1)
    distribution_center_id: int = Field(example=1)


class DepartmentHeader(BaseModel):
    """ Class DepartmentHeader """
    data: List[DepartmentModel]
