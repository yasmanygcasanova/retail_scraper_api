import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class AssortmentModel(BaseModel):
    """ Model representing an individual item in the assortment. """
    
    name: str = Field(..., example="Powerade Mountain Berry Blast Sports Drink (28 fl oz)")
    description: str = Field(..., example="Refreshing sports drink with a berry flavor")
    product_id: str = Field(..., example="63395f84-0103-40d3-9065-ffb8ff7aba66")
    category: str = Field(..., example="Beverages")
    store_id: str = Field(..., example="a6961a93-7682-40a0-8e05-ce4bb8bfbfe4")
    
    # Availability indicators
    available: str = Field(..., example="S")  # "S" for available, "N" for not available
    has_customizations: str = Field(..., example="N")  # "S" if the product has customizations, "N" if not
    
    # Pricing and discount info
    price_from: float = Field(..., example=2.99)
    price_to: float = Field(..., example=1.99)  # Discounted price
    discount: Optional[float] = Field(None, example=1.00)  # If there is a discount (optional)

    # Rating and endorsement info
    rating: int = Field(..., example=4)  # Rating from 1 to 5
    num_ratings: int = Field(..., example=120)  # Number of ratings
    endorsement: str = Field(..., example="S")  # "S" if endorsed, "N" if not
    
    # Image and timestamps
    image: str = Field(..., example="https://example.com/image.jpg")
    created_at: datetime.date = Field(..., example="2024-01-01")
    hour: datetime.time = Field(..., example="10:00:00")


class AssortmentHeader(BaseModel):
    """ Model representing the header for assortment data, containing a list of items. """
    data: List[AssortmentModel]  # A list of AssortmentModel instances representing the items
