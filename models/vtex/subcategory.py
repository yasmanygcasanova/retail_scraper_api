""" Subcategory """
from typing import List

from pydantic import BaseModel, Field


class SubCategoryModel(BaseModel):
    """ Class SubcategoryModel """
    name: str = Field(example="CARNES BOVINAS")
    department_id: int = Field(example=3)
    category_id: int = Field(example=9)
    subcategory_id: int = Field(example=10)
    url: str = Field(
        example="https://mambodelivery.vtexcommercestable.com.br/acougue/carnes/carnes-bovinas"
    )


class SubCategoryHeader(BaseModel):
    """ Class SubcategoryHeader """
    data: List[SubCategoryModel]
