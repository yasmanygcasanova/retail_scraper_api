""" Store """
from typing import List, Optional

from pydantic import BaseModel, Field


class MarketModel(BaseModel):
    """ Class MarketModel """
    name: str = Field(example="BIG INDIANOPOLIS")
    segment: str = Field(example="MERCADO")
    store_type: Optional[str] = Field(example="SCHEDULE")
    store_id: str = Field(example="ada76d64-b645-4c5f-af08-be98e5b68f10")
    store_slug: str = Field(example="big-indianopolis-mirandopolis")
    url: str = Field(example="merchant?alias=HOME_MERCADO_BR&channel=IFOOD&id=44be4e0a"
                             "-a110-40f3-b387-9318e36bd607&identifier=ada76d64-b645-4c"
                             "5f-af08-be98e5b68f10&latitude=-23.5608786&longitude=-46.6"
                             "570743&name=Big%20Indian%C3%B3polis&size=40&slug=sao-paulo"
                             "-sp%2Fbig-indianopolis-mirandopolis")
    available: str = Field(example="S")
    distance: float = Field(example=7.69)
    user_rating: float = Field(example=4.35)
    fee: int = Field(example=1998)
    time_min_minutes: Optional[int] = Field(example=68)
    time_max_minutes: Optional[int] = Field(example=78)
    latitude: str = Field(example="-23.5942581")
    longitude: str = Field(example="-46.6107278")
    zip_code: str = Field(example="04268-040")
    region: Optional[str] = Field(example="sao-paulo-sp")
    alias: str = Field(example="HOME_MERCADO_BR")


class MarketHeader(BaseModel):
    """ Class MarketHeader """
    data: List[MarketModel]
