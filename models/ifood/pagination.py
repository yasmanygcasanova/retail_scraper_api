""" Pagination """
from pydantic import BaseModel, Field


class PaginationModel(BaseModel):
    """ Class PaginationModel """
    records_per_page: int = Field(example=50)
    items: int = Field(example=500)
    pages: int = Field(example=1)
    data: list
