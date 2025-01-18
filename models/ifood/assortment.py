""" Assortment """
import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from models.ifood.pagination import PaginationModel


class AssortmentModel(BaseModel):
    """ Class AssortmentModel """
    name: str = Field(example="MILHO PIPOCA YOKI PREMIUM 500g")
    ean: int = Field(example=0)
    sku: str = Field(example="136151086")
    department: str = Field(example="ALIMENTOS BASICOS")
    category: str = Field(example="GRAOS")
    sub_category: str = Field(example="PIPOCA")
    department_id: str = Field(example="f9845b8a-efe4-48a0-a9aa-c45b50eafafe")
    category_id: str = Field(example="fd853361-fe22-4df8-a72a-89772d615e20")
    search_term: str = Field(example="Grãos")
    details: Optional[str] = Field(example="PACOTE 500g")
    availability: str = Field(example="S")
    price_from: float = Field(example=8.19)
    price_to: float = Field(example=6.17)
    discount: Optional[int] = Field(example=25)
    segment_type: str = Field(example="MERCADOS")
    store_id: str = Field(example="ee4559e2-6c68-429c-9dad-89796c13315e")
    latitude: str = Field(example="-23.5942581")
    longitude: str = Field(example="-46.6107278")
    image: Optional[str] = Field(example="")
    url: str = Field(example="")
    created_at: datetime.date = Field(example="2023-05-01")
    hour: datetime.time = Field(example="10:00:00")


class AssortmentHeader(PaginationModel):
    """ Class AssortmentHeader """
    data: List[AssortmentModel]
