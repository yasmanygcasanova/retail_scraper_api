""" Postal Code """
from pydantic import BaseModel, Field


class PostalCodeModel(BaseModel):
    """ Class PostalCodeModel """
    zip_code: str = Field(example="04268040")
    address: str = Field(example="RUA VIEIRA ALMEIDA")
    neighborhood: str = Field(example="IPIRANGA")
    complement: str = Field(example="")
    city: str = Field(example="SAO PAULO")
    region: str = Field(example="SP")
    latitude: str = Field(example="-23.5942581")
    longitude: str = Field(example="-46.6107278")


class PostalCodeHeader(BaseModel):
    """ Class PostalCodeHeader """
    data: PostalCodeModel
