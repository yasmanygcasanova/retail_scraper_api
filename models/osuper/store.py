""" Store """
from typing import List

from pydantic import BaseModel, Field


class StoreModel(BaseModel):
    """ Class StoreModel """
    name: str = Field(example="HORTIFRUTI TURMALINA LTDA - 04")
    account_id: int = Field(example=100)
    store_id: int = Field(example=253)
    alias: str = Field(example="ACLIMACAO")
    cnpj: str = Field(example="28.036.840/0001-23")
    address: str = Field(example="AV TURMALINA, 120 - ACLIMACAO, SAO PAULO - SP, 01531-020")
    contacts: list[dict]


class StoreHeader(BaseModel):
    """ Class StoreHeader """
    data: List[StoreModel]
