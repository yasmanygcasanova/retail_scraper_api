""" Assortment """
import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from models.ifood.pagination import PaginationModel


class AssortmentModel(BaseModel):
    """ Class AssortmentModel """
    name: str = Field(example="ACUCAR REFINADO DA BARRA 1KG")
    title: str = Field(example="ACUCAR REFINADO DA BARRA 1KG")
    ean: int = Field(example=7896032501010)
    sku: str = Field(example="000000000000115681-PT")
    product_id: int = Field(example=41603)
    brand: str = Field(example="DA BARRA | NULL")
    category_id: int = Field(example=126)
    search_term: str = Field(example="acucar-e-adocantes")
    available: str = Field(example="S")
    delivery_available: str = Field(example="S")
    stock_qty: int = Field(example=1000)
    rating: float = Field(example=0.0)
    price_from: float = Field(example=0.0)
    price_to: float = Field(example=3.85)
    price_wholesale: float = Field(example=3.79)
    min_qty_wholesale: int = Field(example=5)
    image: Optional[str] = Field(
        example="https://d3gdr9n5lqb5z7.cloudfront.net/fotos/115681.jpg"
    )
    url: str = Field(
        example="http://tendaatacado.com.br/api/public/store/product/Acucar-Refinado-da-Barra-1Kg"
    )
    created_at: datetime.date = Field(example="2023-05-01")
    hour: datetime.time = Field(example="10:00:00")


class AssortmentHeader(PaginationModel):
    """ Class AssortmentHeader """
    data: List[AssortmentModel]
