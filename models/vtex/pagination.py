""" Pagination """
from pydantic import BaseModel, Field


class PaginationModel(BaseModel):
    """ Class PaginationModel """
    records_per_page: int = Field(example=20)
    items: int = Field(example=2500)
    pages: int = Field(example=130)
    offset: int = Field(example=0)
    limit: int = Field(example=20)
    data: list
