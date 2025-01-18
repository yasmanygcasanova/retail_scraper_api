""" Store Info """
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class StoreInfoModel(BaseModel):
    """ Class StoreInfoModel """
    name: str = Field(example="Dairy Queen (4040 SW 67th Ave)")
    store_id: str = Field(example="a6961a93-7682-40a0-8e05-ce4bb8bfbfe4")
    slug: str = Field(example="dairy-queen-4040-sw-67th-ave")
    rating: Dict[str, Any]
    location: Dict[str, Any]
    hours: Optional[list] = []
    phone: Optional[str] = Field(example="+13056651387")


class StoreInfoHeader(BaseModel):
    """ Class StoreInfoHeader """
    data: StoreInfoModel
