""" Pagination """
from pydantic import BaseModel, Field


class PaginationModel(BaseModel):
    """ Class PaginationModel """
    records_per_page: int = Field(example=40)
    items: int = Field(example=16)
    pages: int = Field(example=1)
    data: list
