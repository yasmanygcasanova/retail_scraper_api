""" Assortment """
import datetime
from typing import List

from pydantic import BaseModel, Field

from models.vipcommerce.pagination import PaginationModel


class AssortmentModel(BaseModel):
    """ Class AssortmentModel """
    name: str = Field(example="MOLHO PARA SALADA CASTELO BALSAMICO 236ml")
    ean: int = Field(example=7896048282323)
    sku: str = Field(example="AE-018AC")
    product_id: int = Field(example=6316)
    brand: str = Field(example="NA")
    category_id: int = Field(example=61)
    branch_id: int = Field(example=1)
    distribution_center_id: int = Field(example=1)
    price_from: float = Field(example=0.0)
    price_to: float = Field(example=6.39)
    price_offer: float = Field(example=0.0)
    qty_min: int = Field(example=0.0)
    qty_max: int = Field(example=0.0)
    sold_amount: int = Field(example=0)
    available: str = Field(example="S")
    unit_label: str = Field(example="UN")
    unit_fraction: int = Field(example=0)
    qty_fraction: int = Field(example=0)
    price_fraction: float = Field(example=0.0)
    prioritized_product: str = Field(example="N")
    main_volume: str = Field(example="")
    url: str = Field(example="https://www.supermercadosmais.com.br/produtos/detalhe"
                             "/6316/molho-para-salada-castelo-balsamico-236ml")
    image: str = Field(example="https://s3.amazonaws.com/produtos.vipcommerce.com.br"
                               "/250x250/66a84ce8-c0b9-11e7-a6aa-063e6e4e9f3a.jpg")
    created_at: datetime.date = Field(example="2023-05-01")
    hour: datetime.time = Field(example="10:00:00")


class AssortmentHeader(PaginationModel):
    """ Class AssortmentHeader """
    data: List[AssortmentModel]
