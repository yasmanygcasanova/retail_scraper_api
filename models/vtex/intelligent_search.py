""" Intelligence Search """
from typing import List

from pydantic import BaseModel, Field


class IntelligentSearchModel(BaseModel):
    """ Class IntelligenceSearchModel """
    term: str = Field(example="azeite")
    count: int = Field(example=892)


class IntelligentSearchHeader(BaseModel):
    """ Class IntelligenceSearchHeader """
    data: List[IntelligentSearchModel]
