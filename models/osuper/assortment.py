""" Assortment """
import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class AssortmentModel(BaseModel):
    """ Class AssortmentModel """
    name: str = Field(example="SPRITE SEM ACUCAR 2L")
    ean: int = Field(example=7894900061512)
    sku: str = Field(example="2238474")
    store_id: int = Field(example=253)
    category_id: int = Field(example=571970)
    search_term: str = Field(example="Bebidas > Refrigerantes")
    brand: str = Field(example="COCA COLA")
    available: str = Field(example="S")
    sale_unit: Optional[str] = Field(example="UN")
    qty_sale: Optional[int] = Field(example=0)
    price_from: float = Field(example=0)
    price_to: float = Field(example=8.99)
    discount: int = Field(example=0)
    in_stock: int = Field(example=200)
    slug: str = Field(example="sprite-sem-acucar-2l")
    image: Optional[str] = Field(
        example="https://d21wiczbqxib04.cloudfront.net/8zLlTbupkj8Yw9qWhu5r6rANMxQ=/"
        "fit-in/210x210/filters:fill(FFFFFF):"
        "background_color(white)/https://produtos-osuper.s3.amazonaws.com/5311.jpg"
    )
    created_at: datetime.date = Field(example="2023-05-01")
    hour: datetime.time = Field(example="10:00:00")


class AssortmentHeader(BaseModel):
    """ Class AssortmentHeader """
    data: List[AssortmentModel]
