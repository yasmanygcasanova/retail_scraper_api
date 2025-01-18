""" Distribution Center """
from typing import List

from pydantic import BaseModel, Field


class DistributionCenterModel(BaseModel):
    """ Class DistributionCenterModel """
    name: str = Field(example="SM Mais Supermercados Ltda")
    site_url: str = Field(example="www.maissupermercados.com.br")
    cnpj: str = Field(example="37245601000174")
    distribution_center_id: int = Field(example=1)
    zip_code: str = Field(example="12620000")
    address: str = Field(example="Av. Luiz Arantes Júnior")
    number: str = Field(example="245")
    complement: str = Field(example="")
    neighborhood: str = Field(example="Centro")
    city: str = Field(example="Piquete")
    state: str = Field(example="São Paulo")
    email: str = Field(example="mais.atendimento@sanchesemartins.com")
    phone: str = Field(example="(12)992475154")
    whatsapp: str = Field(example="(12)992475154")
    branch_id: int = Field(example=1)
    search_term: str = Field(example="04268040")


class DistributionCenterHeader(BaseModel):
    """ Class DistributionCenterHeader """
    data: List[DistributionCenterModel]
