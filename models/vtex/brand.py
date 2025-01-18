""" Brand """
from typing import List

from pydantic import BaseModel, Field


class BrandModel(BaseModel):
    """ Class BrandModel """
    name: str = Field(example="KIBON")
    title: str = Field(example="KIBON")
    brand_id: int = Field(example=3)


class BrandHeader(BaseModel):
    """ Class BrandHeader """
    data: List[BrandModel]
