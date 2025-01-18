""" Segment """
from typing import List

from pydantic import BaseModel, Field


class SegmentModel(BaseModel):
    """ Class Segment Model """
    name: str = Field(example="MERCADOS")
    segment_type: str = Field(example="GROCERIES")
    alias: str = Field(example="HOME_MERCADO_BR")
    latitude: str = Field(example="-23.5942581")
    longitude: str = Field(example="-46.6107278")


class SegmentHeader(BaseModel):
    """ Class SegmentHeader """
    data: List[SegmentModel]
