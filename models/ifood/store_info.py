""" Store Info """
from pydantic import BaseModel, Field


class StoreInfoModel(BaseModel):
    """ Class StoreInfoModel """
    name: str = Field(example="CARREFOUR HIPER - IMIGRANTES")
    company_code: str = Field(example="IFO")
    phone: str = Field(example="30042222")
    main_category: str = Field(example="MERCADO")
    store_id: str = Field(example="ee4559e2-6c68-429c-9dad-89796c13315e")
    store_type: str = Field(example="MARKET")
    cnpj: str = Field(example="45543915002710")
    logo: str = Field(
        example="https://static-images.ifood.com.br/image/upload"
        "/t_thumbnail/logosgde/ee4559e2-6c68-429c-9dad-89796c13315e/202111121523_Hgf2_i.png"
    )
    country: str = Field(example="BR")
    state: str = Field(example="SP")
    city: str = Field(example="SAO PAULO")
    district: str = Field(example="BOSQUE DA SAUDE")
    zip_code: str = Field(example="04150900")
    latitude: str = Field(example="-23.618427")
    longitude: str = Field(example="-46.626664")
    street_name: str = Field(example="AV RIBEIRO LACERDA")
    street_number: str = Field(example="940")
    price_range: str = Field(example="CHEAPEST")
    delivery_fee: float = Field(example=14.49)
    type_delivery_fee: str = Field(example="FIXED")
    takeout_time: int = Field(example=0)
    delivery_time: int = Field(example=132)
    minimum_order_value: int = Field(example=30)
    preparation_time: int = Field(example=45)
    distance: float = Field(example=3.13)
    available: str = Field(example="S")
    user_rating: float = Field(example=4.4)
    user_rating_count: int = Field(example=182)


class StoreInfoHeader(BaseModel):
    """ Class StoreInfoHeader """
    data: StoreInfoModel
