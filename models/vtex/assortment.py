""" Assortment """
import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from models.vtex.pagination import PaginationModel


class AssortmentModel(BaseModel):
    """ Class AssortmentModel """
    name: str = Field(example="ACUCAR REFINADO UNIAO 1KG")
    product_title: str = Field(example="ACUCAR REFINADO UNIAO 1KG | MAMBO SUPERMERCADO SAO PAULO")
    ean: int = Field(example=7891910000197)
    sku: str = Field(example="1158")
    product_ref: str = Field(example="141299")
    department_id: int = Field(example=731)
    category_id: int = Field(example=0)
    brand_id: int = Field(example=20928)
    measurement_unit: Optional[str] = Field(example="un")
    unit_multiplier: float = Field(example=1.0)
    is_kit: Optional[str] = Field(example="N")
    seller_id: str = Field(example="1")
    seller_name: str = Field(example="SUPERMERCADOS MAMBO - BR")
    seller_default: str = Field(example="S")
    seller_type: str = Field(example="LP")
    available_quantity: Optional[int] = Field(example=1317)
    available: str = Field(example="S")
    price_from: float = Field(example=5.09)
    price_to: float = Field(example=5.09)
    price_pix: float = Field(example=5.09)
    price_without_discount: float = Field(example=5.09)
    discount: int = Field(example=0)
    installments_amount: int = Field(example=1)
    installments_value: float = Field(example=5.09)
    interest_rate: str = Field(example="sem juros")
    installments_total_value: float = Field(example=5.09)
    reward_value: float = Field(example=0)
    tax: float = Field(example=0)
    url: str = Field(example="https://www.mambo.com.br/acucar-refinado-uniao-1kg/p")
    image: str = Field(example="https://www.mambo.com.br/arquivos/ids/157385/acucar-"
                               "refinado-uniao-1kg.jpg?v=637883104663670000")
    created_at: datetime.date = Field(example="2023-05-01")
    hour: datetime.time = Field(example="10:00:00")


class AssortmentHeader(PaginationModel):
    """ Class AssortmentHeader """
    data: List[AssortmentModel]
